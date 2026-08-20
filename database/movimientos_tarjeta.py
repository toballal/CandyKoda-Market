from database.connection import conectar


def registrar_movimiento(
    id_tarjeta,
    tipo,
    monto,
    saldo_anterior,
    saldo_nuevo,
    descripcion,
    id_usuario=None
):
    conexion = conectar()

    if conexion is None:
        return None

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            INSERT INTO movimientos_tarjeta (
                id_tarjeta,
                id_usuario,
                tipo,
                monto,
                saldo_anterior,
                saldo_nuevo,
                descripcion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                id_tarjeta,
                id_usuario,
                tipo,
                monto,
                saldo_anterior,
                saldo_nuevo,
                descripcion
            )
        )

        conexion.commit()

        return cursor.lastrowid

    except Exception as e:
        print("Error al registrar movimiento:", e)
        conexion.rollback()
        return None

    finally:
        if cursor:
            cursor.close()

        conexion.close()