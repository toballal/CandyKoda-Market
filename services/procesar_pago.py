from app_state import obtener_carrito
from database.checkout import crear_compra
from threading import Lock

_bloqueo_pago = Lock()


def procesar_pago(uid, pin):
    if not _bloqueo_pago.acquire(blocking=False):
        return {"exito": False, "mensaje": "Ya hay un pago en proceso"}
    try:
        return crear_compra(uid, pin, obtener_carrito())
    finally:
        _bloqueo_pago.release()
