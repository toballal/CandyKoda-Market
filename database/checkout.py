import hashlib
from decimal import Decimal

from database.connection import conectar
from database.configuracion_sistema import market_en_mantenimiento
from database.logs import registrar_log


class CheckoutError(Exception):
    pass


def crear_compra(uid, pin, carrito):
    """Registra pago, venta, entrega e historiales en una sola transacción."""
    if market_en_mantenimiento():
        return {
            "exito": False,
            "mensaje": "Las compras están pausadas por mantenimiento",
        }
    if not carrito:
        return {"exito": False, "mensaje": "El carrito está vacío"}

    db = conectar()
    if db is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}

    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_tarjeta, id_cliente, saldo, estado, pin_hash
            FROM tarjetas_nfc WHERE uid = %s FOR UPDATE
            """,
            (uid,),
        )
        tarjeta = cursor.fetchone()
        pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
        if tarjeta is None or tarjeta["estado"] != "Activa":
            raise CheckoutError("Tarjeta no registrada o inactiva")
        if tarjeta["pin_hash"] != pin_hash:
            raise CheckoutError("PIN incorrecto")

        ids = [int(item["id_producto"]) for item in carrito]
        placeholders = ", ".join(["%s"] * len(ids))
        cursor.execute(
            f"""
            SELECT p.id_producto, p.nombre, p.precio, p.stock, p.estado,
                   d.id_dispensador, d.cantidad_disponible, d.estado AS estado_dispensador
            FROM productos p
            INNER JOIN dispensadores d ON d.id_producto = p.id_producto
            WHERE p.id_producto IN ({placeholders}) FOR UPDATE
            """,
            tuple(ids),
        )
        catalogo = {row["id_producto"]: row for row in cursor.fetchall()}

        total = Decimal("0")
        for item in carrito:
            producto = catalogo.get(int(item["id_producto"]))
            cantidad = int(item["cantidad"])
            if not producto or producto["estado"] != "Disponible":
                raise CheckoutError(f"{item['producto']} ya no está disponible")
            if cantidad <= 0 or int(producto["stock"]) < cantidad:
                raise CheckoutError(f"Stock insuficiente para {producto['nombre']}")
            if producto["id_dispensador"] is None:
                raise CheckoutError(f"{producto['nombre']} no tiene dispensador asignado")
            if int(producto["cantidad_disponible"] or 0) < cantidad:
                raise CheckoutError(f"El dispensador no tiene suficiente {producto['nombre']}")
            total += Decimal(producto["precio"]) * cantidad

        saldo = Decimal(tarjeta["saldo"])
        if saldo < total:
            raise CheckoutError("Saldo insuficiente")

        cursor.execute(
            "INSERT INTO ventas (id_cliente, id_tarjeta, total, estado) VALUES (%s, %s, %s, 'Pagada')",
            (tarjeta["id_cliente"], tarjeta["id_tarjeta"], total),
        )
        id_venta = cursor.lastrowid
        entregas = []

        for item in carrito:
            producto = catalogo[int(item["id_producto"])]
            cantidad = int(item["cantidad"])
            precio = Decimal(producto["precio"])
            stock_anterior = int(producto["stock"])
            stock_nuevo = stock_anterior - cantidad
            cursor.execute(
                """
                INSERT INTO detalle_venta
                    (id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal, estado_entrega)
                VALUES (%s, %s, %s, %s, 0, %s, 'Pendiente')
                """,
                (id_venta, producto["id_producto"], cantidad, precio, precio * cantidad),
            )
            id_detalle = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO entregas (id_detalle, id_dispensador, cantidad_solicitada, estado)
                VALUES (%s, %s, %s, 'Pendiente')
                """,
                (id_detalle, producto["id_dispensador"], cantidad),
            )
            entregas.append({
                "id_entrega": cursor.lastrowid,
                "id_detalle": id_detalle,
                "id_dispensador": producto["id_dispensador"],
                "cantidad": cantidad,
                "producto": producto["nombre"],
            })
            cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (stock_nuevo, producto["id_producto"]))
            cursor.execute(
                """
                INSERT INTO movimientos_inventario
                    (id_producto, tipo, cantidad, stock_anterior, stock_nuevo, descripcion)
                VALUES (%s, 'Salida', %s, %s, %s, %s)
                """,
                (producto["id_producto"], cantidad, stock_anterior, stock_nuevo, f"Venta #{id_venta}"),
            )

        saldo_nuevo = saldo - total
        cursor.execute("UPDATE tarjetas_nfc SET saldo = %s WHERE id_tarjeta = %s", (saldo_nuevo, tarjeta["id_tarjeta"]))
        cursor.execute(
            """
            INSERT INTO movimientos_tarjeta
                (id_tarjeta, tipo, monto, saldo_anterior, saldo_nuevo, descripcion)
            VALUES (%s, 'Compra', %s, %s, %s, %s)
            """,
            (tarjeta["id_tarjeta"], total, saldo, saldo_nuevo, f"Compra #{id_venta}"),
        )
        registrar_log("Pay", "Pago aprobado", f"Venta #{id_venta} por ${total:,.0f}", conexion=db)
        db.commit()
        return {
            "exito": True,
            "mensaje": "Pago realizado correctamente",
            "id_venta": id_venta,
            "total": total,
            "saldo_restante": saldo_nuevo,
            "entregas": entregas,
        }
    except CheckoutError as error:
        db.rollback()
        return {"exito": False, "mensaje": str(error)}
    except Exception as error:
        db.rollback()
        print("Error al procesar compra:", error)
        return {"exito": False, "mensaje": "No se pudo completar la compra"}
    finally:
        if cursor:
            cursor.close()
        db.close()
