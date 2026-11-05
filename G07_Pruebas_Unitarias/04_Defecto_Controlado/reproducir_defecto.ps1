<#
.SYNOPSIS
  Defecto controlado DEF-02 (G07): introduce temporalmente un error en la
  regla CRQ-02 de EmisionComprobante, comprueba que la suite falla, restaura el
  código y comprueba que vuelve a pasar.

.DESCRIPTION
  Regla real (CRQ-02): una boleta cuyo total sea MAYOR que S/ 700.00 exige DNI.
  Defecto inyectado: se cambia ">" por ">=", de modo que una boleta de
  exactamente S/ 700.00 también exigiría DNI (error de valor límite).
  Prueba que debe detectarlo: PU-13.

  Pasos:
    1. Respalda EmisionComprobante.cs y anota su SHA-256.
    2. Aplica el cambio (equivale a DEF-02_boleta_700.patch).
    3. Corre la suite -> reportes en 1_con_defecto\ (se espera FALLO).
    4. Restaura el archivo original (siempre, aunque algo falle) y verifica
       que el SHA-256 coincide con el del paso 1.
    5. Corre la suite -> reportes en 2_restaurado\ (se espera ÉXITO).
#>
$ErrorActionPreference = 'Stop'
$aqui = $PSScriptRoot
$raiz = (Resolve-Path (Join-Path $aqui '..\..')).Path
$archivo = Join-Path $raiz 'Sistema_Logistico_Condor_final\src\Condor.Dominio\Ventas\EmisionComprobante.cs'
$suite = Join-Path $raiz 'G07_Pruebas_Unitarias\01_Suite\ejecutar_suite.ps1'
$correcto = 'if (cliente is null && Total(solicitud.Detalle) > MontoBoletaIdentificada)'
$defecto  = 'if (cliente is null && Total(solicitud.Detalle) >= MontoBoletaIdentificada)'

$original = [IO.File]::ReadAllText($archivo)
$hashAntes = (Get-FileHash $archivo -Algorithm SHA256).Hash
if (-not $original.Contains($correcto)) { throw "No se encontró la regla original en $archivo" }
$respaldo = "$archivo.respaldo_DEF-02"
Copy-Item $archivo $respaldo -Force

$bitacora = @("DEF-02 defecto controlado - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')",
              "Archivo: Sistema_Logistico_Condor_final/src/Condor.Dominio/Ventas/EmisionComprobante.cs",
              "SHA-256 original: $hashAntes",
              "Cambio inyectado: '>' -> '>=' en la regla de la boleta de S/ 700 (CRQ-02)")
try {
    [IO.File]::WriteAllText($archivo, $original.Replace($correcto, $defecto), (New-Object Text.UTF8Encoding $false))
    $bitacora += "SHA-256 con defecto: $((Get-FileHash $archivo -Algorithm SHA256).Hash)"
    & $suite -Nombre DEF-02_con_defecto -Salida 'G07_Pruebas_Unitarias/04_Defecto_Controlado/1_con_defecto'
    $codigoDefecto = $LASTEXITCODE
    $bitacora += "Ejecución 1 (con defecto): código de salida $codigoDefecto (esperado distinto de 0)"
}
finally {
    Copy-Item $respaldo $archivo -Force
    # Copy-Item conserva la fecha antigua del respaldo: sin esto MSBuild cree que
    # Condor.Dominio.dll está al día y reutiliza la DLL compilada CON el defecto.
    (Get-Item $archivo).LastWriteTime = Get-Date
    Remove-Item $respaldo
    $hashDespues = (Get-FileHash $archivo -Algorithm SHA256).Hash
    $bitacora += "Restaurado. SHA-256 tras restaurar: $hashDespues ($(if ($hashDespues -eq $hashAntes) {'IGUAL al original'} else {'DISTINTO: revisar'}))"
}

& $suite -Nombre DEF-02_restaurado -Salida 'G07_Pruebas_Unitarias/04_Defecto_Controlado/2_restaurado'
$codigoRestaurado = $LASTEXITCODE
$bitacora += "Ejecución 2 (restaurado): código de salida $codigoRestaurado (esperado 0)"
$ok = ($codigoDefecto -ne 0) -and ($codigoRestaurado -eq 0) -and ($hashDespues -eq $hashAntes)
$bitacora += "Conclusión: $(if ($ok) {'la suite DETECTÓ el defecto y vuelve a pasar con el código restaurado'} else {'REVISAR: el resultado no es el esperado'})"
$bitacora | Set-Content -Encoding utf8 (Join-Path $aqui 'bitacora_DEF-02.txt')
$bitacora | Write-Host
if ($ok) { exit 0 } else { exit 1 }
