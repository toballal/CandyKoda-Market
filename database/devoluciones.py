from decimal import Decimal

from database.connection import conectar
from database.logs import registrar_log


def devolver_productos_no_entregados(id_venta):
    """Devuelve solo lo no entregado; es idempotente por número de venta."""
    db = conectar()
    if db is None:
        return {"exito": False, "monto": Decimal("0")}
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id_tarjeta FROM ventas WHERE id_venta=%s FOR UPDATE", (id_venta,))
        venta = cursor.fetchone()
        if not venta or venta["id_tarjeta"] is None:
            db.rollback()
            return {"exito": False, "monto": Decimal("0")}

        descripcion = f"Devolución automática venta #{id_venta}"
        cursor.execute(
            "SELECT monto, saldo_nuevo FROM movimientos_tarjeta WHERE id_tarjeta=%s AND tipo='Devolucion' AND descripcion=%s LIMIT 1",
            (venta["id_tarjeta"], descripcion),
        )
        existente = cursor.fetchone()
        if existente:
            db.rollback()
            return {"exito": True, "monto": Decimal(existente["monto"]), "saldo_nuevo": Decimal(existente["saldo_nuevo"]), "ya_realizada": True}

        cursor.execute(
            """
            SELECT dv.id_detalle, dv.id_producto, dv.cantidad, dv.subtotal, p.nombre
            FROM detalle_venta dv
            JOIN productos p ON p.id_producto=dv.id_producto
            LEFT JOIN entregas e ON e.id_detalle=dv.id_detalle
            WHERE dv.id_venta=%s AND COALESCE(e.estado, 'Error') <> 'Completada'
            """,
            (id_venta,),
        )
        pendientes = cursor.fetchall()
        monto = sum((Decimal(row["subtotal"]) for row in pendientes), Decimal("0"))
        if monto <= 0:
            db.rollback()
            return {"exito": False, "monto": Decimal("0")}

        cursor.execute("SELECT saldo FROM tarjetas_nfc WHERE id_tarjeta=%s FOR UPDATE", (venta["id_tarjeta"],))
        saldo_anterior = Decimal(cursor.fetchone()["saldo"])
        saldo_nuevo = saldo_anterior + monto
        cursor.execute("UPDATE tarjetas_nfc SET saldo=%s WHERE id_tarjeta=%s", (saldo_nuevo, venta["id_tarjeta"]))
        cursor.execute(
            "INSERT INTO movimientos_tarjeta (id_tarjeta, tipo, monto, saldo_anterior, saldo_nuevo, descripcion) VALUES (%s, 'Devolucion', %s, %s, %s, %s)",
            (venta["id_tarjeta"], monto, saldo_anterior, saldo_nuevo, descripcion),
        )
        for row in pendientes:
            cursor.execute("SELECT stock FROM productos WHERE id_producto=%s FOR UPDATE", (row["id_producto"],))
            stock_anterior = int(cursor.fetchone()["stock"])
            stock_nuevo = stock_anterior + int(row["cantidad"])
            cursor.execute("UPDATE productos SET stock=%s, estado='Disponible' WHERE id_producto=%s", (stock_nuevo, row["id_producto"]))
            cursor.execute(
                "INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, stock_anterior, stock_nuevo, descripcion) VALUES (%s, 'Entrada', %s, %s, %s, %s)",
                (row["id_producto"], row["cantidad"], stock_anterior, stock_nuevo, descripcion),
            )
        registrar_log("Pay", "Devolución automática", f"Venta #{id_venta}: ${monto:,.0f} devueltos", nivel="Advertencia", conexion=db)
        db.commit()
        return {"exito": True, "monto": monto, "saldo_nuevo": saldo_nuevo, "ya_realizada": False}
    except Exception as error:
        db.rollback()
        print("Error en devolución automática:", error)
        return {"exito": False, "monto": Decimal("0")}
    finally:
        if cursor:
            cursor.close()
        db.close()
