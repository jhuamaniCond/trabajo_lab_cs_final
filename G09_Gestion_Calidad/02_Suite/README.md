# Suite Selenium de G09 — portal web Cóndor

Pruebas de aceptación y regresión web del Sistema Cóndor 1.2.0, escritas en Python con `unittest`, igual que los ejercicios del Lab 9 (`comun.py` con `crear_driver()` y capturas). Plan y casos en `../01_Plan/plan_pruebas_aceptacion.md`.

## Archivos

| Archivo | Contenido |
|---|---|
| `config.ini` | URL del portal, navegador, headless, tamaño de ventana, espera y umbrales de RNF-01 y RNF-06. Cada clave se puede cambiar con `CONDOR_<CLAVE>` |
| `comun.py` | `crear_driver()` (Chrome o Edge con Selenium Manager) y `PruebaWeb`, la base de cada caso: navegador nuevo por caso, evidencias, captura automática del fallo y mediciones |
| `datos.py` | Credenciales de demostración y generadores de datos aislados: DNI, RUC con dígito verificador, nombres y series únicos por ejecución |
| `paginas.py` | Page Objects (Ingresar, Principal, Venta, Clientes, Catálogo, Historial, Proformas) con selectores por `id` |
| `test_01_acceso.py` | CP-01, CP-02, CP-03, CP-14 |
| `test_02_registro.py` | CP-04, CP-05, CP-06 |
| `test_03_venta.py` | CP-07, CP-08, CP-09 (PN-01) |
| `test_04_proformas_consultas.py` | CP-10 (PN-02, cambio de estado), CP-11, CP-12 |
| `test_05_abastecimiento.py` | CP-13 (PN-03) |
| `ejecutar_suite.py` | Ejecutor: corre la suite y deja reporte HTML, JUnit XML, JSON, log, entorno y capturas en `../04_Reportes/<fecha>_<etiqueta>/` |
| `ejecutar_suite.ps1` | Lo mismo desde PowerShell; antes comprueba que la API responda |

## Instalación

Requisitos:

- Python 3.12 (se probó con 3.12.0).
- Google Chrome o Microsoft Edge actualizados.
- No hace falta descargar chromedriver ni msedgedriver: **Selenium Manager**, incluido en Selenium 4, ubica o descarga el controlador que corresponde a la versión del navegador.

```powershell
pip install -r requirements.txt        # selenium==4.52.0
```

## Ejecución

1. Arrancar el producto, con la API y el portal en http://localhost:5080/:

   ```powershell
   cd ..\..\Sistema_Logistico_Condor_final
   .\ejecutar.ps1 -Api
   ```

2. Ejecutar la suite:

   ```powershell
   cd ..\G09_Gestion_Calidad\02_Suite
   .\ejecutar_suite.ps1 -Etiqueta 1.2.0-r32_final                  # Chrome, sin ventana (regresión)
   .\ejecutar_suite.ps1 -Etiqueta 1.2.0-r32_edge -Navegador edge   # Edge
   .\ejecutar_suite.ps1 -Etiqueta demo -Ventana                    # mirando el navegador
   python -m unittest test_03_venta -v                             # un archivo, sin reporte
   ```

El comando termina con código **0** si todos los casos pasan y **1** si alguno falla. El fallo no se oculta: `unittest` lo registra como FAIL o ERROR y queda la captura `CP-xx_NN_FALLO.png`.

## Reproducir un fallo controlado

Para comprobar que la suite detecta un defecto, se puede devolver temporalmente el portal a uno de los defectos registrados. Por ejemplo, DEF-04: en `Sistema_Logistico_Condor_final/src/Condor.Api/wwwroot/js/portal.js` se borra la línea `ocultarResultado(); // DEF-04 ...` de `convertirProforma()`. Después:

1. Se copia `wwwroot` a `.ejecutar/api/wwwroot`. La API sirve los archivos desde disco, así que no hace falta recompilar.
2. Se ejecuta `python ejecutar_suite.py --etiqueta fallo_controlado --patron test_04_proformas_consultas.py`.
3. CP-10 falla con «DEF-04: no debe quedar el aviso de la emisión anterior» y deja su captura.
4. Se restaura la línea y se vuelve a ejecutar: el caso pasa.

## Datos

Los casos crean datos nuevos en la base de demostración: clientes «Cliente G09 …», productos «Producto G09 prueba …», proveedores «Distribuidora G09 …», boletas, facturas, proformas y compras. Así se demuestra que los registros persisten. Ver `../03_Datos/datos_prueba.md`.
