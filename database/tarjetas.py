from database.connection import conectar
import hashlib

def obtener_datos_tarjeta(uid):
    conexion = conectar()

    if conexion is None:
        return None

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_tarjeta,
                id_cliente,
                saldo
            FROM tarjetas_nfc
            WHERE uid = %s
        """

        cursor.execute(sql, (uid,))

        return cursor.fetchone()

    except Exception as e:
        print("Error al obtener tarjeta:", e)
        return None

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def existe_tarjeta(uid):
    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            SELECT id_tarjeta
            FROM tarjetas_nfc
            WHERE uid = %s
        """

        cursor.execute(sql, (uid,))

        tarjeta = cursor.fetchone()

        return tarjeta is not None

    except Exception as e:
        print("Error al buscar tarjeta:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def validar_pin(uid, pin):
    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        pin_hash = hashlib.sha256(
            pin.encode("utf-8")
        ).hexdigest()

        cursor = conexion.cursor()

        sql = """
            SELECT id_tarjeta
            FROM tarjetas_nfc
            WHERE uid = %s
            AND pin_hash = %s
        """

        cursor.execute(
            sql,
            (uid, pin_hash)
        )

        tarjeta = cursor.fetchone()

        return tarjeta is not None

    except Exception as e:
        print("Error al validar PIN:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def descontar_saldo(uid, monto):
    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE tarjetas_nfc
            SET saldo = saldo - %s
            WHERE uid = %s
            AND saldo >= %s
        """

        cursor.execute(
            sql,
            (monto, uid, monto)
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al actualizar saldo:", e)
        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()

"""
============================================

Separar funciones de aqui en procesar_pago.py

============================================
"""