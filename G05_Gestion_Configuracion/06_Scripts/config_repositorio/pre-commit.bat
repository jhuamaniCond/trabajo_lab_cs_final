@echo off
rem Rechaza confirmaciones con mensaje vacio o de menos de 10 caracteres
rem (politica de configuracion: todo commit explica que cambia y por que).
setlocal
set "REPOS=%~1"
set "TXN=%~2"
set "LOGTMP=%TEMP%\svnlog_%TXN%.txt"
"C:\Program Files\TortoiseSVN\bin\svnlook.exe" log -t "%TXN%" "%REPOS%" > "%LOGTMP%"
for %%A in ("%LOGTMP%") do set TAMANO=%%~zA
del "%LOGTMP%"
if %TAMANO% LSS 12 goto rechazar
exit 0
:rechazar
echo El mensaje de registro debe explicar el cambio: minimo 10 caracteres. 1>&2
exit 1
