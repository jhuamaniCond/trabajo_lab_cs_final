<#
.SYNOPSIS
    G08: ejecuta los cuatro escenarios seguidos (carga, estrés, pico y estabilidad) en una fase.
.EXAMPLE
    .\ejecutar_todos.ps1 -Fase 1_antes
#>
param([string]$Fase = '1_antes', [string[]]$Escenarios = @('carga', 'estres', 'pico', 'estabilidad'))
foreach ($e in $Escenarios) {
    & (Join-Path $PSScriptRoot 'ejecutar_escenario.ps1') -Escenario $e -Fase $Fase
    Start-Sleep -Seconds 30   # pausa entre escenarios para que la CPU y la base vuelvan al reposo
}
