from database.connection import conectar
from database.logs import registrar_log


def iniciar_entrega(id_entrega, id_venta):
    return _actualizar(
        id_entrega,
        id_venta,
        "Dispensando",
        "UPDATE entregas SET estado='Dispensando', fecha_inicio=NOW(), mensaje_error=NULL WHERE id_entrega=%s",
    )


def completar_entrega(id_entrega, id_detalle, id_dispensador, cantidad, id_venta):
    db = conectar()
    if db is None:
        return False
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE entregas SET cantidad_entregada=%s, sensor_confirmado=1,
                estado='Completada', fecha_fin=NOW(), mensaje_error=NULL
            WHERE id_entrega=%s
            """,
            (cantidad, id_entrega),
        )
        cursor.execute("UPDATE detalle_venta SET estado_entrega='Entregado' WHERE id_detalle=%s", (id_detalle,))
        cursor.execute(
            "UPDATE dispensadores SET cantidad_disponible=GREATEST(0, cantidad_disponible-%s), estado=IF(cantidad_disponible<=0, 'Sin stock', 'Disponible') WHERE id_dispensador=%s",
            (cantidad, id_dispensador),
        )
        cursor.execute(
            "UPDATE ventas SET estado=IF(NOT EXISTS (SELECT 1 FROM detalle_venta WHERE id_venta=%s AND estado_entrega<>'Entregado'), 'Completada', 'Entregando') WHERE id_venta=%s",
            (id_venta, id_venta),
        )
        registrar_log("Arduino", "Entrega completada", f"Entrega #{id_entrega}, venta #{id_venta}", conexion=db)
        db.commit()
        return True
    except Exception as error:
        db.rollback()
        print("Error al completar entrega:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        db.close()


def marcar_error(id_entrega, id_detalle, id_venta, mensaje):
    db = conectar()
    if db is None:
        return False
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE entregas SET estado='Error', mensaje_error=%s, fecha_fin=NOW() WHERE id_entrega=%s",
            (mensaje[:255], id_entrega),
        )
        cursor.execute("UPDATE detalle_venta SET estado_entrega='Error' WHERE id_detalle=%s", (id_detalle,))
        cursor.execute("UPDATE ventas SET estado='Error' WHERE id_venta=%s", (id_venta,))
        registrar_log("Arduino", "Error de entrega", f"Venta #{id_venta}: {mensaje}", nivel="Error", conexion=db)
        db.commit()
        return True
    except Exception as error:
        db.rollback()
        print("Error al guardar fallo de entrega:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        db.close()


def _actualizar(id_entrega, id_venta, estado, sql):
    db = conectar()
    if db is None:
        return False
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(sql, (id_entrega,))
        cursor.execute("UPDATE ventas SET estado='Entregando' WHERE id_venta=%s", (id_venta,))
        db.commit()
        return True
    except Exception as error:
        db.rollback()
        print(f"Error al marcar entrega {estado}:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        db.close()
