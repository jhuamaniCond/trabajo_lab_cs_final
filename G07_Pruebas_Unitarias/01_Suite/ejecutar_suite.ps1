<#
.SYNOPSIS
  Ejecuta la suite de pruebas unitarias de G07 y genera los reportes de
  ejecución (TRX y HTML) y de cobertura (coverlet + ReportGenerator).

.DESCRIPTION
  Usa el SDK de .NET 8 instalado en la PC; si no lo hay (o con -Docker), lo
  ejecuta dentro del contenedor oficial mcr.microsoft.com/dotnet/sdk:8.0.
  No necesita base de datos, salvo -SuiteProducto con -ConexionBD.

.PARAMETER Version
  Código bajo prueba: 1.1.1 (línea base vigente, por defecto) o 1.0.0
  (producto anterior a CC-01, en 05_Regresion\producto_1.0.0).

.PARAMETER Nombre
  Nombre de la ejecución; los reportes quedan en 03_Reportes\<Nombre>
  (o en la carpeta indicada con -Salida).

.PARAMETER SuiteProducto
  Además de la suite G07 corre la suite del producto (tests\Condor.Pruebas)
  y combina la cobertura de ambas sobre Condor.Dominio (indicador de RNF-08).

.EXAMPLE
  .\ejecutar_suite.ps1                                   # suite G07 sobre 1.1.1
  .\ejecutar_suite.ps1 -Version 1.0.0 -Nombre regresion_antes_CC-01
  .\ejecutar_suite.ps1 -SuiteProducto -Nombre cobertura_RNF-08
#>
param(
    [ValidateSet('1.1.1', '1.0.0')] [string] $Version = '1.1.1',
    [string] $Nombre = "ejecucion_v$Version",
    [string] $Salida,
    [switch] $SuiteProducto,
    [string] $ConexionBD,
    [switch] $Docker
)

$ErrorActionPreference = 'Stop'
$Raiz = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path          # carpeta "Trabajo Grupal"
$Suite = 'G07_Pruebas_Unitarias/01_Suite'
if (-not $Salida) { $Salida = "G07_Pruebas_Unitarias/03_Reportes/$Nombre" }
$Salida = $Salida -replace '\\', '/'
$usarDocker = $Docker -or -not (Get-Command dotnet -ErrorAction SilentlyContinue)

function Ruta([string] $relativa) { if ($usarDocker) { "/w/$relativa" } else { Join-Path $Raiz $relativa } }

function Dotnet([string] $carpeta, [string[]] $argumentos) {
    $ErrorActionPreference = 'Continue'   # la salida de error de dotnet no debe cortar el script
    if ($usarDocker) {
        # Volúmenes: paquetes NuGet y caché de herramientas locales (ReportGenerator)
        $docker = @('run', '--rm', '-v', "${Raiz}:/w", '-v', 'condor-nuget:/root/.nuget/packages',
                    '-v', 'condor-dotnet-tools:/root/.dotnet/toolResolverCache', '-w', "/w/$carpeta")
        if ($ConexionBD) { $docker += @('-e', "CONDOR_TEST_CONN=$ConexionBD") }
        & docker @docker 'mcr.microsoft.com/dotnet/sdk:8.0' dotnet @argumentos | Out-Host
    } else {
        if ($ConexionBD) { $env:CONDOR_TEST_CONN = $ConexionBD }
        Push-Location (Join-Path $Raiz $carpeta)
        try { & dotnet @argumentos | Out-Host } finally { Pop-Location }
    }
    return $LASTEXITCODE
}

$crudo = "$Salida/crudo"
if (Test-Path (Join-Path $Raiz $Salida)) { Remove-Item -Recurse -Force (Join-Path $Raiz $Salida) }
Write-Host "== G07 | producto $Version | salida $Salida | $(if ($usarDocker) {'Docker sdk:8.0'} else {'dotnet local'})"

# 1. Suite G07 (casos PU-01 a PU-27)
$codigo = Dotnet "$Suite/Condor.PruebasUnitarias" @(
    'test', '--nologo', "-p:ProductoVersion=$Version",
    '--settings', (Ruta "$Suite/cobertura.runsettings"),
    '--results-directory', (Ruta "$crudo/G07"),
    '--logger', "trx;LogFileName=$Nombre.trx",
    '--logger', "html;LogFileName=$Nombre.html",
    '--logger', 'console;verbosity=normal',
    '--collect', 'XPlat Code Coverage')

# 2. Suite del producto (opcional, para la cobertura de RNF-08)
if ($SuiteProducto) {
    $codigoProducto = Dotnet 'Sistema_Logistico_Condor_final/tests/Condor.Pruebas' @(
        'test', '--nologo',
        '--settings', (Ruta "$Suite/cobertura.runsettings"),
        '--results-directory', (Ruta "$crudo/producto"),
        '--logger', "trx;LogFileName=${Nombre}_suite_producto.trx",
        '--logger', "html;LogFileName=${Nombre}_suite_producto.html",
        '--collect', 'XPlat Code Coverage')
    if ($codigo -eq 0) { $codigo = $codigoProducto }
}

# 3. Reporte de cobertura (ReportGenerator 5.3.11, manifiesto en .config/)
$null = Dotnet $Suite @('tool', 'restore')
$null = Dotnet $Suite @('tool', 'run', 'reportgenerator',
    "-reports:$(Ruta "$crudo")/*/*/coverage.cobertura.xml",
    "-targetdir:$(Ruta "$Salida/cobertura")",
    '-assemblyfilters:+Condor.Dominio',
    '-reporttypes:Html;TextSummary;Cobertura',
    "-title:Condor $Version - $Nombre")

# 4. Reportes a la vista: TRX/HTML de ejecución y resumen de cobertura
Get-ChildItem -Recurse (Join-Path $Raiz $crudo) -Include *.trx, *.html | Copy-Item -Destination (Join-Path $Raiz $Salida)
Get-Content (Join-Path $Raiz "$Salida/cobertura/Summary.txt") -TotalCount 14
Write-Host "== Resultado: $(if ($codigo -eq 0) {'TODAS LAS PRUEBAS PASARON'} else {"HAY PRUEBAS FALLIDAS (código $codigo)"})"
exit $codigo
