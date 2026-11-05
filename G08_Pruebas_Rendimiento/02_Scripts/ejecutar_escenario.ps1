<#
.SYNOPSIS
    G08: ejecuta un escenario de condor_rendimiento.jmx en modo no gráfico, con monitoreo de CPU y memoria.

.DESCRIPTION
    Antes de cada escenario deja la base en el mismo estado (03_Datos\reiniciar_ventas.sql: 0
    comprobantes, series en 0). Durante la prueba registra:
      - monitoreo_windows.csv : typeperf (Monitor de rendimiento de Windows) cada 2 s: CPU total,
        memoria disponible y, por proceso, CPU, memoria privada e hilos de CondorApi.
      - monitoreo_jmeter.csv  : cada 2 s, CPU y memoria del proceso java de JMeter, por PID (typeperf no
        sirve aquí: su comodín java* se resuelve antes de que JMeter arranque).
      - monitoreo_postgres.csv: cada 5 s, docker stats del contenedor Cas_condor (CPU y memoria) y,
        de pg_stat_activity, las conexiones de la API a condor_rendimiento: total, activas y en espera
        de un bloqueo (wait_event_type = 'Lock').
    Salida en 04_Resultados\<Fase>\<escenario>\: resultado.jtl, jmeter.log, dashboard\ (reporte HTML),
    los dos CSV de monitoreo y entorno.json.

.EXAMPLE
    .\ejecutar_escenario.ps1 -Escenario carga -Fase 1_antes
    .\ejecutar_escenario.ps1 -Escenario estres -Fase 2_despues
    .\ejecutar_escenario.ps1 -Escenario humo     # 2 usuarios 30 s, para comprobar el plan
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('carga', 'estres', 'pico', 'estabilidad', 'capacidad', 'humo')][string]$Escenario,
    # Solo para -Escenario capacidad: hilos sin pausas (diagnóstico del cuello de botella).
    [int]$Usuarios = 50,
    [string]$Fase = '1_antes',
    [string]$JMeter = $(if ($env:JMETER_HOME) { Join-Path $env:JMETER_HOME 'bin\jmeter.bat' }
                        else { Join-Path $PSScriptRoot '..\..\..\8\apache-jmeter-5.6.3\bin\jmeter.bat' }),
    [string]$UrlApi = 'http://localhost:5080'
)
$ErrorActionPreference = 'Stop'
$Contenedor = 'Cas_condor'
$Base = 'condor_rendimiento'
$Plan = Join-Path $PSScriptRoot 'condor_rendimiento.jmx'
$Datos = (Resolve-Path (Join-Path $PSScriptRoot '..\03_Datos')).Path
$JMeter = (Resolve-Path $JMeter).Path

# Propiedades -J de cada escenario (los grupos de hilos que no se nombran quedan en 0 hilos).
$escenarios = @{
    carga       = @{ props = @('carga.usuarios=10'); segundos = 330 }
    estres      = @{ props = @('estres.e1=10', 'estres.e2=15', 'estres.e3=25'); segundos = 570 }
    pico        = @{ props = @('pico.base=10', 'pico.rafaga=40'); segundos = 420 }
    estabilidad = @{ props = @('estabilidad.usuarios=10'); segundos = 930 }
    humo        = @{ props = @('carga.usuarios=2', 'carga.rampa=2', 'carga.duracion=30'); segundos = 30 }
    capacidad   = @{ props = @("capacidad.usuarios=$Usuarios", 'pausa.min=0', 'pausa.rango=0'); segundos = 130 }
}
$e = $escenarios[$Escenario]
$carpeta = if ($Escenario -eq 'capacidad') { "capacidad_${Usuarios}u" } else { $Escenario }
$salida = Join-Path $PSScriptRoot "..\04_Resultados\$Fase\$carpeta"
if (Test-Path $salida) { Remove-Item -Recurse -Force $salida }
New-Item -ItemType Directory -Force $salida | Out-Null
$salida = (Resolve-Path $salida).Path

function Paso([string]$t) { Write-Host "==> $t" -ForegroundColor Cyan }

Paso 'Comprobando Condor.Api'
$salud = Invoke-RestMethod "$UrlApi/api/salud" -TimeoutSec 5
if ($salud.estado -ne 'OK') { throw "La API responde $($salud.estado); ejecute preparar_entorno.ps1" }

Paso 'Reiniciando las ventas de condor_rendimiento (mismo estado inicial en cada escenario)'
Get-Content -Raw -Encoding UTF8 (Join-Path $Datos 'reiniciar_ventas.sql') |
    & docker exec -i $Contenedor psql -q -v ON_ERROR_STOP=1 -U condor_app -d $Base
if ($LASTEXITCODE -ne 0) { throw 'Falló reiniciar_ventas.sql' }

$entorno = Join-Path $PSScriptRoot 'entorno_actual.json'
if (Test-Path $entorno) {
    $info = Get-Content -Raw $entorno | ConvertFrom-Json
    $info | Add-Member -Force escenario $Escenario
    $info | Add-Member -Force fase $Fase
    $info | Add-Member -Force propiedades_jmeter ($e.props -join ' ')
    $info | Add-Member -Force inicio (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
    $info | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $salida 'entorno.json')
}

Paso 'Arrancando el monitoreo (typeperf y docker stats + pg_stat_activity)'
$muestras = [int](($e.segundos + 40) / 2)
$contadores = @(
    '\Processor(_Total)\% Processor Time', '\Memory\Available MBytes',
    '\Process(CondorApi)\% Processor Time', '\Process(CondorApi)\Working Set - Private', '\Process(CondorApi)\Thread Count')
$typeperf = Start-Process typeperf -ArgumentList (($contadores | ForEach-Object { "`"$_`"" }) +
    @('-si', '2', '-sc', "$muestras", '-f', 'CSV', '-y', '-o', "`"$salida\monitoreo_windows.csv`"")) -WindowStyle Hidden -PassThru

$monitorPg = Start-Job -ArgumentList $Contenedor, $Base, "$salida\monitoreo_postgres.csv" -ScriptBlock {
    param($contenedor, $base, $archivo)
    'hora,cpu_postgres_pct,memoria_postgres_mib,conexiones_api,activas,esperando_bloqueo' | Set-Content $archivo
    $consulta = "SELECT count(*), count(*) FILTER (WHERE state = 'active'), count(*) FILTER (WHERE wait_event_type = 'Lock') " +
                "FROM pg_stat_activity WHERE datname = '$base' AND application_name LIKE 'Condor%'"
    while ($true) {
        $hora = (Get-Date).ToString('HH:mm:ss')
        $stats = (& docker stats --no-stream --format '{{.CPUPerc}};{{.MemUsage}}' $contenedor) -split ';'
        $cpu = $stats[0].TrimEnd('%')
        $mem = ($stats[1] -split '/')[0].Trim()
        $mib = if ($mem -match '([\d.]+)GiB') { [double]$Matches[1] * 1024 } elseif ($mem -match '([\d.]+)MiB') { [double]$Matches[1] } else { 0 }
        $pg = (& docker exec $contenedor psql -U condor_app -d $base -Atc $consulta) -replace '\|', ','
        "$hora,$cpu,$mib,$pg" | Add-Content $archivo
        Start-Sleep -Seconds 4
    }
}

Paso "JMeter (no GUI): escenario $Escenario, $($e.segundos) s"
$argumentos = @('-n', '-t', $Plan, "-Jdatos=$($Datos -replace '\\', '/')")
$argumentos += $e.props | ForEach-Object { "-J$_" }
$argumentos += @(
    '-Jjmeter.reportgenerator.apdex_satisfied_threshold=500',
    '-Jjmeter.reportgenerator.apdex_tolerated_threshold=2000',
    '-Jjmeter.reportgenerator.overall_granularity=10000',
    '-Jjmeter.save.saveservice.thread_counts=true',
    '-l', "$salida\resultado.jtl", '-j', "$salida\jmeter.log", '-e', '-o', "$salida\dashboard")
# Java escribe avisos en stderr; con 'Stop', PowerShell 5.1 los trataría como error.
$antes = @(Get-Process java -ErrorAction SilentlyContinue | ForEach-Object Id)
$monitorJm = Start-Job -ArgumentList (,$antes), "$salida\monitoreo_jmeter.csv" -ScriptBlock {
    param($previos, $archivo)
    'hora,cpu_jmeter_pct,memoria_jmeter_mb' | Set-Content $archivo
    # jmeter.bat lanza más de un java (el lanzador y la JVM de la prueba): se sigue el de más memoria.
    $previo = @{}
    $t0 = Get-Date
    $vistos = $false
    while ($true) {
        Start-Sleep -Seconds 2
        $procs = @(Get-Process java -ErrorAction SilentlyContinue | Where-Object { $previos -notcontains $_.Id })
        if ($procs.Count -eq 0) { if ($vistos) { break } else { continue } }
        $vistos = $true
        $p = $procs | Sort-Object PrivateMemorySize64 -Descending | Select-Object -First 1
        $t1 = Get-Date
        $cpu1 = $p.TotalProcessorTime.TotalSeconds
        if ($previo.ContainsKey($p.Id)) {
            $pct = 100 * ($cpu1 - $previo[$p.Id]) / ($t1 - $t0).TotalSeconds / [Environment]::ProcessorCount
            '{0},{1},{2}' -f $t1.ToString('HH:mm:ss'), [math]::Round($pct, 2).ToString([cultureinfo]::InvariantCulture), [math]::Round($p.PrivateMemorySize64 / 1MB, 1).ToString([cultureinfo]::InvariantCulture) | Add-Content $archivo
        }
        $previo = @{ $p.Id = $cpu1 }
        $t0 = $t1
    }
}
$ErrorActionPreference = 'Continue'
& $JMeter @argumentos 2>&1 | ForEach-Object { "$_" }
$codigo = $LASTEXITCODE
$ErrorActionPreference = 'Stop'

Paso 'Deteniendo el monitoreo'
Stop-Job $monitorPg, $monitorJm; Remove-Job $monitorPg, $monitorJm
if (-not $typeperf.HasExited) { Start-Sleep -Seconds 6; if (-not $typeperf.HasExited) { $typeperf | Stop-Process -Force } }

$filas = @(Import-Csv "$salida\resultado.jtl")
$errores = @($filas | Where-Object success -ne 'true').Count
Write-Host ("Muestras: {0}  errores: {1}  ({2:N2} %)" -f $filas.Count, $errores, (100 * $errores / [math]::Max(1, $filas.Count))) -ForegroundColor Green
Write-Host "Resultados en $salida"
if ($codigo -ne 0) { throw "JMeter terminó con código $codigo" }
