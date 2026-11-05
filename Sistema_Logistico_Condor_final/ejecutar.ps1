<#
.SYNOPSIS
    Levanta todo lo necesario y abre el Sistema de Ventas Cóndor en esta PC.

.DESCRIPTION
    1. Arranca Docker Desktop si no está corriendo.
    2. Levanta PostgreSQL 16 en un contenedor propio (Cas_condor) con sus datos
       en el volumen cas_condor_datos, así que lo registrado se conserva entre ejecuciones.
       Usa el puerto 5433 para no chocar con otro PostgreSQL de la PC en el 5432.
    3. Compila y publica la app WPF (CondorVentas.exe) y el backend (CondorApi.exe).
       Si la PC tiene el SDK de .NET 8 lo usa; si no, compila dentro de Docker
       (mcr.microsoft.com/dotnet/sdk:8.0).
    4. La primera vez que se crea la base, carga el catálogo de muestra
       (db/datos/lista_precios.csv, T-19) y los datos de demostración: clientes,
       proveedores, ventas, proformas, compras y guías (herramientas/Condor.DatosDemo).
    5. Arranca el backend Condor.Api en http://localhost:5080 (CC-01): aplica las
       migraciones y es el único que se conecta a PostgreSQL.
    6. Escribe condor.json apuntando a la API y abre CondorVentas.exe, que pide
       usuario y contraseña (encargado / Encargado2026!, vendedor1 / Vendedor2026!).

.EXAMPLE
    .\ejecutar.ps1                 # compila, arranca la API y abre la aplicación
    .\ejecutar.ps1 -SinCompilar    # usa la última versión compilada
    .\ejecutar.ps1 -Api            # solo arranca el backend (para JMeter o para otra PC)
    .\ejecutar.ps1 -DatosDemo      # vuelve a cargar los datos de demostración (agrega otro lote)
    .\ejecutar.ps1 -CargarCatalogo # vuelve a cargar la lista de precios (omite los ya existentes)
    .\ejecutar.ps1 -Detener        # detiene la API y el contenedor de PostgreSQL
    .\ejecutar.ps1 -BorrarDatos    # además borra la base de datos

    Si PowerShell no deja ejecutar scripts:
    powershell -ExecutionPolicy Bypass -File .\ejecutar.ps1
#>
[CmdletBinding()]
param(
    # Puerto de esta PC donde se publica PostgreSQL (5433: el 5432 puede estar ocupado por otro proyecto).
    [int]$Puerto = 5433,
    # Puerto del backend REST (Condor.Api).
    [int]$PuertoApi = 5080,
    # No recompila: usa lo que ya está en .ejecutar\app y .ejecutar\api.
    [switch]$SinCompilar,
    [switch]$CargarCatalogo,
    [switch]$DatosDemo,
    # Solo arranca el backend REST; no abre la app de escritorio.
    [switch]$Api,
    [switch]$Detener,
    [switch]$BorrarDatos
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$Contenedor = 'Cas_condor'
$Volumen    = 'cas_condor_datos'
$BaseDatos  = 'condor'
$Usuario    = 'condor_app'
$Clave      = 'condor_local'          # Solo para desarrollo en esta PC.
$Salida     = Join-Path $PSScriptRoot '.ejecutar\app'
$SalidaApi  = Join-Path $PSScriptRoot '.ejecutar\api'
$Exe        = Join-Path $Salida 'CondorVentas.exe'
$ExeApi     = Join-Path $SalidaApi 'CondorApi.exe'
$UrlApi     = "http://localhost:$PuertoApi"
$HayDotnet  = [bool](Get-Command dotnet -ErrorAction SilentlyContinue)

function Paso([string]$texto) { Write-Host "==> $texto" -ForegroundColor Cyan }

function Invoke-Docker {
    # Ejecuta docker y falla si devuelve error (docker no lanza excepciones).
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Falló: docker $($args -join ' ')" }
}

# Copia el código a /tmp del contenedor para no dejar obj/ de Linux en el
# repositorio; los paquetes NuGet quedan en un volumen para que la próxima vez sea rápida.
$PrepararCopia = "cp -r /repo /tmp/src && cd /tmp/src && rm -rf .git .ejecutar && " +
                 "find . -type d \( -name bin -o -name obj \) -prune -exec rm -rf {} + && "

function Test-Api {
    try { return (Invoke-RestMethod "$UrlApi/api/salud" -TimeoutSec 3 -UseBasicParsing).estado -eq 'OK' } catch { return $false }
}

# Detiene los programas de .ejecutar y espera a que terminen: Windows no deja
# borrar ni reemplazar un .exe hasta que su proceso salió del todo.
function Stop-Programa([string[]]$nombres) {
    $procesos = @(Get-Process $nombres -ErrorAction SilentlyContinue)
    if ($procesos.Count -eq 0) { return }
    $procesos | Stop-Process -Force -ErrorAction SilentlyContinue
    $procesos | Wait-Process -Timeout 15 -ErrorAction SilentlyContinue
}

function Stop-Api { Stop-Programa 'CondorApi' }

# Borra una carpeta de salida; reintenta unos segundos si un archivo sigue en uso.
function Remove-Salida([string]$carpeta) {
    for ($intento = 1; (Test-Path $carpeta) -and $intento -le 10; $intento++) {
        try { Remove-Item -Recurse -Force $carpeta -ErrorAction Stop }
        catch {
            if ($intento -eq 10) { throw "No se pudo borrar $carpeta (¿hay un programa abierto desde ahí?): $($_.Exception.Message)" }
            Start-Sleep -Milliseconds 700
        }
    }
}

# --- 1. Docker ---------------------------------------------------------------
Paso 'Comprobando Docker'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $binDocker = @(
        "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin",
        "$env:ProgramFiles\Docker\Docker\resources\bin"
    ) | Where-Object { Test-Path (Join-Path $_ 'docker.exe') } | Select-Object -First 1
    if (-not $binDocker) { throw 'No se encontró Docker. Instale Docker Desktop: https://www.docker.com/products/docker-desktop/' }
    $env:PATH = "$binDocker;$env:PATH"
}

& docker info *> $null
if ($LASTEXITCODE -ne 0) {
    $escritorio = @(
        "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe",
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $escritorio) { throw 'Docker no está corriendo y no se encontró Docker Desktop.' }
    Paso 'Arrancando Docker Desktop (puede tardar un minuto)'
    Start-Process $escritorio
    $limite = (Get-Date).AddMinutes(3)
    do {
        Start-Sleep -Seconds 3
        & docker info *> $null
    } until ($LASTEXITCODE -eq 0 -or (Get-Date) -gt $limite)
    if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop no terminó de arrancar en 3 minutos.' }
}

# --- Detener / borrar --------------------------------------------------------
if ($Detener -or $BorrarDatos) {
    Stop-Api
    Write-Host 'API (CondorApi) detenida.'
    & docker rm -f $Contenedor *> $null
    Write-Host "PostgreSQL ($Contenedor) detenido."
    if ($BorrarDatos) {
        & docker volume rm $Volumen *> $null
        Write-Host "Base de datos borrada (volumen $Volumen)."
    }
    return
}

# --- 2. PostgreSQL -----------------------------------------------------------
$estado = (& docker ps -a --filter "name=^$Contenedor$" --format '{{.State}}') 2>$null
if (-not $estado) {
    Paso "Creando PostgreSQL 16 ($Contenedor) en el puerto $Puerto"
    $CargarCatalogo = $true
    $DatosDemo = $true
    Invoke-Docker run -d --name $Contenedor --restart unless-stopped `
        -e "POSTGRES_DB=$BaseDatos" -e "POSTGRES_USER=$Usuario" -e "POSTGRES_PASSWORD=$Clave" `
        -p "${Puerto}:5432" -v "${Volumen}:/var/lib/postgresql/data" `
        postgres:16 | Out-Null
} elseif ($estado -ne 'running') {
    Paso "Arrancando PostgreSQL ($Contenedor)"
    Invoke-Docker start $Contenedor | Out-Null
} else {
    Paso "PostgreSQL ($Contenedor) ya está corriendo"
}

$limite = (Get-Date).AddMinutes(1)
do {
    Start-Sleep -Seconds 1
    & docker exec $Contenedor pg_isready -q -h 127.0.0.1 -U $Usuario -d $BaseDatos *> $null
} until ($LASTEXITCODE -eq 0 -or (Get-Date) -gt $limite)
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL no respondió. Revise: docker logs $Contenedor" }

# --- 3. Compilar -------------------------------------------------------------
$proyectoApp = 'src/Condor.Escritorio/Condor.Escritorio.csproj'
$proyectoApi = 'src/Condor.Api/Condor.Api.csproj'
# Un solo .exe por programa (con .NET adentro): el Control inteligente de
# aplicaciones de Windows bloqueaba las DLL sueltas sin firma.
$opcionesApp = @('-c', 'Release', '-r', 'win-x64', '--self-contained', 'true',
                 '-p:PublishSingleFile=true', '-p:IncludeNativeLibrariesForSelfExtract=true',
                 '-p:EnableWindowsTargeting=true', '-v', 'q', '-nologo')
$opcionesApi = @('-c', 'Release', '-r', 'win-x64', '--self-contained', 'true', '-p:PublishSingleFile=true', '-v', 'q', '-nologo')

$compilarApp = -not $Api -and (-not $SinCompilar -or -not (Test-Path $Exe))
$compilarApi = -not $SinCompilar -or -not (Test-Path $ExeApi)
if ($compilarApp -or $compilarApi) {
    # Los .exe no se pueden reemplazar mientras corren: se cierran la API y,
    # si se va a recompilar, la app abierta desde .ejecutar\app.
    Stop-Api
    if ($compilarApp) { Stop-Programa 'CondorVentas' }
    if ($compilarApp) { Remove-Salida $Salida }
    if ($compilarApi) { Remove-Salida $SalidaApi }
    New-Item -ItemType Directory -Force $Salida, $SalidaApi | Out-Null

    if ($HayDotnet) {
        Paso 'Compilando con el SDK de .NET de esta PC'
        if ($compilarApi) { & dotnet publish $proyectoApi @opcionesApi -o $SalidaApi; if ($LASTEXITCODE -ne 0) { throw 'La compilación de la API falló.' } }
        if ($compilarApp) { & dotnet publish $proyectoApp @opcionesApp -o $Salida; if ($LASTEXITCODE -ne 0) { throw 'La compilación de la app falló.' } }
    } else {
        Paso 'Compilando dentro de Docker (esta PC no tiene el SDK de .NET)'
        $pasos = @()
        if ($compilarApi) { $pasos += "dotnet publish $proyectoApi $($opcionesApi -join ' ') -o /salida-api" }
        if ($compilarApp) { $pasos += "dotnet publish $proyectoApp $($opcionesApp -join ' ') -o /salida-app" }
        Invoke-Docker run --rm `
            -v "${PSScriptRoot}:/repo:ro" -v "${Salida}:/salida-app" -v "${SalidaApi}:/salida-api" -v 'condor-nuget:/root/.nuget/packages' `
            mcr.microsoft.com/dotnet/sdk:8.0 sh -c ($PrepararCopia + ($pasos -join ' && '))
    }
}
if (-not (Test-Path $ExeApi)) { throw "No se generó $ExeApi" }
if (-not $Api -and -not (Test-Path $Exe)) { throw "No se generó $Exe" }

# --- 4. Catálogo y datos de demostración -------------------------------------
if ($CargarCatalogo -or $DatosDemo) {
    # Las herramientas de carga se conectan a PostgreSQL con su propio condor.json.
    $carpetaConfig = Join-Path $PSScriptRoot '.ejecutar\carga'
    New-Item -ItemType Directory -Force $carpetaConfig | Out-Null
    # Desde un contenedor, el PostgreSQL de esta PC se alcanza en host.docker.internal.
    [ordered]@{
        Servidor  = $(if ($HayDotnet) { 'localhost' } else { 'host.docker.internal' })
        Puerto    = $Puerto
        BaseDatos = $BaseDatos
        Usuario   = $Usuario
        Clave     = $Clave
    } | ConvertTo-Json | Set-Content -Path (Join-Path $carpetaConfig 'condor.json') -Encoding UTF8

    $herramientas = @()
    if ($CargarCatalogo) { $herramientas += ,@('Cargando el catálogo de muestra (db/datos/lista_precios.csv)', 'herramientas/Condor.CargaCatalogo', 'db/datos/lista_precios.csv') }
    if ($DatosDemo)      { $herramientas += ,@('Cargando los datos de demostración (clientes, proveedores, ventas, proformas, compras y guías)', 'herramientas/Condor.DatosDemo', '') }
    foreach ($h in $herramientas) {
        Paso $h[0]
        if ($HayDotnet) {
            if ($h[2]) { & dotnet run -v q --project $h[1] -- $h[2] --config $carpetaConfig } else { & dotnet run -v q --project $h[1] -- --config $carpetaConfig }
        } else {
            & docker run --rm -v "${PSScriptRoot}:/repo:ro" -v "${carpetaConfig}:/cfg:ro" -v 'condor-nuget:/root/.nuget/packages' `
                mcr.microsoft.com/dotnet/sdk:8.0 sh -c ($PrepararCopia + "dotnet run -v q --project $($h[1]) -- $($h[2]) --config /cfg")
        }
        # Código 2 de la carga del catálogo = algunas filas con error (ya informadas arriba).
        if ($LASTEXITCODE -notin 0, 2) { Write-Warning "No se pudo completar: $($h[0])." }
    }
}

# --- 5. Backend REST (CC-01) -------------------------------------------------
if (Test-Api) {
    Paso "La API ya está corriendo en $UrlApi"
} else {
    Paso "Arrancando la API en $UrlApi"
    $env:BaseDatos__Servidor = 'localhost'
    $env:BaseDatos__Puerto = "$Puerto"
    $env:BaseDatos__BaseDatos = $BaseDatos
    $env:BaseDatos__Usuario = $Usuario
    $env:BaseDatos__Clave = $Clave
    $env:Urls = "http://0.0.0.0:$PuertoApi"
    $procesoApi = Start-Process -FilePath $ExeApi -WorkingDirectory $SalidaApi -WindowStyle Minimized -PassThru
    $limite = (Get-Date).AddMinutes(1)
    do { Start-Sleep -Seconds 2 } until ((Test-Api) -or $procesoApi.HasExited -or (Get-Date) -gt $limite)
    if (-not (Test-Api)) { throw 'La API no respondió en /api/salud. Revise la ventana minimizada de CondorApi.' }
}

if ($Api) {
    Write-Host ''
    Write-Host "API lista: $UrlApi (docs/api.md). Para detenerla: .\ejecutar.ps1 -Detener" -ForegroundColor Green
    Write-Host 'Usuarios de demostración: encargado / Encargado2026!  ·  vendedor1 / Vendedor2026!'
    return
}

# --- 6. Configurar y abrir ---------------------------------------------------
Paso 'Escribiendo condor.json (la app se conecta a la API, no a PostgreSQL)'
[ordered]@{
    # Backend: si la API no está corriendo al abrir la app, la app la arranca (PC principal).
    Api = [ordered]@{ Url = $UrlApi; TiempoEsperaSegundos = 15; Backend = '..\api\CondorApi.exe' }
} | ConvertTo-Json | Set-Content -Path (Join-Path $Salida 'condor.json') -Encoding UTF8

Paso 'Abriendo Sistema de Ventas Cóndor'
$inicio = Get-Date
$app = Start-Process -FilePath $Exe -WorkingDirectory $Salida -PassThru
Start-Sleep -Seconds 4
if ($app.HasExited -and $app.ExitCode -ne 0) {
    $bloqueo = Get-WinEvent -FilterHashtable @{ LogName = 'Microsoft-Windows-CodeIntegrity/Operational'; StartTime = $inicio } -ErrorAction SilentlyContinue |
        Where-Object { $_.Message -like '*CondorVentas*' -or $_.Message -like '*Condor.*' } |
        Select-Object -First 1
    if ($bloqueo) {
        Write-Warning "Windows (Control inteligente de aplicaciones) bloqueó un archivo de la aplicación:`n$($bloqueo.Message)"
    }
    throw "La aplicación se cerró con código $($app.ExitCode)."
}

Write-Host ''
Write-Host "Listo. API: $UrlApi · PostgreSQL ($Contenedor): localhost:$Puerto/$BaseDatos." -ForegroundColor Green
Write-Host 'Usuarios: encargado / Encargado2026!  ·  vendedor1 / Vendedor2026!  ·  vendedor2 / Vendedor2026!'
Write-Host 'La API y PostgreSQL siguen corriendo en segundo plano; para detenerlos: .\ejecutar.ps1 -Detener'
