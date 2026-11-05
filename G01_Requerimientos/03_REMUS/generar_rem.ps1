<#
=============================================================================
 generar_rem.ps1 -- Generador de documentos REMUS desde datos en JSON
 -----------------------------------------------------------------------
 Un archivo .rem de REMUS es una base de datos Microsoft Jet 4.0 (Access).
 Este script la escribe directamente por OLEDB, sin tocar remus.exe, de modo
 que todo el contenido de la ERS se carga por script y solo queda abrir el
 archivo en REMUS para revisarlo y capturarlo.

 Uso:
   powershell -ExecutionPolicy Bypass -File generar_rem.ps1
   powershell ... -File generar_rem.ps1 -Datos otro.json -Salida otro.rem -Abrir

 Requisitos: Microsoft ACE OLEDB (viene con Office) o Jet 4.0.
=============================================================================
#>
[CmdletBinding()]
param(
    [string] $Datos,
    [string] $Salida,
    [string] $Base,
    [switch] $Abrir
)

$ErrorActionPreference = 'Stop'

# Directorio del script (compatible con distintas formas de invocacion)
$aqui = $PSScriptRoot
if (-not $aqui) { $aqui = Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $aqui) { $aqui = (Get-Location).Path }

if (-not $Datos)  { $Datos  = Join-Path $aqui 'condor_datos.json' }
if (-not $Salida) { $Salida = Join-Path $aqui 'condor.rem' }
if (-not $Base)   { $Base   = Join-Path $aqui 'remus\base\remus_base_empty_spanish.rem' }

# ---------------------------------------------------------------- utilidades
function Get-Proveedor {
    $nombres = (New-Object System.Data.OleDb.OleDbEnumerator).GetElements() |
               Select-Object -ExpandProperty SOURCES_NAME
    foreach ($p in 'Microsoft.ACE.OLEDB.16.0','Microsoft.ACE.OLEDB.12.0','Microsoft.Jet.OLEDB.4.0') {
        if ($nombres -contains $p) { return $p }
    }
    throw "No se encontro un proveedor OLEDB para Access. Instala 'Microsoft Access Database Engine'."
}

# --------------------------------------------------------------- preparacion
if (-not (Test-Path $Datos)) { throw "No existe el archivo de datos: $Datos" }
if (-not (Test-Path $Base))  { throw "No existe la plantilla base: $Base" }

Write-Host "Leyendo datos de $Datos" -ForegroundColor Cyan
$d = Get-Content -Path $Datos -Raw -Encoding UTF8 | ConvertFrom-Json

if (Test-Path $Salida) {
    $bak = "$Salida.bak"
    Copy-Item $Salida $bak -Force
    Write-Host "Copia de seguridad en $bak" -ForegroundColor DarkGray
}
Copy-Item $Base $Salida -Force
Write-Host "Plantilla copiada a $Salida" -ForegroundColor DarkGray

$prov = Get-Proveedor
Write-Host "Proveedor OLEDB: $prov" -ForegroundColor DarkGray
$cn = New-Object System.Data.OleDb.OleDbConnection("Provider=$prov;Data Source=$Salida;")
$cn.Open()

# ------------------------------------------------------ capa de acceso a BD
# oid es un contador GLOBAL compartido por todos los objetos de especificacion
# (secciones, parrafos, objetivos, requisitos, ...). Las tablas de relacion
# (Trace, Step, Action, ...) llevan su propia secuencia independiente.
$script:oid = 0
function Next-Oid { $script:oid++; return $script:oid }

$script:seq = @{}
function Next-Seq([string]$clave) {
    if (-not $script:seq.ContainsKey($clave)) { $script:seq[$clave] = 0 }
    $script:seq[$clave] = [int]$script:seq[$clave] + 1
    return [int]$script:seq[$clave]
}

function Ins([string]$tabla, [hashtable]$campos) {
    $cols = @(); $marks = @(); $vals = @()
    foreach ($k in $campos.Keys) { $cols += "[$k]"; $marks += '?'; $vals += $campos[$k] }
    $cmd = $cn.CreateCommand()
    $cmd.CommandText = "INSERT INTO [$tabla] (" + ($cols -join ',') + ") VALUES (" + ($marks -join ',') + ")"
    foreach ($v in $vals) {
        $p = $cmd.CreateParameter()
        if ($null -eq $v) {
            $p.OleDbType = [System.Data.OleDb.OleDbType]::LongVarWChar; $p.Value = [DBNull]::Value
        } elseif ($v -is [bool]) {
            $p.OleDbType = [System.Data.OleDb.OleDbType]::Boolean; $p.Value = $v
        } elseif ($v -is [DateTime]) {
            $p.OleDbType = [System.Data.OleDb.OleDbType]::Date; $p.Value = $v
        } elseif ($v -is [int] -or $v -is [long] -or $v -is [double]) {
            $p.OleDbType = [System.Data.OleDb.OleDbType]::Integer; $p.Value = [int]$v
        } else {
            $p.OleDbType = [System.Data.OleDb.OleDbType]::LongVarWChar; $p.Value = [string]$v
        }
        [void]$cmd.Parameters.Add($p)
    }
    [void]$cmd.ExecuteNonQuery()
}

# Las tablas de valores de REMUS estan en espanol con tildes ("hay presion" ->
# "hay presión", "anio(s)" -> "año(s)"). Se normaliza para poder escribir el
# JSON sin acentos y que igual case.
function Plano([string]$s) {
    if (-not $s) { return '' }
    $s = $s.Replace([char]0x00F1, 'n').Replace([char]0x00D1, 'N')   # ñ Ñ
    $d = $s.Normalize([Text.NormalizationForm]::FormD)
    $sb = New-Object Text.StringBuilder
    foreach ($c in $d.ToCharArray()) {
        if ([Globalization.CharUnicodeInfo]::GetUnicodeCategory($c) -ne
            [Globalization.UnicodeCategory]::NonSpacingMark) { [void]$sb.Append($c) }
    }
    $r = $sb.ToString().Normalize([Text.NormalizationForm]::FormC).ToLowerInvariant().Trim()
    return $r.Replace('anio', 'ano')   # acepta la grafia sin enie: anio(s) = año(s)
}

# Tablas de valores predefinidos: nombre normalizado -> oid (se leen de la plantilla)
function Read-Valores([string]$tabla) {
    $h = @{}
    $cmd = $cn.CreateCommand(); $cmd.CommandText = "SELECT oid,name FROM [$tabla]"
    $r = $cmd.ExecuteReader()
    while ($r.Read()) { $h[(Plano ([string]$r[1]))] = [int]$r[0] }
    $r.Close()
    return $h
}
$VImportancia = Read-Valores 'ImportanceValue'
$VUrgencia    = Read-Valores 'UrgencyValue'
$VEstado      = Read-Valores 'StatusValue'
$VEstabilidad = Read-Valores 'StabilityValue'
$VTiempo      = Read-Valores 'TimeUnitValue'
$VTerminacion = Read-Valores 'TerminationValue'
$VConflicto   = Read-Valores 'ConflictStatusValue'

function Val($tabla, $nombre, $porDefecto = 'PD') {
    if ([string]::IsNullOrWhiteSpace($nombre)) { $nombre = $porDefecto }
    $k = Plano $nombre
    if ($tabla.ContainsKey($k)) { return $tabla[$k] }
    Write-Warning "Valor '$nombre' no existe en la tabla de valores; se usa PD"
    return $tabla['pd']
}

$fecha = if ($d.documento.fecha) { [DateTime]::Parse($d.documento.fecha) } else { Get-Date }
$vMaj  = if ($d.documento.versionMajor) { [int]$d.documento.versionMajor } else { 1 }
$vMin  = if ($null -ne $d.documento.versionMinor) { [int]$d.documento.versionMinor } else { 0 }

# Campos comunes de todo objeto de especificacion
function Comunes([int]$o, [string]$nombre, $parent, [int]$num, [int]$orden) {
    @{ oid = $o; name = $nombre; versionMajor = $vMaj; versionMinor = $vMin
       versionDate = $fecha; comments = 'Ninguno'; number = $num
       document = 1; parent = $parent; order = $orden }
}

# mapas id-logico -> oid
$MAPA = @{}
function Reg([string]$id, [int]$o) { if ($id) { $MAPA[$id] = $o } }
function Ref([string]$id) {
    if (-not $id) { return $null }
    if (-not $MAPA.ContainsKey($id)) { throw "Referencia desconocida: '$id'" }
    return $MAPA[$id]
}

Write-Host ''
Write-Host 'Generando documento...' -ForegroundColor Cyan

# ------------------------------------------------------------- 1. documentos
# REMUS mantiene cuatro documentos; el 1 es la ERS y es donde va todo.
$docC = Next-Oid   # 1
Ins 'C_RequirementsSpecification' @{ oid=$docC; name=$d.documento.nombre; versionMajor=$vMaj
                                     versionMinor=$vMin; versionDate=$fecha
                                     comments=$d.documento.comentarios }
$docD = Next-Oid   # 2
Ins 'D_RequirementsSpecification' @{ oid=$docD; name='Documento de Análisis del Sistema'
                                     versionMajor=$vMaj; versionMinor=$vMin; versionDate=$fecha; comments='Ninguno' }
$docF = Next-Oid   # 3
Ins 'DefectsSpecification' @{ oid=$docF; name='Registro de Defectos'
                              versionMajor=$vMaj; versionMinor=$vMin; versionDate=$fecha; comments='Ninguno' }
$docH = Next-Oid   # 4
Ins 'ChangeRequestsSpecification' @{ oid=$docH; name='Registro de Peticiones de Cambio'
                                     versionMajor=$vMaj; versionMinor=$vMin; versionDate=$fecha; comments='Ninguno' }

# --------------------------------------------------------------- 2. secciones
$SEC = @{}
function New-Seccion([string]$clave, [string]$nombre, [string]$padre) {
    $o = Next-Oid
    $p = if ($padre) { $SEC[$padre] } else { $null }
    $orden = Next-Seq "sec:$padre"
    $c = Comunes $o $nombre $p (Next-Seq 'Section') $orden
    $c['isOrderedByName'] = $false
    $c['isAppendix']      = $false
    Ins 'Section' $c
    $SEC[$clave] = $o
    return $o
}

New-Seccion 'intro'    'Introducción'                        $null | Out-Null
New-Seccion 'partic'   'Participantes en el proyecto'        $null | Out-Null
New-Seccion 'obj'      'Objetivos del sistema'               $null | Out-Null
New-Seccion 'cat'      'Catálogo de requisitos'              $null | Out-Null
New-Seccion 'irq'      'Requisitos de información'           'cat' | Out-Null
New-Seccion 'crq'      'Reglas de negocio y restricciones'   'cat' | Out-Null
New-Seccion 'act'      'Actores del sistema'                 'cat' | Out-Null
New-Seccion 'uc'       'Requisitos funcionales (casos de uso)' 'cat' | Out-Null
New-Seccion 'nfr'      'Requisitos no funcionales'           'cat' | Out-Null
New-Seccion 'matriz'   'Matrices de rastreabilidad'          $null | Out-Null
New-Seccion 'confl'    'Conflictos detectados'               $null | Out-Null
Write-Host ("  secciones .................. {0}" -f $SEC.Count)

# --------------------------------------------------------------- 3. parrafos
$nPar = 0
foreach ($p in $d.parrafos) {
    $o = Next-Oid
    $c = Comunes $o $p.titulo $SEC[$p.seccion] (Next-Seq 'Paragraph') (Next-Seq "sec:$($p.seccion)")
    $c['text'] = ($p.texto -join "`r`n")
    $c['isGlossaryItem'] = [bool]$p.glosario
    Ins 'Paragraph' $c
    $nPar++
}
Write-Host ("  parrafos ................... {0}" -f $nPar)

# ---------------------------------------------------------- 4. organizaciones
foreach ($org in $d.organizaciones) {
    $o = Next-Oid
    $c = Comunes $o $org.nombre $SEC['partic'] (Next-Seq 'Organization') (Next-Seq 'sec:partic')
    $c['address']   = $org.direccion
    $c['telephone'] = $org.telefono
    $c['fax']       = $org.fax
    Ins 'Organization' $c
    Reg $org.id $o
}
Write-Host ("  organizaciones ............. {0}" -f @($d.organizaciones).Count)

# Portada: preparado para / preparado por
$nRel = 0
if ($d.documento.preparadoPara) {
    Ins 'IsPreparedFor' @{ oid = (Next-Seq 'IsPreparedFor'); document = $docC
                           organization = (Ref $d.documento.preparadoPara) }
    $nRel++
}
if ($d.documento.preparadoPor) {
    Ins 'IsPreparedBy' @{ oid = (Next-Seq 'IsPreparedBy'); document = $docC
                          organization = (Ref $d.documento.preparadoPor) }
    $nRel++
}

# ----------------------------------------------------------- 5. participantes
foreach ($s in $d.participantes) {
    $o = Next-Oid
    $c = Comunes $o $s.nombre $SEC['partic'] (Next-Seq 'Stakeholder') (Next-Seq 'sec:partic')
    $c['role']         = $s.rol
    $c['isCustomer']   = [bool]$s.cliente
    $c['isDeveloper']  = [bool]$s.desarrollador
    $c['isUser']       = [bool]$s.usuario
    $c['organization'] = (Ref $s.organizacion)
    Ins 'Stakeholder' $c
    Reg $s.id $o
}
Write-Host ("  participantes .............. {0}" -f @($d.participantes).Count)

# --------------------------------------------------------------- 6. objetivos
foreach ($ob in $d.objetivos) {
    $o = Next-Oid
    $c = Comunes $o $ob.nombre $SEC['obj'] (Next-Seq 'Objective') (Next-Seq 'sec:obj')
    $c['importance'] = Val $VImportancia $ob.importancia
    $c['urgency']    = Val $VUrgencia    $ob.urgencia
    $c['status']     = Val $VEstado      $ob.estado
    $c['stability']  = Val $VEstabilidad $ob.estabilidad
    $c['description'] = $ob.descripcion
    Ins 'Objective' $c
    Reg $ob.id $o
}
Write-Host ("  objetivos .................. {0}" -f @($d.objetivos).Count)

# ---------------------------------------------------------------- 7. actores
foreach ($a in $d.actores) {
    $o = Next-Oid
    $c = Comunes $o $a.nombre $SEC['act'] (Next-Seq 'Actor') (Next-Seq 'sec:act')
    $c['role'] = $a.rol
    Ins 'Actor' $c
    Reg $a.id $o
}
Write-Host ("  actores .................... {0}" -f @($d.actores).Count)

# --------------------------------------------- 8. requisitos de informacion
foreach ($r in $d.requisitosInformacion) {
    $o = Next-Oid
    $c = Comunes $o $r.nombre $SEC['irq'] (Next-Seq 'InformationRequirement') (Next-Seq 'sec:irq')
    $c['importance']       = Val $VImportancia $r.importancia
    $c['urgency']          = Val $VUrgencia    $r.urgencia
    $c['status']           = Val $VEstado      $r.estado
    $c['stability']        = Val $VEstabilidad $r.estabilidad
    $c['relevantConcept']  = $r.conceptoRelevante
    $c['avgLifeTimeValue'] = [int]$r.vidaMediaValor
    $c['avgLifeTimeTime']  = Val $VTiempo $r.vidaMediaUnidad
    $c['maxLifeTimeValue'] = [int]$r.vidaMaxValor
    $c['maxLifeTimeTime']  = Val $VTiempo $r.vidaMaxUnidad
    $c['avgOcurrences']    = [int]$r.ocurrenciasMedias
    $c['maxOcurrences']    = [int]$r.ocurrenciasMaximas
    Ins 'InformationRequirement' $c
    Reg $r.id $o
    $i = 0
    foreach ($dato in $r.datos) {
        $i++
        Ins 'SpecificData' @{ oid = (Next-Seq 'SpecificData'); owner = $o; order = $i
                              description = $dato; comments = 'Ninguno' }
    }
}
Write-Host ("  requisitos de informacion .. {0}" -f @($d.requisitosInformacion).Count)

# ------------------------------------------------- 9. requisitos de restriccion
foreach ($r in $d.restricciones) {
    $o = Next-Oid
    $c = Comunes $o $r.nombre $SEC['crq'] (Next-Seq 'ConstraintRequirement') (Next-Seq 'sec:crq')
    $c['importance']  = Val $VImportancia $r.importancia
    $c['urgency']     = Val $VUrgencia    $r.urgencia
    $c['status']      = Val $VEstado      $r.estado
    $c['stability']   = Val $VEstabilidad $r.estabilidad
    $c['description'] = $r.descripcion
    Ins 'ConstraintRequirement' $c
    Reg $r.id $o
}
Write-Host ("  restricciones .............. {0}" -f @($d.restricciones).Count)

# ------------------------------------------------------------ 10. casos de uso
$nPasos = 0; $nExc = 0
foreach ($u in $d.casosUso) {
    $o = Next-Oid
    $c = Comunes $o $u.nombre $SEC['uc'] (Next-Seq 'UseCase') (Next-Seq 'sec:uc')
    $c['importance']      = Val $VImportancia $u.importancia
    $c['urgency']         = Val $VUrgencia    $u.urgencia
    $c['status']          = Val $VEstado      $u.estado
    $c['stability']       = Val $VEstabilidad $u.estabilidad
    $c['isAbstract']      = [bool]$u.abstracto
    $c['triggeringEvent'] = $u.evento
    $c['precondition']    = $u.precondicion
    $c['postcondition']   = $u.postcondicion
    # frequency* tiene DEFAULT 0 y clave ajena a TimeUnitValue: hay que darle un oid valido
    $c['frequencyValue']  = [int]$u.frecuenciaValor
    $c['frequencyTime']   = Val $VTiempo $u.frecuenciaUnidad
    Ins 'UseCase' $c
    Reg $u.id $o
}

# Segunda pasada: los pasos 'incluye' pueden apuntar a un caso de uso definido
# mas adelante (UC-07 incluye UC-09 y UC-10), asi que todos deben estar
# registrados antes de crear los pasos.
foreach ($u in $d.casosUso) {
    $o = Ref $u.id

    # Pasos: cada paso apunta a una Action (de actor, del sistema o inclusion)
    $nPaso = 0
    $oidPasos = @{}
    foreach ($p in $u.pasos) {
        $nPaso++
        $oa = Next-Seq 'Action'
        $acc = @{ oid = $oa; description = $p.descripcion
                  isUseCaseAction = $false; isSystemAction = $false; isActorAction = $false
                  useCase = $null; actor = $null
                  performanceValue = 0; performanceTime = (Val $VTiempo 'PD') }
        switch ($p.tipo) {
            'actor'   { $acc['isActorAction']   = $true;  $acc['actor']   = (Ref $p.actor) }
            'sistema' { $acc['isSystemAction']  = $true }
            'incluye' { $acc['isUseCaseAction'] = $true;  $acc['useCase'] = (Ref $p.casoUso) }
            default   { $acc['isSystemAction']  = $true }
        }
        Ins 'Action' $acc

        $op = Next-Seq 'Step'
        Ins 'Step' @{ oid = $op; owner = $o; order = $nPaso
                      isConditional = [bool]$p.condicional
                      condition = $(if ($p.condicion) { $p.condicion } else { 'PD' })
                      action = $oa; comments = 'Ninguno' }
        $oidPasos[$nPaso] = $op
        $nPasos++
    }

    # Excepciones: cuelgan de un paso concreto
    $porPaso = @{}
    foreach ($e in $u.excepciones) {
        $np = [int]$e.paso
        if (-not $oidPasos.ContainsKey($np)) { Write-Warning "$($u.id): excepcion sobre paso inexistente $np"; continue }
        if (-not $porPaso.ContainsKey($np)) { $porPaso[$np] = 0 }
        $porPaso[$np] = [int]$porPaso[$np] + 1

        $oa = Next-Seq 'Action'
        Ins 'Action' @{ oid = $oa; description = $e.accion
                        isUseCaseAction = $false; isSystemAction = $true; isActorAction = $false
                        useCase = $null; actor = $null
                        performanceValue = 0; performanceTime = (Val $VTiempo 'PD') }
        Ins 'StepException' @{ oid = (Next-Seq 'StepException'); step = $oidPasos[$np]
                               order = $porPaso[$np]; condition = $e.condicion
                               termination = (Val $VTerminacion $e.terminacion 'queda sin efecto')
                               action = $oa; comments = 'Ninguno' }
        $nExc++
    }
}
Write-Host ("  casos de uso ............... {0} ({1} pasos, {2} excepciones)" -f @($d.casosUso).Count, $nPasos, $nExc)

# ------------------------------------------------ 11. requisitos no funcionales
foreach ($r in $d.noFuncionales) {
    $o = Next-Oid
    $c = Comunes $o $r.nombre $SEC['nfr'] (Next-Seq 'NonFunctionalRequirement') (Next-Seq 'sec:nfr')
    $c['importance']  = Val $VImportancia $r.importancia
    $c['urgency']     = Val $VUrgencia    $r.urgencia
    $c['status']      = Val $VEstado      $r.estado
    $c['stability']   = Val $VEstabilidad $r.estabilidad
    $c['description'] = $r.descripcion
    Ins 'NonFunctionalRequirement' $c
    Reg $r.id $o
}
Write-Host ("  requisitos no funcionales .. {0}" -f @($d.noFuncionales).Count)

# ------------------------------------------------------------- 12. conflictos
foreach ($k in $d.conflictos) {
    $o = Next-Oid
    $c = Comunes $o $k.nombre $SEC['confl'] (Next-Seq 'Conflict') (Next-Seq 'sec:confl')
    $c['importance']  = Val $VImportancia $k.importancia
    $c['urgency']     = Val $VUrgencia    $k.urgencia
    $c['status']      = Val $VConflicto   $k.estado 'no resuelto'
    $c['description'] = $k.descripcion
    $c['solution']    = $k.solucion
    Ins 'Conflict' $c
    Reg $k.id $o
}
Write-Host ("  conflictos ................. {0}" -f @($d.conflictos).Count)

# ----------------------------------------------------------- 13. matrices
foreach ($m in $d.matrices) {
    $o = Next-Oid
    $c = Comunes $o $m.nombre $SEC['matriz'] (Next-Seq 'TraceabilityMatrix') (Next-Seq 'sec:matriz')
    $c['rows']    = ($m.filas    -join ' ')
    $c['columns'] = ($m.columnas -join ' ')
    Ins 'TraceabilityMatrix' $c
}
Write-Host ("  matrices ................... {0}" -f @($d.matrices).Count)

# ------------------------------------------- 14. trazabilidad y autoria
# Trace: requisito -> objetivo.  IsSourceOf: participante -> objeto.
$nTrace = 0; $nFuente = 0
function Enlazar($coleccion) {
    foreach ($x in $coleccion) {
        foreach ($objId in $x.objetivos) {
            Ins 'Trace' @{ oid = (Next-Seq 'Trace'); isChecked = $true
                           source = (Ref $x.id); target = (Ref $objId) }
            $script:nTrace++
        }
        foreach ($fid in $x.fuentes) {
            Ins 'IsSourceOf' @{ oid = (Next-Seq 'IsSourceOf'); stakeholder = (Ref $fid)
                                specificationObject = (Ref $x.id) }
            $script:nFuente++
        }
    }
}
Enlazar $d.objetivos
Enlazar $d.requisitosInformacion
Enlazar $d.restricciones
Enlazar $d.casosUso
Enlazar $d.noFuncionales
Write-Host ("  trazas ..................... {0}" -f $nTrace)
Write-Host ("  fuentes (participante->req)  {0}" -f $nFuente)

$cn.Close()
$cn.Dispose()
[System.Data.OleDb.OleDbConnection]::ReleaseObjectPool()

Write-Host ''
Write-Host ("LISTO -> {0}" -f (Resolve-Path $Salida)) -ForegroundColor Green
Write-Host ("Objetos de especificacion creados: {0}" -f $script:oid) -ForegroundColor Green
Write-Host ''
Write-Host 'Abrelo en REMUS (Archivo > Abrir) y usa el boton H para generar el HTML.' -ForegroundColor Yellow

if ($Abrir) {
    $exe = Join-Path $aqui 'remus\bin\remus.exe'
    if (Test-Path $exe) { Start-Process -FilePath (Resolve-Path $exe) -ArgumentList (Resolve-Path $Salida) }
    else { Write-Warning "No se encontro remus.exe en $exe" }
}
