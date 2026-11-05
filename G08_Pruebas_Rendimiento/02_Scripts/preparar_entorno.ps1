<#
.SYNOPSIS
    G08: deja lista la base condor_rendimiento y arranca Condor.Api contra ella.

.DESCRIPTION
    1. Comprueba que el contenedor Cas_condor (PostgreSQL 16, puerto 5433) esté corriendo
       (lo crea ..\..\Sistema_Logistico_Condor_final\ejecutar.ps1).
    2. Crea la base condor_rendimiento si no existe (no se usa la base del local ni condor_pruebas).
    3. Detiene CondorApi y lo arranca otra vez con BaseDatos__BaseDatos=condor_rendimiento y el
       tamaño de pool pedido (BaseDatos__MaxConexiones). Al arrancar, la API aplica las migraciones.
    4. Carga el conjunto de datos (03_Datos\preparar_bd_rendimiento.sql), salvo con -SinDatos.
    5. Escribe entorno_actual.json (equipo, versiones y configuración); ejecutar_escenario.ps1 lo
       copia junto a cada resultado.

.EXAMPLE
    .\preparar_entorno.ps1                    # línea base: pool de 20 conexiones (appsettings.json)
    .\preparar_entorno.ps1 -MaxConexiones 60  # otra configuración del pool
#>
[CmdletBinding()]
param(
    [int]$MaxConexiones = 20,
    [int]$PuertoApi = 5080,
    [switch]$SinDatos,
    # Carpeta con CondorApi.exe publicado por ejecutar.ps1 (-Api). Otra carpeta permite probar otra compilación.
    [string]$CarpetaApi = (Join-Path $PSScriptRoot '..\..\Sistema_Logistico_Condor_final\.ejecutar\api')
)
$ErrorActionPreference = 'Stop'
$Contenedor = 'Cas_condor'
$Base = 'condor_rendimiento'
$Datos = Join-Path $PSScriptRoot '..\03_Datos'
$CarpetaApi = (Resolve-Path $CarpetaApi).Path
$UrlApi = "http://localhost:$PuertoApi"

function Paso([string]$t) { Write-Host "==> $t" -ForegroundColor Cyan }
function Sql([string]$base, [string]$consulta) {
    $r = & docker exec $Contenedor psql -U condor_app -d $base -Atc $consulta
    if ($LASTEXITCODE -ne 0) { throw "Falló la consulta en ${base}: $consulta" }
    return $r
}

Paso "PostgreSQL ($Contenedor)"
if ((& docker inspect -f '{{.State.Running}}' $Contenedor 2>$null) -ne 'true') {
    throw "$Contenedor no está corriendo. Ejecute primero Sistema_Logistico_Condor_final\ejecutar.ps1 -Api"
}
if (-not (Sql 'postgres' "SELECT 1 FROM pg_database WHERE datname = '$Base'")) {
    Paso "Creando la base $Base"
    Sql 'postgres' "CREATE DATABASE $Base" | Out-Null
}

Paso "Arrancando Condor.Api contra $Base (MaxConexiones = $MaxConexiones)"
Get-Process CondorApi -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
$env:BaseDatos__Servidor = 'localhost'
$env:BaseDatos__Puerto = '5433'
$env:BaseDatos__BaseDatos = $Base
$env:BaseDatos__Usuario = 'condor_app'
$env:BaseDatos__Clave = 'condor_local'
$env:BaseDatos__MaxConexiones = "$MaxConexiones"
$env:Urls = "http://0.0.0.0:$PuertoApi"
$api = Start-Process -FilePath (Join-Path $CarpetaApi 'CondorApi.exe') -WorkingDirectory $CarpetaApi -WindowStyle Hidden -PassThru
$limite = (Get-Date).AddMinutes(1)
do {
    Start-Sleep -Seconds 2
    try { $salud = Invoke-RestMethod "$UrlApi/api/salud" -TimeoutSec 3 } catch { $salud = $null }
} until (($salud -and $salud.estado -eq 'OK') -or $api.HasExited -or (Get-Date) -gt $limite)
if (-not $salud -or $salud.estado -ne 'OK') { throw 'Condor.Api no respondió OK en /api/salud.' }

if (-not $SinDatos) {
    Paso 'Cargando el conjunto de datos (3 000 productos, 200 clientes, 10 vendedores de carga)'
    Get-Content -Raw -Encoding UTF8 (Join-Path $Datos 'preparar_bd_rendimiento.sql') |
        & docker exec -i $Contenedor psql -q -v ON_ERROR_STOP=1 -U condor_app -d $Base
    if ($LASTEXITCODE -ne 0) { throw 'Falló preparar_bd_rendimiento.sql' }
}

Paso 'Registrando el entorno (entorno_actual.json)'
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$so = Get-CimInstance Win32_OperatingSystem
$eq = Get-CimInstance Win32_ComputerSystem
$red = Get-NetAdapter -Physical -ErrorAction SilentlyContinue | Where-Object Status -eq 'Up' | Select-Object -First 1
$jmeter = Join-Path $PSScriptRoot '..\..\..\8\apache-jmeter-5.6.3'
$entorno = [ordered]@{
    fecha              = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
    equipo             = "$($eq.Manufacturer) $($eq.Model)"
    procesador         = "$($cpu.Name.Trim()) ($($cpu.NumberOfCores) núcleos, $($cpu.NumberOfLogicalProcessors) hilos lógicos)"
    memoria_gb         = [math]::Round($eq.TotalPhysicalMemory / 1GB, 1)
    sistema_operativo  = "$($so.Caption) $($so.Version) (compilación $($so.BuildNumber))"
    red                = 'Bucle local (localhost): JMeter, Condor.Api y PostgreSQL en el mismo equipo; adaptador físico ' +
                         $(if ($red) { "$($red.InterfaceDescription) $($red.LinkSpeed)" } else { 'no usado' })
    docker             = (& docker version --format '{{.Server.Version}}')
    docker_recursos    = (& docker info --format '{{.NCPU}} CPU, {{.MemTotal}} bytes')
    postgresql         = (Sql $Base 'SELECT version()')
    base_datos         = $Base
    producto           = 'Sistema Logístico Cóndor; /api/salud informa ' + $salud.version + ' (1.1.1 informaba 1.1.0: el .csproj no se había actualizado; corregido en 1.1.2)'
    svn                = ((& svn info --show-item last-changed-revision (Join-Path $PSScriptRoot '..\..\Sistema_Logistico_Condor_final') 2>$null) | Select-Object -First 1)
    api_exe            = (Join-Path $CarpetaApi 'CondorApi.exe')
    api_exe_fecha      = (Get-Item (Join-Path $CarpetaApi 'CondorApi.exe')).LastWriteTime.ToString('yyyy-MM-dd HH:mm')
    api_max_conexiones = $MaxConexiones
    api_url            = $UrlApi
    datos              = [ordered]@{
        productos    = [int](Sql $Base 'SELECT count(*) FROM producto WHERE activo')
        clientes     = [int](Sql $Base 'SELECT count(*) FROM cliente')
        usuarios     = [int](Sql $Base 'SELECT count(*) FROM usuario WHERE activo')
        comprobantes = [int](Sql $Base 'SELECT count(*) FROM comprobante')
    }
    java               = ((& cmd /c 'java -version 2>&1') | Select-Object -First 1)
    jmeter             = '5.6.3 (' + (Resolve-Path $jmeter).Path + ')'
}
$entorno | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $PSScriptRoot 'entorno_actual.json')
$entorno | ConvertTo-Json -Depth 4
Write-Host "Listo. API en $UrlApi sobre $Base." -ForegroundColor Green
