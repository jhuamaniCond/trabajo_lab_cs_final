// CC-03: portal web del mostrador. Solo presenta: las reglas (IGV, series,
// validaciones, permisos por rol) las aplica Condor.Api con Condor.Dominio.
"use strict";

const $ = (id) => document.getElementById(id);
const CLAVE_SESION = "condor.sesion";
const ENCARGADO = "ENCARGADO";
const MODULOS = {
  Venta: { titulo: "Nueva venta", seccion: "ModuloVenta", tecla: "F1" },
  Catalogo: { titulo: "Catálogo", seccion: "ModuloCatalogo", tecla: "F2", cargar: () => buscarCatalogo() },
  Clientes: { titulo: "Clientes", seccion: "ModuloClientes", tecla: "F3", cargar: () => buscarClientes() },
  Compras: { titulo: "Compras", seccion: "ModuloCompras", tecla: "F4", encargado: true, cargar: () => buscarCompras() },
  Historial: { titulo: "Historial", seccion: "ModuloHistorial", tecla: "F5", cargar: () => buscarHistorial() },
  Proveedores: { titulo: "Proveedores", seccion: "ModuloProveedores", tecla: "F6", encargado: true, cargar: () => buscarProveedores() },
  Proformas: { titulo: "Proformas", seccion: "ModuloProformas", tecla: "F7", cargar: () => buscarProformas() },
  Guias: { titulo: "Guías", seccion: "ModuloSoloEscritorio", tecla: "F8", encargado: true, cargar: () => soloEscritorio("Guías de remisión", "") },
  Respaldo: { titulo: "Respaldo", seccion: "ModuloRespaldo", tecla: "F9", encargado: true, cargar: () => listarRespaldos() },
  Reporte: { titulo: "Reporte", seccion: "ModuloReporte", tecla: "F12", encargado: true, cargar: () => generarReporte() },
};

let sesion = null;          // { token, usuario, nombre, rol }
let moduloActual = "Venta";
let venta = nuevaVenta();

function nuevaVenta() {
  return { detalle: [], cliente: null, seleccionado: null, sugerencias: [], indice: -1, proforma: null };
}

// ---------------------------------------------------------------- utilidades

const soles = (n) => "S/ " + Number(n || 0).toFixed(2);
const redondear = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const fechaCorta = (d) => d ? new Date(d.length === 10 ? d + "T12:00:00" : d).toLocaleDateString("es-PE", { day: "2-digit", month: "2-digit", year: "numeric" }) : "";
const fechaHora = (d) => new Date(d).toLocaleString("es-PE", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: false });
const hoyIso = () => { const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 10); };
const inicioMesIso = () => hoyIso().slice(0, 8) + "01";

function texto(el, valor) { el.textContent = valor ?? ""; }
function mostrar(el, si) { el.classList.toggle("oculto", !si); }
function error(el, mensaje) { texto(el, mensaje); mostrar(el, !!mensaje); }
function escapar(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

function mensaje(textoMensaje, alerta = false) {
  const el = $("TextoMensaje");
  texto(el, textoMensaje);
  el.classList.toggle("alerta", alerta);
}

class ErrorApi extends Error {
  constructor(estado, titulo, errores) { super(titulo); this.estado = estado; this.errores = errores || []; }
  get detalle() { return this.errores.length ? this.errores.join(" ") : this.message; }
}

async function api(metodo, ruta, cuerpo) {
  const cabeceras = { Accept: "application/json" };
  if (sesion) cabeceras.Authorization = "Bearer " + sesion.token;
  if (cuerpo !== undefined) cabeceras["Content-Type"] = "application/json";
  let respuesta;
  try {
    respuesta = await fetch(ruta, { method: metodo, headers: cabeceras, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });
  } catch {
    conexion(false);
    throw new ErrorApi(0, "Sin conexión con la PC principal: revise la red y reintente.");
  }
  conexion(respuesta.status !== 503);
  const txt = await respuesta.text();
  const datos = txt ? JSON.parse(txt) : null;
  if (respuesta.ok) return datos;
  if (respuesta.status === 401 && sesion && ruta !== "/api/auth/login") {
    cerrarSesion("La sesión venció: ingrese otra vez.");
  }
  if (respuesta.status === 403) throw new ErrorApi(403, "Acceso denegado: esta acción es solo para el Encargado general.");
  throw new ErrorApi(respuesta.status, datos?.title || "No se pudo completar la operación.", datos?.errores);
}

function conexion(ok) {
  $("PuntoConexion").classList.toggle("caida", !ok);
  texto($("TextoConexion"), ok ? "Conectado" : "Sin conexión");
}

// ---------------------------------------------------------------- ingreso

async function ingresar(evento) {
  evento.preventDefault();
  const aviso = $("AvisoError");
  mostrar(aviso, false);
  $("BotonIngresar").disabled = true;
  try {
    const r = await api("POST", "/api/auth/login", { usuario: $("CampoUsuario").value.trim(), clave: $("CampoClave").value });
    sesion = { token: r.token, usuario: r.usuario, nombre: r.nombre, rol: r.rol };
    try { sessionStorage.setItem(CLAVE_SESION, JSON.stringify(sesion)); } catch { /* sin almacenamiento */ }
    abrirPrincipal();
  } catch (e) {
    texto($("TextoError"), e.message);
    mostrar(aviso, true);
    $("CampoClave").value = "";
    $("CampoClave").focus();
  } finally {
    $("BotonIngresar").disabled = false;
  }
}

function abrirPrincipal() {
  mostrar($("PantallaIngresar"), false);
  mostrar($("PantallaPrincipal"), true);
  $("PantallaPrincipal").classList.toggle("encargado", sesion.rol === ENCARGADO);
  texto($("TextoUsuario"), sesion.usuario);
  texto($("TextoRol"), sesion.rol === ENCARGADO ? "Encargado general" : "Vendedor");
  document.title = "Ferretería Cóndor Majes - Nueva venta";
  mensaje(`Bienvenido, ${sesion.nombre}.`);
  irA(moduloDeHash() || "Venta");
}

function cerrarSesion(motivo) {
  sesion = null;
  try { sessionStorage.removeItem(CLAVE_SESION); } catch { /* sin almacenamiento */ }
  cerrarModales();
  cancelarVenta();
  history.replaceState(null, "", location.pathname);
  mostrar($("PantallaPrincipal"), false);
  mostrar($("PantallaIngresar"), true);
  $("CampoUsuario").value = "";
  $("CampoClave").value = "";
  texto($("TextoError"), motivo || "");
  mostrar($("AvisoError"), !!motivo);
  document.title = "Ferretería Cóndor Majes";
  $("CampoUsuario").focus();
}

// ---------------------------------------------------------------- navegación

function moduloDeHash() {
  const nombre = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  return Object.keys(MODULOS).find((m) => m.toLowerCase() === nombre.toLowerCase());
}

function irA(modulo) {
  const def = MODULOS[modulo];
  if (!def || !sesion) return;
  // Misma regla que PermisosModulo de la app: el Vendedor se queda en Nueva venta.
  if (def.encargado && sesion.rol !== ENCARGADO) {
    mensaje(`Acceso denegado: el módulo ${def.titulo} es solo para el Encargado general.`, true);
    modulo = "Venta";
  } else {
    mensaje("");
  }
  moduloActual = modulo;
  const destino = MODULOS[modulo];
  document.querySelectorAll(".modulo").forEach((s) => mostrar(s, s.id === destino.seccion));
  document.querySelectorAll(".menu[data-modulo]").forEach((b) => b.classList.toggle("activo", b.dataset.modulo === modulo));
  const hash = "#/" + modulo.toLowerCase();
  if (location.hash !== hash) history.replaceState(null, "", hash);
  if (destino.cargar) destino.cargar();
  if (modulo === "Venta") $("CampoProducto").focus();
}

function soloEscritorio(titulo, glifo) {
  texto($("TituloSoloEscritorio"), titulo);
  texto($("IconoSoloEscritorio"), glifo);
  texto($("TextoSoloEscritorio"), `${titulo}: use la app de escritorio en la PC principal.`);
}

// ---------------------------------------------------------------- nueva venta

let temporizador = null;
function alEscribirProducto() {
  venta.seleccionado = null;
  clearTimeout(temporizador);
  const t = $("CampoProducto").value.trim();
  if (t.length < 3 || /^\d+$/.test(t)) { cerrarSugerencias(); return; }
  temporizador = setTimeout(async () => {
    try {
      venta.sugerencias = await api("GET", `/api/productos?texto=${encodeURIComponent(t)}&limite=12`);
      venta.indice = venta.sugerencias.length ? 0 : -1;
      pintarSugerencias();
      error($("ErrorVenta"), venta.sugerencias.length ? "" : `No hay productos que coincidan con «${t}».`);
    } catch (e) { error($("ErrorVenta"), e.message); }
  }, 220);
}

function pintarSugerencias() {
  const lista = $("ListaSugerencias");
  lista.innerHTML = venta.sugerencias.map((p, i) =>
    `<li role="option" data-indice="${i}" class="${i === venta.indice ? "elegido" : ""}">` +
    `<span class="miniatura"></span><div><div class="nombre">${escapar(p.nombre)}</div>` +
    `<div class="detalle">${escapar(p.unidad)}   ·   ${soles(p.precio)}</div></div></li>`).join("");
  mostrar(lista, venta.sugerencias.length > 0);
}

function cerrarSugerencias() { venta.sugerencias = []; venta.indice = -1; mostrar($("ListaSugerencias"), false); }

function elegirSugerencia(i) {
  const p = venta.sugerencias[i];
  if (!p) return;
  venta.seleccionado = p;
  $("CampoProducto").value = p.nombre;
  cerrarSugerencias();
  $("CampoCantidad").focus();
  $("CampoCantidad").select();
}

async function teclaProducto(e) {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    if (!venta.sugerencias.length) return;
    e.preventDefault();
    venta.indice = (venta.indice + (e.key === "ArrowDown" ? 1 : -1) + venta.sugerencias.length) % venta.sugerencias.length;
    pintarSugerencias();
  } else if (e.key === "Enter") {
    e.preventDefault();
    const t = $("CampoProducto").value.trim();
    if (venta.sugerencias.length) elegirSugerencia(Math.max(venta.indice, 0));
    else if (/^\d{4,}$/.test(t)) await agregarPorCodigo(t);
    else if (venta.seleccionado) { $("CampoCantidad").focus(); $("CampoCantidad").select(); }
  }
}

async function agregarPorCodigo(codigo) {
  try {
    const p = await api("GET", `/api/productos/codigo/${encodeURIComponent(codigo)}`);
    sumarLinea(p, 1);
    $("CampoProducto").value = "";
  } catch (e) { error($("ErrorVenta"), e.message); }
}

function leerCantidad() {
  const t = $("CampoCantidad").value.trim().replace(",", ".");
  const n = Number(t);
  if (!/^\d+(\.\d{1,3})?$/.test(t) || !(n > 0) || n > 99999) return null;
  return n;
}

function agregar() {
  ocultarResultado();
  if (venta.proforma) { error($("ErrorVenta"), "La venta sale de una proforma: su detalle no se cambia. Cancele la venta para armar otra."); return; }
  if (!venta.seleccionado) { error($("ErrorVenta"), "Elija un producto de la lista antes de agregarlo."); $("CampoProducto").focus(); return; }
  const cantidad = leerCantidad();
  if (cantidad === null) { error($("ErrorVenta"), "La cantidad debe ser mayor que cero, hasta 99 999 y con 3 decimales como máximo."); $("CampoCantidad").focus(); return; }
  sumarLinea(venta.seleccionado, cantidad);
  venta.seleccionado = null;
  $("CampoProducto").value = "";
  $("CampoCantidad").value = "1";
  $("CampoProducto").focus();
}

function sumarLinea(producto, cantidad) {
  error($("ErrorVenta"), "");
  const linea = venta.detalle.find((l) => l.productoId === producto.id);
  if (linea) linea.cantidad = Math.round((linea.cantidad + cantidad) * 1000) / 1000;
  else venta.detalle.push({ productoId: producto.id, descripcion: producto.nombre, unidad: producto.unidad, cantidad, precio: producto.precio });
  pintarVenta();
}

function pintarVenta() {
  const cuerpo = $("TablaDetalle").tBodies[0];
  const bloqueada = !!venta.proforma;
  cuerpo.innerHTML = venta.detalle.map((l, i) =>
    `<tr data-producto="${l.productoId}"><td class="c">${i + 1}</td>` +
    `<td><div class="producto"><span class="miniatura"></span><span class="descripcion">${escapar(l.descripcion)}</span></div></td>` +
    `<td class="c"><input class="cantidad" data-indice="${i}" value="${l.cantidad}" ${bloqueada ? "disabled" : ""} aria-label="Cantidad de ${escapar(l.descripcion)}"></td>` +
    `<td class="c">${escapar(l.unidad)}</td><td class="d">${l.precio.toFixed(2)}</td>` +
    `<td class="d importe">${redondear(l.cantidad * l.precio).toFixed(2)}</td>` +
    `<td class="c">${bloqueada ? "" : `<button class="quitar" data-indice="${i}" title="Quitar de la venta"></button>`}</td></tr>`).join("");
  mostrar($("DetalleVacio"), venta.detalle.length === 0);
  const total = redondear(venta.detalle.reduce((s, l) => s + redondear(l.cantidad * l.precio), 0));
  const op = total ? redondear(total / 1.18) : 0;
  texto($("TextoOpGravada"), soles(op));
  texto($("TextoIgv"), soles(redondear(total - op)));
  texto($("TextoTotal"), soles(total));
  $("BotonEmitir").disabled = venta.detalle.length === 0;
  $("CampoProducto").disabled = bloqueada;
  $("BotonAgregar").disabled = bloqueada;
  $("TipoProforma").disabled = bloqueada;
  mostrar($("AvisoProforma"), bloqueada);
  if (bloqueada) {
    const p = venta.proforma;
    texto($("TextoAvisoProforma"), `Venta desde la proforma ${p.numero} (vigente hasta el ${fechaCorta(p.validaHasta)}): se emite con los precios cotizados.`);
  }
}

function cambiarCantidad(e) {
  const i = Number(e.target.dataset.indice);
  const t = e.target.value.trim().replace(",", ".");
  const n = Number(t);
  if (!/^\d+(\.\d{1,3})?$/.test(t) || !(n > 0) || n > 99999) {
    error($("ErrorVenta"), "La cantidad debe ser mayor que cero, hasta 99 999 y con 3 decimales como máximo.");
    e.target.value = venta.detalle[i].cantidad;
    return;
  }
  error($("ErrorVenta"), "");
  venta.detalle[i].cantidad = n;
  pintarVenta();
}

function quitarLinea(i) { venta.detalle.splice(i, 1); pintarVenta(); }

// ---- Cliente

async function buscarCliente() {
  ocultarResultado();
  const doc = $("CampoDocumento").value.replace(/\s/g, "");
  const campo = $("CampoDocumento");
  campo.classList.remove("invalido");
  error($("ErrorCliente"), "");
  if (!/^(\d{8}|\d{11})$/.test(doc)) {
    campo.classList.add("invalido");
    error($("ErrorCliente"), "El documento debe ser un DNI de 8 dígitos o un RUC de 11.");
    return;
  }
  try {
    elegirCliente(await api("GET", `/api/clientes/${doc}`));
  } catch (e) {
    if (e.estado === 404) {
      venta.cliente = null;
      pintarCliente();
      texto($("TextoSinCliente"), "Ese documento no está registrado. Pulse Nuevo cliente para registrarlo.");
    } else {
      campo.classList.add("invalido");
      error($("ErrorCliente"), e.message);
    }
  }
}

function elegirCliente(cliente) {
  venta.cliente = cliente;
  if (cliente) {
    const tipo = document.querySelector('input[name="tipo"]:checked').value;
    if (cliente.tipoDocumento === "RUC" && tipo !== "FACTURA" && tipo !== "PROFORMA" && tipo !== "NOTA_VENTA") $("TipoFactura").checked = true;
    if (cliente.tipoDocumento === "DNI" && (tipo === "BOLETA" || tipo === "FACTURA")) $("TipoConDni").checked = true;
  }
  pintarCliente();
}

function pintarCliente() {
  const c = venta.cliente;
  mostrar($("ClienteSeleccionado"), !!c);
  mostrar($("SinCliente"), !c);
  texto($("TextoSinCliente"), "Sin cliente: boleta sin DNI.");
  if (c) {
    texto($("ClienteNombre"), c.nombre);
    texto($("ClienteDocumento"), `${c.tipoDocumento} ${c.numeroDocumento}`);
    texto($("ClienteDireccion"), c.direccion || "");
    $("CampoDocumento").value = c.numeroDocumento;
    $("CampoDocumento").classList.remove("invalido");
    error($("ErrorCliente"), "");
  }
}

function quitarCliente() { venta.cliente = null; $("CampoDocumento").value = ""; pintarCliente(); }

// ---- Emitir

async function emitir() {
  if (venta.detalle.length === 0) return;
  ocultarResultado();
  mostrar($("ErrorEmision"), false);
  const tipo = document.querySelector('input[name="tipo"]:checked').value;
  const documentoCliente = venta.cliente?.numeroDocumento || null;
  $("BotonEmitir").disabled = true;
  try {
    const c = venta.proforma
      ? await api("POST", `/api/proformas/${venta.proforma.id}/convertir`, { tipo, documentoCliente })
      : await api("POST", "/api/comprobantes", {
          tipo, documentoCliente,
          detalle: venta.detalle.map((l) => ({ productoId: l.productoId, cantidad: l.cantidad })),
        });
    const sunat = c.estadoSunat === "NO APLICA" ? "" : ` · SUNAT: ${c.estadoSunat}`;
    cancelarVenta();
    texto($("TextoResultadoEmision"), `${c.tipo} ${c.numero} emitida · Total ${soles(c.total)}${sunat}`);
    $("ResultadoEmision").dataset.numero = c.numero;
    mostrar($("ResultadoEmision"), true);
    mensaje(`${c.tipo} ${c.numero} guardada en la base central.`);
  } catch (e) {
    texto($("TextoErrorEmision"), e.detalle);
    mostrar($("ErrorEmision"), true);
    $("BotonEmitir").disabled = venta.detalle.length === 0;
  }
}

function ocultarResultado() { mostrar($("ResultadoEmision"), false); }

function cancelarVenta() {
  venta = nuevaVenta();
  $("CampoProducto").value = "";
  $("CampoCantidad").value = "1";
  $("CampoDocumento").value = "";
  $("CampoDocumento").classList.remove("invalido");
  $("TipoBoleta").checked = true;
  cerrarSugerencias();
  ["ErrorVenta", "ErrorCliente", "ErrorEmision"].forEach((id) => mostrar($(id), false));
  pintarCliente();
  pintarVenta();
}

// ---------------------------------------------------------------- catálogo y clientes

async function buscarCatalogo() {
  try {
    const t = $("CampoBuscarCatalogo").value.trim();
    const productos = await api("GET", `/api/productos?limite=100${t ? "&texto=" + encodeURIComponent(t) : ""}`);
    $("TablaCatalogo").tBodies[0].innerHTML = productos.map((p) =>
      `<tr><td>${escapar(p.codigoBarras || "—")}</td><td>${escapar(p.nombre)}</td><td class="c">${escapar(p.unidad)}</td><td class="d">${soles(p.precio)}</td></tr>`).join("");
    texto($("TextoCatalogo"), `${productos.length} productos${productos.length === 100 ? " (los primeros 100: afine la búsqueda)" : ""}.`);
  } catch (e) { texto($("TextoCatalogo"), e.message); }
}

let clienteElegido = null;
async function buscarClientes() {
  try {
    const t = $("CampoBuscarClientes").value.trim();
    const clientes = await api("GET", `/api/clientes?limite=200${t ? "&texto=" + encodeURIComponent(t) : ""}`);
    clienteElegido = null;
    $("BotonUsarCliente").disabled = true;
    const cuerpo = $("TablaClientes").tBodies[0];
    cuerpo.innerHTML = clientes.map((c, i) =>
      `<tr data-indice="${i}" data-documento="${escapar(c.numeroDocumento)}"><td>${escapar(c.tipoDocumento)} ${escapar(c.numeroDocumento)}</td><td>${escapar(c.nombre)}</td><td>${escapar(c.direccion || "")}</td></tr>`).join("");
    cuerpo._datos = clientes;
    texto($("TextoClientes"), `${clientes.length} clientes.`);
  } catch (e) { texto($("TextoClientes"), e.message); }
}

function usarCliente() {
  if (!clienteElegido) return;
  irA("Venta");
  elegirCliente(clienteElegido);
}

// ---------------------------------------------------------------- historial

function rangoHistorial(desde, hasta) { $("FiltroDesde").value = desde; $("FiltroHasta").value = hasta; buscarHistorial(); }

async function buscarHistorial() {
  error($("ErrorHistorial"), "");
  if (!$("FiltroDesde").value && !$("FiltroHasta").value && !$("FiltroDesde").dataset.todo) {
    $("FiltroDesde").value = $("FiltroHasta").value = hoyIso();
  }
  const p = new URLSearchParams({ limite: "200" });
  if ($("FiltroDesde").value) p.set("desde", $("FiltroDesde").value);
  if ($("FiltroHasta").value) p.set("hasta", $("FiltroHasta").value);
  if ($("FiltroTipo").value) p.set("tipo", $("FiltroTipo").value);
  if ($("FiltroTexto").value.trim()) p.set("texto", $("FiltroTexto").value.trim());
  try {
    const r = await api("GET", "/api/comprobantes?" + p);
    $("TablaHistorial").tBodies[0].innerHTML = r.comprobantes.map((c) =>
      `<tr data-numero="${escapar(c.numero)}"><td>${escapar(c.tipo)}</td><td>${escapar(c.numero)}</td><td>${fechaHora(c.fecha)}</td>` +
      `<td>${escapar(c.cliente ? c.cliente.nombre : "Sin cliente")}</td><td>${escapar(c.usuario)}</td><td class="d">${soles(c.total)}</td><td>${escapar(c.estadoSunat)}</td></tr>`).join("");
    texto($("TextoHistorial"), r.cantidad === 0 ? "No hay comprobantes con esos filtros."
      : `${r.cantidad} comprobantes${r.cantidad > r.comprobantes.length ? ` (se muestran ${r.comprobantes.length})` : ""} · Total del período ${soles(r.total)}`);
  } catch (e) {
    $("TablaHistorial").tBodies[0].innerHTML = "";
    texto($("TextoHistorial"), "");
    error($("ErrorHistorial"), e.message);
  }
}

// ---------------------------------------------------------------- proveedores

async function buscarProveedores() {
  try {
    const t = $("CampoBuscarProveedores").value.trim();
    const lista = await api("GET", `/api/proveedores?limite=200${t ? "&texto=" + encodeURIComponent(t) : ""}`);
    $("TablaProveedores").tBodies[0].innerHTML = lista.map((p) =>
      `<tr><td>${escapar(p.ruc)}</td><td>${escapar(p.razonSocial)}</td><td>${escapar(p.telefono || "")}</td><td>${escapar(p.contacto || "")}</td></tr>`).join("");
    texto($("TextoProveedores"), `${lista.length} proveedores.`);
  } catch (e) { texto($("TextoProveedores"), e.message); }
}

// ---------------------------------------------------------------- compras

async function buscarCompras() {
  if (!$("CompraDesde").value) $("CompraDesde").value = inicioMesIso();
  if (!$("CompraHasta").value) $("CompraHasta").value = hoyIso();
  error($("ErrorCompras"), "");
  const p = new URLSearchParams({ desde: $("CompraDesde").value, hasta: $("CompraHasta").value });
  if ($("CompraProveedor").value.trim()) p.set("proveedor", $("CompraProveedor").value.trim());
  try {
    const r = await api("GET", "/api/compras?" + p);
    $("TablaCompras").tBodies[0].innerHTML = r.compras.map((c) =>
      `<tr data-documento="${escapar(c.documento)}"><td>${escapar(c.documento)}</td><td>${fechaCorta(c.fechaEmision)}</td><td>${escapar(c.rucProveedor || "")}</td>` +
      `<td>${escapar(c.proveedor || "")}</td><td class="d">${soles(c.opGravada)}</td><td class="d">${soles(c.igv)}</td><td class="d">${soles(c.total)}</td></tr>`).join("");
    texto($("TextoCompras"), r.cantidad === 0 ? "No hay compras en el período." : `${r.cantidad} compras · Egresos del período ${soles(r.total)}`);
  } catch (e) {
    $("TablaCompras").tBodies[0].innerHTML = "";
    texto($("TextoCompras"), "");
    error($("ErrorCompras"), e.message);
  }
}

let compra = { lineas: [], productos: [] };
function abrirNuevaCompra() {
  compra = { lineas: [], productos: [] };
  abrirModal("VentanaNuevaCompra", "Compras");
  $("CampoCompraFecha").value = hoyIso();
  $("CampoCompraCantidad").value = "1";
  pintarCompra();
}

let temporizadorCompra = null;
function alEscribirProductoCompra() {
  clearTimeout(temporizadorCompra);
  const t = $("CampoCompraProducto").value.trim();
  if (t.length < 3 || compra.productos.some((p) => p.nombre === t)) return;
  temporizadorCompra = setTimeout(async () => {
    try {
      compra.productos = await api("GET", `/api/productos?texto=${encodeURIComponent(t)}&limite=15`);
      $("ListaCompraProductos").innerHTML = compra.productos.map((p) => `<option value="${escapar(p.nombre)}"></option>`).join("");
    } catch { /* la lista queda vacía */ }
  }, 220);
}

function agregarLineaCompra() {
  const aviso = $("ErrorNuevaCompra");
  const producto = compra.productos.find((p) => p.nombre === $("CampoCompraProducto").value.trim());
  const cantidad = Number($("CampoCompraCantidad").value.replace(",", "."));
  const costo = Number($("CampoCompraCosto").value.replace(",", "."));
  if (!producto) { texto(aviso, "Elija un producto de la lista del catálogo."); mostrar(aviso, true); return; }
  if (!(cantidad > 0) || !(costo > 0)) { texto(aviso, "Cada producto debe tener cantidad y costo mayores que cero."); mostrar(aviso, true); return; }
  mostrar(aviso, false);
  compra.lineas.push({ productoId: producto.id, nombre: producto.nombre, cantidad, costoUnitario: costo });
  $("CampoCompraProducto").value = "";
  $("CampoCompraCosto").value = "";
  $("CampoCompraCantidad").value = "1";
  pintarCompra();
  $("CampoCompraProducto").focus();
}

function pintarCompra() {
  $("TablaLineasCompra").tBodies[0].innerHTML = compra.lineas.map((l, i) =>
    `<tr><td>${escapar(l.nombre)}</td><td class="c">${l.cantidad}</td><td class="d">${l.costoUnitario.toFixed(2)}</td>` +
    `<td class="d">${redondear(l.cantidad * l.costoUnitario).toFixed(2)}</td><td class="c"><button type="button" class="quitar" data-indice="${i}" title="Quitar"></button></td></tr>`).join("");
  texto($("TextoTotalCompra"), soles(compra.lineas.reduce((s, l) => s + redondear(l.cantidad * l.costoUnitario), 0)));
}

async function guardarCompra(e) {
  e.preventDefault();
  try {
    const c = await api("POST", "/api/compras", {
      rucProveedor: $("CampoCompraRuc").value.trim(),
      tipoDocumento: $("CampoCompraTipo").value,
      serie: $("CampoCompraSerie").value.trim(),
      numero: Number($("CampoCompraNumero").value) || 0,
      fechaEmision: $("CampoCompraFecha").value || null,
      detalle: compra.lineas.map((l) => ({ productoId: l.productoId, cantidad: l.cantidad, costoUnitario: l.costoUnitario })),
    });
    cerrarModales();
    mensaje(`Compra ${c.documento} de ${c.proveedor} registrada (${soles(c.total)}).`);
    $("CompraProveedor").value = c.rucProveedor;
    buscarCompras();
  } catch (err) { errorModal("ErrorNuevaCompra", err); }
}

// ---------------------------------------------------------------- proformas

let proformaElegida = null;
async function buscarProformas() {
  try {
    const t = $("CampoBuscarProformas").value.trim();
    const lista = await api("GET", `/api/proformas?limite=200${t ? "&texto=" + encodeURIComponent(t) : ""}`);
    proformaElegida = null;
    $("BotonConvertir").disabled = true;
    const cuerpo = $("TablaProformas").tBodies[0];
    cuerpo._datos = lista;
    cuerpo.innerHTML = lista.map((p, i) => {
      const estado = p.estado === "CONVERTIDA" ? `Convertida en ${p.convertidaEn}`
        : p.estado === "VENCIDA" ? `Vencida el ${fechaCorta(p.validaHasta)}` : `Vigente hasta el ${fechaCorta(p.validaHasta)}`;
      return `<tr data-indice="${i}" data-numero="${escapar(p.numero)}"><td>${escapar(p.numero)}</td><td>${fechaHora(p.fecha)}</td>` +
        `<td>${escapar(p.cliente ? p.cliente.nombre : "Sin cliente")}</td><td>${escapar(p.cliente ? p.cliente.numeroDocumento : "")}</td>` +
        `<td class="d">${soles(p.total)}</td><td class="estado estado-${p.estado.toLowerCase()}">${escapar(estado)}</td></tr>`;
    }).join("");
    const vigentes = lista.filter((p) => p.estado === "VIGENTE").length;
    texto($("TextoProformas"), `${lista.length} proformas, ${vigentes} vigentes. Elija una y pulse Convertir en venta (Enter).`);
  } catch (e) { texto($("TextoProformas"), e.message); }
}

function elegirProforma(fila) {
  document.querySelectorAll("#TablaProformas tr.elegida").forEach((f) => f.classList.remove("elegida"));
  fila.classList.add("elegida");
  proformaElegida = $("TablaProformas").tBodies[0]._datos[Number(fila.dataset.indice)];
  const vigente = proformaElegida.estado === "VIGENTE";
  $("BotonConvertir").disabled = !vigente;
  mensaje(vigente ? "" : proformaElegida.estado === "CONVERTIDA"
    ? `La proforma ${proformaElegida.numero} ya se convirtió en ${proformaElegida.convertidaEn}.`
    : `La proforma ${proformaElegida.numero} está vencida: emita una proforma nueva con los precios de hoy.`, !vigente);
}

async function convertirProforma() {
  if (!proformaElegida || proformaElegida.estado !== "VIGENTE") return;
  try {
    const completa = await api("GET", `/api/comprobantes/${proformaElegida.id}`);
    cancelarVenta();
    ocultarResultado(); // DEF-04: no dejar a la vista el aviso de la emisión anterior
    venta.proforma = proformaElegida;
    venta.detalle = completa.detalle.map((l) => ({ productoId: l.productoId, descripcion: l.descripcion, unidad: l.unidad, cantidad: l.cantidad, precio: l.precioUnitario }));
    irA("Venta");
    if (completa.cliente) elegirCliente(completa.cliente);
    if (!completa.cliente || completa.cliente.tipoDocumento === "DNI") $(completa.cliente ? "TipoConDni" : "TipoBoleta").checked = true;
    else $("TipoFactura").checked = true;
    pintarVenta();
    mensaje(`Proforma ${proformaElegida.numero} lista para emitir.`);
  } catch (e) { mensaje(e.message, true); }
}

// ---------------------------------------------------------------- reporte y respaldos

async function generarReporte() {
  if (!$("ReporteDesde").value) $("ReporteDesde").value = inicioMesIso();
  if (!$("ReporteHasta").value) $("ReporteHasta").value = hoyIso();
  error($("ErrorReporte"), "");
  try {
    const r = await api("GET", `/api/reportes/ventas?desde=${$("ReporteDesde").value}&hasta=${$("ReporteHasta").value}`);
    texto($("ReporteCantidad"), r.cantidadVentas);
    texto($("ReporteTotal"), soles(r.total));
    texto($("ReporteIgv"), soles(r.igv));
    texto($("ReportePromedio"), soles(r.ticketPromedio));
    texto($("ReportePendientes"), r.pendientesSunat);
    const filas = (lista) => lista.map((l) => `<tr><td>${escapar(l.clave)}</td><td class="c">${l.cantidad}</td><td class="d">${soles(l.total)}</td></tr>`).join("");
    $("TablaReporteTipo").tBodies[0].innerHTML = filas(r.porTipo);
    $("TablaReporteUsuario").tBodies[0].innerHTML = filas(r.porUsuario);
    $("TablaReporteTerminal").tBodies[0].innerHTML = filas(r.porTerminal);
    $("TablaReporteDia").tBodies[0].innerHTML = filas(r.porDia);
    mostrar($("ResultadoReporte"), true);
  } catch (e) {
    mostrar($("ResultadoReporte"), false);
    error($("ErrorReporte"), e.message);
  }
}

async function listarRespaldos() {
  try {
    const lista = await api("GET", "/api/respaldos");
    $("TablaRespaldos").tBodies[0].innerHTML = lista.map((r) =>
      `<tr><td>${escapar(r.archivo)}</td><td>${escapar(r.carpeta)}</td><td class="d">${escapar(r.tamano)}</td><td>${fechaHora(r.terminadoEn)}</td><td>${escapar(r.terminal || "")}</td></tr>`).join("");
    texto($("TextoRespaldos"), lista.length ? `${lista.length} respaldos (los últimos 10).` : "Aún no se ha generado ningún respaldo de la base de datos.");
  } catch (e) { texto($("TextoRespaldos"), e.message); }
}

// ---------------------------------------------------------------- ventanas modales

let origenModal = null;
function abrirModal(id, origen) {
  origenModal = origen;
  const f = $(id);
  f.reset();
  mostrar(f.querySelector(".aviso-error"), false);
  mostrar($("Velo"), true);
  mostrar(f, true);
  f.querySelector("input").focus();
}
function cerrarModales() {
  document.querySelectorAll(".modal").forEach((m) => mostrar(m, false));
  mostrar($("Velo"), false);
}
function hayModal() { return !$("Velo").classList.contains("oculto"); }
function errorModal(id, e) { const el = $(id); texto(el, e.detalle || e.message); mostrar(el, true); }

async function guardarProducto(e) {
  e.preventDefault();
  try {
    const p = await api("POST", "/api/productos", {
      nombre: $("CampoNombreProducto").value.trim(),
      precio: Number($("CampoPrecioProducto").value.replace(",", ".")) || 0,
      unidad: $("CampoUnidadProducto").value,
      codigoBarras: $("CampoCodigoProducto").value.trim() || null,
    });
    cerrarModales();
    mensaje(`Producto «${p.nombre}» registrado en el catálogo.`);
    if (origenModal === "Venta") { venta.seleccionado = p; $("CampoProducto").value = p.nombre; $("CampoCantidad").focus(); }
    else { $("CampoBuscarCatalogo").value = p.nombre; buscarCatalogo(); }
  } catch (err) { errorModal("ErrorNuevoProducto", err); }
}

async function guardarCliente(e) {
  e.preventDefault();
  try {
    const c = await api("POST", "/api/clientes", {
      documento: $("CampoNuevoDocumento").value.trim(),
      nombre: $("CampoNuevoNombre").value.trim(),
      direccion: $("CampoNuevaDireccion").value.trim() || null,
    });
    cerrarModales();
    mensaje(`Cliente ${c.nombre} registrado.`);
    if (origenModal === "Venta") elegirCliente(c);
    else { $("CampoBuscarClientes").value = c.numeroDocumento; buscarClientes(); }
  } catch (err) { errorModal("ErrorNuevoCliente", err); }
}

async function guardarProveedor(e) {
  e.preventDefault();
  try {
    const p = await api("POST", "/api/proveedores", {
      ruc: $("CampoProveedorRuc").value.trim(),
      razonSocial: $("CampoProveedorRazon").value.trim(),
      telefono: $("CampoProveedorTelefono").value.trim() || null,
      contacto: $("CampoProveedorContacto").value.trim() || null,
    });
    cerrarModales();
    mensaje(`Proveedor ${p.razonSocial} registrado.`);
    $("CampoBuscarProveedores").value = p.ruc;
    buscarProveedores();
  } catch (err) { errorModal("ErrorNuevoProveedor", err); }
}

// ---------------------------------------------------------------- teclado y reloj

const TECLAS = Object.fromEntries(Object.entries(MODULOS).map(([m, d]) => [d.tecla, m]));

function teclaGlobal(e) {
  if (!sesion) return;
  if (e.key === "Escape") {
    e.preventDefault();
    if (hayModal()) cerrarModales();
    else if (venta.sugerencias.length) cerrarSugerencias();
    else if (moduloActual !== "Venta") irA("Venta");
    else cancelarVenta();
    return;
  }
  if (hayModal()) return;
  if (TECLAS[e.key]) { e.preventDefault(); irA(TECLAS[e.key]); return; }
  if (e.key === "F10") { e.preventDefault(); if (moduloActual === "Venta") emitir(); return; }
  if (e.altKey && (e.key === "d" || e.key === "D")) { e.preventDefault(); irA("Venta"); $("CampoDocumento").focus(); return; }
  if (e.key === "Enter" && moduloActual === "Proformas" && proformaElegida && document.activeElement?.tagName !== "INPUT") { e.preventDefault(); convertirProforma(); }
}

function reloj() {
  const d = new Date();
  texto($("Fecha"), d.toLocaleDateString("es-PE", { day: "numeric", month: "short", year: "numeric" }));
  texto($("Hora"), d.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit", hour12: false }));
}

async function vigilarConexion() {
  try { conexion((await fetch("/api/salud")).ok); } catch { conexion(false); }
}

// ---------------------------------------------------------------- arranque

function enlazar() {
  $("VentanaIngresar").addEventListener("submit", ingresar);
  $("BotonSalir").addEventListener("click", () => { $("CampoUsuario").value = ""; $("CampoClave").value = ""; mostrar($("AvisoError"), false); $("CampoUsuario").focus(); });
  document.querySelectorAll(".menu[data-modulo]").forEach((b) => b.addEventListener("click", () => irA(b.dataset.modulo)));
  $("MenuCerrarSesion").addEventListener("click", () => cerrarSesion());
  window.addEventListener("hashchange", () => { const m = moduloDeHash(); if (m && m !== moduloActual) irA(m); });
  document.addEventListener("keydown", teclaGlobal);

  $("CampoProducto").addEventListener("input", alEscribirProducto);
  $("CampoProducto").addEventListener("keydown", teclaProducto);
  $("CampoProducto").addEventListener("blur", () => setTimeout(() => mostrar($("ListaSugerencias"), false), 150));
  $("ListaSugerencias").addEventListener("mousedown", (e) => { const li = e.target.closest("li"); if (li) { e.preventDefault(); elegirSugerencia(Number(li.dataset.indice)); } });
  $("CampoCantidad").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); agregar(); } });
  $("BotonAgregar").addEventListener("click", agregar);
  $("TablaDetalle").addEventListener("change", (e) => { if (e.target.matches("input.cantidad")) cambiarCantidad(e); });
  $("TablaDetalle").addEventListener("click", (e) => { const b = e.target.closest("button.quitar"); if (b) quitarLinea(Number(b.dataset.indice)); });
  $("CampoDocumento").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); buscarCliente(); } });
  $("BotonBuscarCliente").addEventListener("click", buscarCliente);
  $("BotonQuitarCliente").addEventListener("click", quitarCliente);
  $("BotonEmitir").addEventListener("click", emitir);
  $("BotonCancelarVenta").addEventListener("click", cancelarVenta);
  document.querySelectorAll('input[name="tipo"]').forEach((r) => r.addEventListener("change", () => { mostrar($("ErrorEmision"), false); ocultarResultado(); }));

  $("BotonNuevoProducto").addEventListener("click", () => abrirModal("VentanaNuevoProducto", "Venta"));
  $("BotonNuevoProductoCatalogo").addEventListener("click", () => abrirModal("VentanaNuevoProducto", "Catalogo"));
  $("BotonNuevoCliente").addEventListener("click", () => { abrirModal("VentanaNuevoCliente", "Venta"); $("CampoNuevoDocumento").value = $("CampoDocumento").value.trim(); });
  $("BotonNuevoClienteModulo").addEventListener("click", () => abrirModal("VentanaNuevoCliente", "Clientes"));
  $("BotonNuevoProveedor").addEventListener("click", () => abrirModal("VentanaNuevoProveedor", "Proveedores"));
  $("VentanaNuevoProducto").addEventListener("submit", guardarProducto);
  $("VentanaNuevoCliente").addEventListener("submit", guardarCliente);
  $("VentanaNuevoProveedor").addEventListener("submit", guardarProveedor);
  document.querySelectorAll(".cerrar-modal").forEach((b) => b.addEventListener("click", cerrarModales));
  $("Velo").addEventListener("click", cerrarModales);

  $("BotonBuscarCatalogo").addEventListener("click", buscarCatalogo);
  $("CampoBuscarCatalogo").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarCatalogo(); });
  $("BotonBuscarClientes").addEventListener("click", buscarClientes);
  $("CampoBuscarClientes").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarClientes(); });
  $("TablaClientes").addEventListener("click", (e) => {
    const fila = e.target.closest("tbody tr"); if (!fila) return;
    document.querySelectorAll("#TablaClientes tr.elegida").forEach((f) => f.classList.remove("elegida"));
    fila.classList.add("elegida");
    clienteElegido = $("TablaClientes").tBodies[0]._datos[Number(fila.dataset.indice)];
    $("BotonUsarCliente").disabled = false;
  });
  $("TablaClientes").addEventListener("dblclick", usarCliente);
  $("BotonUsarCliente").addEventListener("click", usarCliente);

  $("BotonBuscarHistorial").addEventListener("click", () => { delete $("FiltroDesde").dataset.todo; buscarHistorial(); });
  $("FiltroTexto").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarHistorial(); });
  $("BotonHoy").addEventListener("click", () => { delete $("FiltroDesde").dataset.todo; rangoHistorial(hoyIso(), hoyIso()); });
  $("BotonEsteMes").addEventListener("click", () => { delete $("FiltroDesde").dataset.todo; rangoHistorial(inicioMesIso(), hoyIso()); });
  $("BotonTodo").addEventListener("click", () => { $("FiltroDesde").dataset.todo = "1"; rangoHistorial("", ""); });

  $("BotonBuscarProveedores").addEventListener("click", buscarProveedores);
  $("CampoBuscarProveedores").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarProveedores(); });
  $("BotonBuscarProformas").addEventListener("click", buscarProformas);
  $("CampoBuscarProformas").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarProformas(); });
  $("TablaProformas").addEventListener("click", (e) => { const f = e.target.closest("tbody tr"); if (f) elegirProforma(f); });
  $("TablaProformas").addEventListener("dblclick", convertirProforma);
  $("BotonConvertir").addEventListener("click", convertirProforma);
  $("BotonGenerarReporte").addEventListener("click", generarReporte);
  $("BotonBuscarCompras").addEventListener("click", buscarCompras);
  $("CompraProveedor").addEventListener("keydown", (e) => { if (e.key === "Enter") buscarCompras(); });
  $("BotonNuevaCompra").addEventListener("click", abrirNuevaCompra);
  $("CampoCompraProducto").addEventListener("input", alEscribirProductoCompra);
  $("BotonAgregarLineaCompra").addEventListener("click", agregarLineaCompra);
  $("TablaLineasCompra").addEventListener("click", (e) => { const b = e.target.closest("button.quitar"); if (b) { compra.lineas.splice(Number(b.dataset.indice), 1); pintarCompra(); } });
  $("VentanaNuevaCompra").addEventListener("submit", guardarCompra);
}

enlazar();
reloj();
setInterval(reloj, 20000);
setInterval(vigilarConexion, 10000);
pintarVenta();
try { sesion = JSON.parse(sessionStorage.getItem(CLAVE_SESION) || "null"); } catch { sesion = null; }
if (sesion) abrirPrincipal(); else $("CampoUsuario").focus();
