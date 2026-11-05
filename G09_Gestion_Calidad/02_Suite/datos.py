"""Datos de prueba de la suite (ver 03_Datos/datos_prueba.md).

- Credenciales: los usuarios de demostración de la migración V014.
- Datos aislados: cada ejecución genera DNI, RUC (con dígito verificador
  válido), nombres de producto y series de compra que no existen en la base,
  con un sufijo de la ejecución. Así ningún caso depende de lo que dejó otro ni
  de una ejecución anterior.
- Datos inválidos: valores fijos que violan una regla de Condor.Dominio.
"""
import random
import time

ENCARGADO = ("encargado", "Encargado2026!")
VENDEDOR = ("vendedor1", "Vendedor2026!")
# vendedor2 solo se usa en el caso de credenciales inválidas, para que su
# intento fallido no afecte a los demás casos (5 fallos bloquean la cuenta).
VENDEDOR_CLAVE_ERRADA = ("vendedor2", "ClaveEquivocada1")
VENDEDOR2 = ("vendedor2", "Vendedor2026!")

# Producto del catálogo de demostración que siempre existe (db/datos/lista_precios.csv).
PRODUCTO_BUSQUEDA = "cemento"

SUFIJO = time.strftime("%m%d%H%M%S")
_azar = random.Random()

PESOS_RUC = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)


def digito_ruc(primeros_diez):
    suma = sum(int(d) * p for d, p in zip(primeros_diez, PESOS_RUC))
    return (11 - suma % 11) % 10


def ruc_valido(prefijo="20"):
    cuerpo = prefijo + "".join(str(_azar.randint(0, 9)) for _ in range(8))
    return cuerpo + str(digito_ruc(cuerpo))


def ruc_digito_errado():
    ruc = ruc_valido()
    return ruc[:10] + str((int(ruc[10]) + 1) % 10)


def dni_nuevo():
    # Empieza con 9: los DNI de los datos de demostración no empiezan así.
    return "9" + "".join(str(_azar.randint(0, 9)) for _ in range(7))


def nombre_producto():
    return f"Producto G09 prueba {SUFIJO}-{_azar.randint(100, 999)}"


def nombre_cliente():
    return f"Cliente G09 {SUFIJO}-{_azar.randint(100, 999)}"


def numero_compra():
    return _azar.randint(10_000_000, 99_999_999)


# Datos inválidos (reglas de ValidadorDocumento, ValidadorProducto y EmisionComprobante).
DNI_CORTO = "1234"
PRECIO_CERO = "0"
CANTIDAD_INVALIDA = "0"
