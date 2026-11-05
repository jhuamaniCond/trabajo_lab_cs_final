# -*- coding: utf-8 -*-
"""
generar_manual_usuario.py
Manual breve de usuario del Sistema Cóndor 1.2.0 (vendedores y encargado).

    python Docs/generar_manual_usuario.py
"""

import os

from comun import (Documento, SALIDA, VERSION, portada, indice, pie_paginado,
                   figura, informar)

C9 = "G09_Gestion_Calidad/04_Reportes/20261104_1919_1.2.0-r32_final-3/capturas/"
CC = "G09_Gestion_Calidad/00_Solicitud_Cambio/capturas/"

FIGURAS = {
    "u_ingresar": (CC + "01_app_ingresar.png", "Ventana Ingresar de la aplicación de escritorio.", 11),
    "u_cred": (C9 + "CP-02_01_credenciales_invalidas.png", "Mensaje ante un usuario inexistente o una contraseña equivocada (portal web).", 14),
    "u_principal": (CC + "02_app_nueva_venta.png", "Pantalla principal Nueva venta: menú de módulos, búsqueda, detalle, cliente, resumen y pie de estado.", 16),
    "u_denegado": (C9 + "CP-03_02_acceso_denegado_por_direccion.png", "Un Vendedor que intenta abrir un módulo del Encargado se queda en Nueva venta con el aviso «Acceso denegado».", 14),
    "u_sugerencias": (C9 + "CP-07_01_sugerencias.png", "Sugerencias de productos desde la tercera letra.", 14),
    "u_boleta": (C9 + "CP-07_02_boleta_emitida.png", "Boleta emitida: número, total y estado ante la SUNAT.", 14),
    "u_reglas": (C9 + "CP-09_02_boleta_mayor_700_sin_dni.png", "Una boleta de más de S/ 700 sin DNI no se emite; la venta no se pierde.", 14),
    "u_clientes": (CC + "05_app_clientes.png", "Módulo Clientes (F3) en la aplicación de escritorio.", 15),
    "u_producto": (C9 + "CP-06_01_producto_registrado.png", "Producto nuevo registrado en el Catálogo (F2).", 14),
    "u_proformas": (CC + "04_app_proformas.png", "Módulo Proformas (F7) con el estado de cada proforma.", 15),
    "u_convertida": (C9 + "CP-10_03_proforma_convertida.png", "Proforma en estado Convertida, con el comprobante en que se convirtió.", 14),
    "u_historial": (CC + "03_app_historial.png", "Historial de ventas (F5) con filtros, total del período y estado ante la SUNAT.", 15),
    "u_compra": (C9 + "CP-13_02_compra_registrada.png", "Compra registrada en el módulo Compras (F4).", 14),
    "u_compra_rep": (C9 + "CP-13_03_compra_repetida.png", "Aviso de compra repetida: el comprobante del proveedor ya está registrado.", 14),
    "u_reporte": (C9 + "CP-12_01_reporte_consolidado.png", "Reporte consolidado de ventas por día, tipo, caja y usuario (portal web, F12).", 15),
    "u_guias": ("Docs/figuras/capturas/app_guias_F8.png", "Módulo Guías de remisión (F8) en la aplicación de escritorio.", 15),
    "u_respaldo": ("Docs/figuras/capturas/app_respaldo_F9.png", "Módulo Respaldo (F9) en un equipo sin la carpeta de respaldo configurada: el sistema indica qué falta y deshabilita Generar respaldo.", 15),
    "u_cerrar": (C9 + "CP-14_01_sesion_cerrada.png", "Tras Cerrar sesión se vuelve a la ventana Ingresar con los campos vacíos.", 12),
}
ORDEN = list(FIGURAS)
PASOS = {
    "u_guias": [
        "Arrancar el sistema con `.\\ejecutar.ps1` desde `Sistema_Logistico_Condor_final` (base, API y app).",
        "Ingresar como `encargado` / `Encargado2026!`.",
        "Pulsar F8 (Guías de remisión) y esperar a que cargue la lista de guías de los datos de demostración.",
        "Capturar solo la ventana de CondorVentas a su tamaño normal (unos 970 × 580 px) y guardar el PNG en la ruta indicada.",
    ],
    "u_respaldo": [
        "Arrancar el sistema con `.\\ejecutar.ps1` e ingresar como `encargado` / `Encargado2026!`.",
        "Pulsar F9 (Respaldo); si se desea, Generar respaldo hacia una carpeta de prueba y esperar el mensaje con el nombre del archivo.",
        "Capturar solo la ventana de CondorVentas a su tamaño normal y guardar el PNG en la ruta indicada.",
    ],
}


def fig(doc, clave):
    figura(doc, clave, FIGURAS, PASOS)


def construir():
    doc = Documento(figuras=ORDEN)
    portada(doc, "MANUAL DE USUARIO", "Vendedores y Encargado general")
    indice(doc)

    doc.titulo(1, "1. Introducción")
    doc.parrafo(
        "Este manual explica cómo usar el Sistema Cóndor %s para vender en el mostrador, cotizar, "
        "registrar compras y consultar la información del negocio. Está dirigido a los **vendedores** "
        "y al **Encargado general** de la ferretería. Para instalar o configurar el sistema, vea el "
        "Manual técnico." % VERSION)
    doc.parrafo(
        "El sistema se usa desde la **aplicación de escritorio** (CondorVentas) en las PC del local o "
        "desde el **portal web del mostrador** en un navegador (`http://<PC principal>:5080/`). Ambos "
        "tienen las mismas pantallas, atajos y reglas; las guías de remisión, la ticketera y la "
        "generación del respaldo solo están en la aplicación de escritorio.")
    doc.parrafo("**Convenciones:** las teclas se escriben en negrita (**F10**, **Esc**); los textos que muestra el sistema van entre comillas latinas («…»).")

    doc.titulo(1, "2. Ingresar y cerrar sesión")
    doc.parrafo("Al abrir el programa aparece la ventana **Ingresar**. Escriba su usuario y su contraseña y pulse **Ingresar** (o **Enter**). El botón solo se habilita cuando ambos campos tienen texto.")
    fig(doc, "u_ingresar")
    doc.tabla([
        ["Usuario de demostración", "Contraseña", "Rol"],
        ["`encargado`", "`Encargado2026!`", "Encargado general (todos los módulos)"],
        ["`vendedor1`, `vendedor2`", "`Vendedor2026!`", "Vendedor"],
    ], anchos_cm=[5.0, 4.0, 7.0])
    doc.vinetas([
        "Si el usuario no existe o la contraseña es incorrecta, el sistema muestra «Usuario o contraseña incorrectos.» (el mismo mensaje en los dos casos, por seguridad).",
        "Después de **5 intentos fallidos seguidos** la cuenta se bloquea **15 minutos**, aunque luego se escriba la contraseña correcta. Espere o pida ayuda al Encargado.",
        "La sesión dura un turno (8 horas). Si vence, el sistema vuelve a pedir el ingreso.",
        "Para terminar, pulse **Cerrar sesión** en el menú: se descarta la venta en curso y se vuelve a Ingresar.",
    ])
    fig(doc, "u_cred")

    doc.titulo(1, "3. La pantalla principal")
    doc.parrafo("Tras ingresar se abre **Nueva venta**. A la izquierda está el menú de módulos; al centro, la búsqueda de productos y el detalle; a la derecha, el cliente y el resumen con el total. El pie muestra su usuario y rol, la PC, el estado de la SUNAT y la conexión con la PC principal.")
    fig(doc, "u_principal")
    doc.tabla([
        ["Tecla", "Acción", "Vendedor", "Encargado"],
        ["**F1** / **Esc**", "Volver a Nueva venta / cancelar la venta en curso", "Sí", "Sí"],
        ["**F2**", "Catálogo de productos", "Sí", "Sí"],
        ["**F3**", "Clientes", "Sí", "Sí"],
        ["**F4**", "Compras a proveedores", "No", "Sí"],
        ["**F5**", "Historial de ventas", "Sí", "Sí"],
        ["**F6**", "Proveedores", "No", "Sí"],
        ["**F7**", "Proformas", "Sí", "Sí"],
        ["**F8**", "Guías de remisión (solo app)", "No", "Sí"],
        ["**F9**", "Respaldo de la base de datos", "No", "Sí"],
        ["**F10**", "Emitir e imprimir el comprobante", "Sí", "Sí"],
        ["**F11**", "Reimprimir el último ticket", "Sí", "Sí"],
        ["**F12**", "Reporte consolidado (portal web)", "No", "Sí"],
        ["**Alt+D**", "Ir al campo DNI o RUC del cliente", "Sí", "Sí"],
        ["**Ctrl+N** / **Alt+L**", "Nuevo producto / nuevo cliente", "Sí", "Sí"],
    ], anchos_cm=[3.4, 8.2, 2.2, 2.2])
    doc.parrafo("El Vendedor no ve los módulos del Encargado. Si pulsa su tecla, se queda en Nueva venta con el aviso «Acceso denegado: el módulo … es solo para el Encargado general».")
    fig(doc, "u_denegado")

    doc.titulo(1, "4. Vender (boleta, factura o nota de venta)")
    doc.numerada([
        "En **Producto**, escriba al menos tres letras del nombre (no importan mayúsculas ni tildes) o pase el producto por el lector de código de barras.",
        "Elija la sugerencia con las flechas y **Enter**; escriba la **Cantidad** y pulse **Enter** para agregarlo al detalle. Repita para cada producto.",
        "Si la venta lleva cliente, pulse **Alt+D**, escriba el DNI (8 dígitos) o el RUC (11 dígitos) y pulse **Enter**. Si no existe, regístrelo con **Alt+L** (Nuevo cliente).",
        "Elija el tipo: **Boleta**, **Con DNI**, **Factura**, **Nota venta** o **Proforma**. El resumen muestra la operación gravada, el IGV (18 %) y el total.",
        "Pulse **F10** (Emitir e imprimir). El sistema muestra «Boleta B001-… emitida · Total … · SUNAT: …», imprime el ticket y deja la pantalla lista para la siguiente venta.",
    ])
    fig(doc, "u_sugerencias")
    fig(doc, "u_boleta")
    doc.parrafo("**Reglas que aplica el sistema** (si no se cumplen, muestra el motivo y la venta no se pierde):")
    doc.vinetas([
        "Una **boleta de más de S/ 700.00** exige el DNI del cliente: elija **Con DNI**.",
        "Una **factura** solo se emite a un cliente con RUC válido, razón social y dirección.",
        "Cada línea admite una cantidad mayor que 0 y hasta 99 999, con tres decimales como máximo; un comprobante tiene hasta 100 líneas.",
        "El precio de cada producto lo fija el catálogo; no se puede cambiar en la venta.",
        "Los números de comprobante son correlativos por serie (B001, F001, NV01, PR01) aunque varias PC emitan a la vez.",
    ])
    fig(doc, "u_reglas")
    doc.titulo(2, "4.1 Ticket y reimpresión")
    doc.parrafo("Si la ticketera falla, el comprobante ya quedó guardado con su número: el sistema muestra el motivo (sin papel, tapa abierta, apagada). Corrija el problema y reimprima con **F11** o desde el Historial (F5); la reimpresión sale marcada como **copia**. Sin ticketera configurada, el ticket se muestra en pantalla.")
    doc.titulo(2, "4.2 Envío a la SUNAT")
    doc.parrafo("Las boletas y facturas se envían solas a la SUNAT después de emitirlas; la venta **no espera** a internet. Si no hay conexión, el comprobante queda **PENDIENTE** y se reenvía automáticamente. El pie avisa en rojo cuando el pendiente más antiguo está por vencer el plazo de 3 días.")
    doc.tabla([
        ["Estado", "Significado", "Qué hacer"],
        ["PENDIENTE", "Aún no se envió (sin internet o SUNAT sin configurar)", "Nada: se reenvía solo"],
        ["ACEPTADO", "La SUNAT lo aceptó (CDR código 0)", "—"],
        ["OBSERVADO", "Aceptado con observaciones", "Corregir el dato en los siguientes comprobantes"],
        ["RECHAZADO", "Sin validez", "Emitir otro comprobante corregido"],
    ], anchos_cm=[3.0, 7.0, 6.0])

    doc.titulo(1, "5. Clientes y catálogo")
    doc.parrafo("**Clientes (F3):** busque por DNI, RUC o nombre. Para registrar uno nuevo use **Nuevo cliente**: el sistema valida que el DNI tenga 8 dígitos y que el RUC empiece con 10, 15, 16, 17 o 20 y tenga su dígito verificador correcto. Puede escribir el documento con puntos, guiones o espacios: se limpian solos.")
    fig(doc, "u_clientes")
    doc.parrafo("**Catálogo (F2):** busque productos y registre nuevos con nombre, precio con IGV, unidad y, opcionalmente, código de barras. No se permiten dos productos con el mismo nombre (sin distinguir mayúsculas ni tildes) ni con el mismo código de barras.")
    fig(doc, "u_producto")

    doc.titulo(1, "6. Proformas (cotizaciones)")
    doc.numerada([
        "Arme la venta como en la sección 4, elija **Proforma** y pulse **F10**. La proforma vale **7 días** contando el de su emisión y no se envía a la SUNAT.",
        "Cuando el cliente vuelva, abra **Proformas (F7)**, búsquela por número o cliente y pulse **Enter** (Convertir en venta). El detalle, los precios cotizados y el cliente pasan a Nueva venta.",
        "Elija el tipo de comprobante y pulse **F10**. La proforma queda en estado **Convertida** con el número del comprobante.",
    ])
    fig(doc, "u_proformas")
    doc.parrafo("Una proforma **vencida** o **ya convertida** no se puede convertir otra vez.")
    fig(doc, "u_convertida")

    doc.titulo(1, "7. Historial de ventas")
    doc.parrafo("**Historial (F5)** lista los comprobantes por período, tipo, cliente o número, con el total del período, el usuario que emitió cada uno y su estado ante la SUNAT. Desde aquí se reimprime un ticket (como copia) y se reenvían los pendientes. La fecha final no puede ser anterior a la inicial.")
    fig(doc, "u_historial")

    doc.titulo(1, "8. Funciones del Encargado general")
    doc.titulo(2, "8.1 Proveedores y compras (F6, F4)")
    doc.numerada([
        "En **Proveedores (F6)** registre al proveedor con su RUC (único), razón social y datos de contacto.",
        "En **Compras (F4)** pulse **Nueva compra** (**Alt+N**), escriba el RUC del proveedor, el tipo, serie y número de su comprobante y la fecha (no futura ni de más de un año).",
        "Agregue los productos con su cantidad y costo unitario y pulse **Registrar compra**. La lista muestra la operación gravada, el IGV y el total.",
    ])
    fig(doc, "u_compra")
    doc.parrafo("El mismo comprobante del proveedor (RUC, tipo, serie y número) no se puede registrar dos veces.")
    fig(doc, "u_compra_rep")
    doc.titulo(2, "8.2 Reporte consolidado de ventas")
    doc.parrafo("En el portal web, **Reporte (F12)** resume las ventas de un período por día, tipo de comprobante, caja y usuario. Las proformas no suman ventas y los rechazados se muestran aparte. El período no puede pasar de 366 días.")
    fig(doc, "u_reporte")
    doc.titulo(2, "8.3 Guías de remisión (F8, solo app)")
    doc.parrafo("Emita la guía desde una factura o a mano: motivo, fecha de traslado (no anterior a hoy), peso bruto, punto de partida y de llegada (ubigeo de 6 dígitos) y los datos del transportista o del vehículo y conductor. La guía se imprime y se envía a la SUNAT.")
    fig(doc, "u_guias")
    doc.titulo(2, "8.4 Respaldo de la base de datos (F9, PC principal)")
    doc.numerada([
        "Conecte el disco externo a la PC principal.",
        "Pulse **Respaldo (F9)** y luego **Generar respaldo**. Al terminar se muestra el nombre del archivo (por ejemplo, `condor_2026-11-17_18-45.backup`).",
        "Quite el disco con «Quitar hardware de forma segura» y guárdelo fuera del local.",
    ])
    doc.parrafo("Si el último respaldo tiene más de 24 horas, el sistema lo avisa al abrir. La restauración la hace el responsable técnico (Manual técnico).")
    fig(doc, "u_respaldo")

    doc.titulo(1, "9. Mensajes frecuentes")
    doc.tabla([
        ["Mensaje", "Causa", "Qué hacer"],
        ["«Usuario o contraseña incorrectos.»", "Usuario o clave mal escritos", "Revise mayúsculas; tras 5 intentos la cuenta se bloquea 15 min"],
        ["«Acceso denegado: el módulo … es solo para el Encargado general»", "El módulo no corresponde a su rol", "Pida al Encargado que lo haga"],
        ["«Las boletas de más de S/ 700.00 deben llevar el DNI del cliente…»", "Boleta grande sin cliente", "Elija Con DNI y busque o registre al cliente"],
        ["«La factura requiere un cliente con RUC…»", "Factura sin RUC válido", "Digite el RUC y pulse Buscar"],
        ["«El RUC no es válido: revise los números…»", "Dígito verificador errado", "Verifique el RUC con el cliente"],
        ["«La fecha final no puede ser anterior a la inicial.»", "Período invertido", "Corrija las fechas"],
        ["Aviso de conexión con «Reintentar»", "La PC principal o la API no responde", "Verifique que la PC principal esté encendida y pulse Reintentar"],
        ["Pie en rojo: pendientes SUNAT por vencer", "Sin internet hace días", "Revise la conexión de la PC con internet o avise al Encargado"],
    ], anchos_cm=[5.6, 4.2, 6.2])

    doc.titulo(1, "10. Cerrar sesión")
    doc.parrafo("Use **Cerrar sesión** del menú al terminar su turno o al dejar la PC. En el portal web, la sesión se elimina del navegador y recargar la página no la reabre.")
    fig(doc, "u_cerrar")

    pie_paginado(doc, "Manual de usuario — Sistema Cóndor %s" % VERSION)
    os.makedirs(SALIDA, exist_ok=True)
    salida = os.path.join(SALIDA, "Manual_Usuario_Condor.docx")
    doc.guardar(salida)
    informar(salida)


if __name__ == "__main__":
    construir()
