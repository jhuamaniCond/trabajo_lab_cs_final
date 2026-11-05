<#
.SYNOPSIS
    Ejecuta la suite Selenium de G09 contra el portal web de Condor.Api.
.EXAMPLE
    .\ejecutar_suite.ps1 -Etiqueta 1.2.0-r32_final              # Chrome, sin ventana
    .\ejecutar_suite.ps1 -Etiqueta 1.2.0-r32_edge -Navegador edge
    .\ejecutar_suite.ps1 -Etiqueta prueba -Ventana -Patron test_01_acceso.py
#>
param(
    [string]$Etiqueta = 'ejecucion',
    [ValidateSet('chrome', 'edge')][string]$Navegador = 'chrome',
    [string]$Url = 'http://localhost:5080/',
    [string]$Patron = 'test_*.py',
    [switch]$Ventana
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
try { $salud = Invoke-RestMethod ($Url.TrimEnd('/') + '/api/salud') -TimeoutSec 5 }
catch { throw "La API no responde en $Url. Arránquela con ..\..\Sistema_Logistico_Condor_final\ejecutar.ps1 -Api" }
Write-Host "Producto $($salud.version) ($($salud.estado)) en $Url" -ForegroundColor Cyan
$env:CONDOR_URL = $Url
$env:CONDOR_NAVEGADOR = $Navegador
$argumentos = @('ejecutar_suite.py', '--etiqueta', $Etiqueta, '--patron', $Patron)
if ($Ventana) { $argumentos += '--ventana' }
python @argumentos
exit $LASTEXITCODE
