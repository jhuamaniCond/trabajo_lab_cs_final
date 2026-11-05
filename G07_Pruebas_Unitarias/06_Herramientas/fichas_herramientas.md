# Fichas de herramientas — G07

Formato pedido por el enunciado: nombre, versión exacta, finalidad, requisitos de instalación, procedencia, licencia, configuración, procedimiento de ejecución y archivos generados.

**Equivalencia con JUnit.** El producto Cóndor está hecho en C# (.NET 8), no en Java; el docente permitió usar la tecnología propia siempre que se cumplan las actividades de los laboratorios. La herramienta equivalente a JUnit es **xUnit** y la equivalente a JaCoCo es **coverlet + ReportGenerator**. Correspondencia: `@Test` → `[Fact]`, prueba parametrizada → `[Theory]` + `[InlineData]`, `assertEquals` / `assertThrows` → `Assert.Equal` / `Assert.Throws<T>`, `@BeforeEach` → constructor de la clase de prueba (xUnit crea una instancia por caso).

## xUnit (marco de pruebas unitarias)

| Campo | Contenido |
|---|---|
| Versión exacta | **xunit 2.9.2**, ejecutor **xunit.runner.visualstudio 2.8.2**, **Microsoft.NET.Test.Sdk 17.11.1** (las mismas que la suite del producto `tests/Condor.Pruebas`) |
| Finalidad | Escribir y ejecutar los 27 casos PU-01 a PU-27 sobre 5 componentes de `Condor.Dominio` |
| Requisitos de instalación | .NET SDK 8.0; los paquetes se descargan de NuGet al restaurar (`dotnet restore`) |
| Procedencia | https://xunit.net · https://www.nuget.org/packages/xunit/2.9.2 |
| Licencia | Apache 2.0 (xUnit) · MIT (Microsoft.NET.Test.Sdk) |
| Configuración | `01_Suite/Condor.PruebasUnitarias/Condor.PruebasUnitarias.csproj`. Solo se usa la API de xUnit 2 (`[Fact]`, `[Theory]`, `[InlineData]`, `[Trait]`, `Assert`); no se mezcla con xUnit v3, NUnit ni MSTest. Ninguna prueba captura `Exception` ni la excepción de aserción: el fallo llega al ejecutor. La propiedad `ProductoVersion` (1.1.1 o 1.0.0) elige el código bajo prueba |
| Ejecución | `.\01_Suite\ejecutar_suite.ps1` o `dotnet test 01_Suite/Condor.PruebasUnitarias` |
| Archivos generados | `*.trx` (resultado por caso, formato VSTest) y `*.html` (logger html) en `03_Reportes/`, `04_Defecto_Controlado/` y `05_Regresion/` |

## Dobles de prueba (escritos a mano)

| Campo | Contenido |
|---|---|
| Versión exacta | Código propio, `01_Suite/Condor.PruebasUnitarias/CC01/DoblesAutenticacion.cs` y `Dobles/Datos.cs` |
| Finalidad | Aislar `ServicioAutenticacion` de PostgreSQL y del reloj del sistema: `RepositorioUsuariosFalso` (falso + espía de `IUsuarioRepositorio`) y `RelojFalso` (reemplaza a `DateTimeOffset.UtcNow`); `Datos` arma datos fijos y reproducibles |
| Requisitos | Ninguno adicional |
| Procedencia / licencia | Equipo del proyecto · misma licencia del producto |
| Alternativa evaluada | Moq 4.20 o NSubstitute 5: no se usaron porque `IUsuarioRepositorio` tiene solo 3 métodos y un doble escrito a mano deja visibles los datos que se comprueban (bitácora, intentos, búsquedas) |

## coverlet (recolector de cobertura)

| Campo | Contenido |
|---|---|
| Versión exacta | **coverlet.collector 6.0.2** |
| Finalidad | Medir líneas y ramas ejecutadas de `Condor.Dominio` (equivalente a JaCoCo) |
| Requisitos | Paquete NuGet referenciado por el proyecto de pruebas |
| Procedencia | https://github.com/coverlet-coverage/coverlet |
| Licencia | MIT |
| Configuración | `01_Suite/cobertura.runsettings`: formato Cobertura, `Include=[Condor.Dominio]*`, excluye ensamblados de prueba y código con `[GeneratedCode]`, `[CompilerGenerated]` o `[ExcludeFromCodeCoverage]` |
| Ejecución | `dotnet test ... --collect "XPlat Code Coverage" --settings 01_Suite/cobertura.runsettings` (lo hace `ejecutar_suite.ps1`) |
| Archivos generados | `crudo/*/<guid>/coverage.cobertura.xml` en cada carpeta de reporte |

## ReportGenerator (reporte de cobertura)

| Campo | Contenido |
|---|---|
| Versión exacta | **dotnet-reportgenerator-globaltool 5.3.11** (herramienta local, manifiesto `01_Suite/.config/dotnet-tools.json`) |
| Finalidad | Convertir el XML de coverlet en un reporte HTML navegable por clase y línea, y combinar la cobertura de la suite G07 con la del producto |
| Requisitos | .NET SDK 8.0; `dotnet tool restore` la instala desde NuGet |
| Procedencia | https://reportgenerator.io · https://github.com/danielpalme/ReportGenerator |
| Licencia | Apache 2.0 (la edición gratuita no incluye la cobertura por método, marcada «PRO» en el reporte) |
| Configuración | `-assemblyfilters:+Condor.Dominio -reporttypes:Html;TextSummary;Cobertura` |
| Ejecución | Automática al final de `ejecutar_suite.ps1` |
| Archivos generados | `cobertura/index.html`, una página por clase, `Summary.txt` y `Cobertura.xml` combinado |

## .NET SDK 8 y Docker

| Campo | Contenido |
|---|---|
| Versión exacta | **.NET SDK 8.0.425** (runtime 8.0.31) en la imagen `mcr.microsoft.com/dotnet/sdk:8.0`; **Docker Desktop 29.7.2** |
| Finalidad | Compilar y ejecutar la suite. En las PC del equipo no hay SDK local, así que `ejecutar_suite.ps1` usa el contenedor; si encuentra `dotnet` en el PATH usa el local |
| Requisitos | Windows 10/11 con Docker Desktop (WSL 2), o el SDK de .NET 8 instalado |
| Procedencia | https://dotnet.microsoft.com/download/dotnet/8.0 · https://hub.docker.com/_/microsoft-dotnet-sdk |
| Licencia | .NET: MIT · Docker Desktop: suscripción gratuita para uso educativo y personal |
| Configuración | Volúmenes `condor-nuget` (paquetes NuGet) y `condor-dotnet-tools` (caché de herramientas); la carpeta `Trabajo Grupal` se monta en `/w` |
| Archivos generados | `bin/` y `obj/` (ignorados en SVN) |

## Python, openpyxl, Selenium y Chrome (catálogo y capturas)

| Campo | Contenido |
|---|---|
| Versión exacta | Python **3.12.0**, openpyxl **3.1.5**, Selenium **4.52.0**, Google Chrome **156.0.8078.79** |
| Finalidad | `02_Catalogo/generar_catalogo.py` arma el catálogo leyendo los `.trx` y `Cobertura.xml` (no hay estados escritos a mano); `03_Reportes/capturar_reportes.py` captura los reportes HTML en Chrome sin ventana |
| Requisitos | `pip install openpyxl selenium`; Chrome instalado (Selenium Manager descarga el controlador compatible) |
| Procedencia | https://www.python.org · https://pypi.org/project/openpyxl/ · https://www.selenium.dev |
| Licencia | Python: PSF · openpyxl: MIT · Selenium: Apache 2.0 · Chrome: términos de Google |
| Archivos generados | `02_Catalogo/catalogo_casos_prueba.xlsx`; `capturas/*.png` en `03_Reportes`, `04_Defecto_Controlado` y `05_Regresion` |

## Comparación con las alternativas

| Criterio | xUnit 2.9 (elegido) | NUnit 4 | MSTest 3 | JUnit 5 + JaCoCo (guía) |
|---|---|---|---|---|
| Lenguaje | C# / .NET | C# / .NET | C# / .NET | Java (no aplica al producto) |
| Aislamiento entre casos | Instancia nueva por caso; paralelo por clase | Instancia por fixture (estado compartido si no se cuida) | Instancia por caso | Instancia por caso |
| Parametrización | `[Theory]` + `[InlineData]` | `[TestCase]` | `[DataRow]` | `@ParameterizedTest` |
| Cobertura | coverlet + ReportGenerator | coverlet + ReportGenerator | coverlet o Microsoft.CodeCoverage | JaCoCo |
| Motivo | Ya lo usa la suite del producto (930 pruebas): una sola API y las mismas versiones | Habría dos marcos en la solución | Igual que NUnit | El producto no está en Java |
