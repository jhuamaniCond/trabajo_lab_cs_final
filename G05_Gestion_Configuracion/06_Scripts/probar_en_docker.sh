#!/usr/bin/env bash
# Ejecuta la suite del producto de una copia de trabajo dentro del SDK de .NET 8
# (esta PC no tiene el SDK instalado) y deja el reporte .trx en la carpeta indicada.
#
#   ./probar_en_docker.sh <carpeta Sistema_Logistico_Condor_final> <carpeta de salida> <nombre> [filtro]
#
# Las pruebas [FactConBD] usan la base condor_pruebas del contenedor Cas_condor (puerto 5433).
set -euo pipefail
ORIGEN=$(cd "$1" && pwd -W)
mkdir -p "$2"
SALIDA=$(cd "$2" && pwd -W)
NOMBRE=$3
FILTRO=${4:-}
ARGS=(--logger "trx;LogFileName=$NOMBRE.trx" --results-directory /out)
[ -n "$FILTRO" ] && ARGS+=(--filter "$FILTRO")
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$ORIGEN:/repo:ro" -v "$SALIDA:/out" -v condor-nuget:/root/.nuget/packages \
  -e CONDOR_TEST_CONN="Host=host.docker.internal;Port=5433;Database=condor_pruebas;Username=condor_app;Password=condor_local" \
  mcr.microsoft.com/dotnet/sdk:8.0 sh -c "cp -r /repo /src && cd /src && find . -name bin -o -name obj -o -name .svn | xargs rm -rf; dotnet test tests/Condor.Pruebas/Condor.Pruebas.csproj $(printf "'%s' " "${ARGS[@]}") 2>&1 | grep -E 'error|Failed |Passed!|Failed!|Total'"
