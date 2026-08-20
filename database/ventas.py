from database.connection import conectar


def crear_venta(id_cliente, id_tarjeta, total):
    conexion = conectar()

    if conexion is None:
        return None

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            INSERT INTO ventas
            (
                id_cliente,
                id_tarjeta,
                total,
                estado
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                id_cliente,
                id_tarjeta,
                total,
                "completada"
            )
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception as e:
        print("Error al crear venta:", e)
        conexion.rollback()
        return None

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def agregar_detalle_venta(
    id_venta,
    id_producto,
    cantidad,
    precio_unitario,
    descuento=0
):
    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        subtotal = (precio_unitario * cantidad) - descuento

        sql = """
            INSERT INTO detalle_venta (
                id_venta,
                id_producto,
                cantidad,
                precio_unitario,
                descuento,
                subtotal,
                estado_entrega
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                id_venta,
                id_producto,
                cantidad,
                precio_unitario,
                descuento,
                subtotal,
                "pendiente"
            )
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception as e:
        print("Error al agregar detalle de venta:", e)
        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()