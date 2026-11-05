<#
.SYNOPSIS
    G08: prueba de capacidad (diagnóstico del cuello de botella). Ejecuta el grupo "Capacidad" sin pausas
    con 10, 25, 50 y 100 hilos (2 min cada uno, la API recién arrancada antes de cada nivel).
.EXAMPLE
    .\capacidad.ps1 -Fase 1_antes
    .\capacidad.ps1 -Fase 2_despues -MaxConexiones 20
#>
param([string]$Fase = '1_antes', [int[]]$Niveles = @(10, 25, 50, 100), [int]$MaxConexiones = 20, [string]$CarpetaApi)
foreach ($u in $Niveles) {
    $p = @{ MaxConexiones = $MaxConexiones; SinDatos = $true }
    if ($CarpetaApi) { $p.CarpetaApi = $CarpetaApi }
    & (Join-Path $PSScriptRoot 'preparar_entorno.ps1') @p | Out-Null
    & (Join-Path $PSScriptRoot 'ejecutar_escenario.ps1') -Escenario capacidad -Usuarios $u -Fase $Fase
    Start-Sleep -Seconds 20
}
