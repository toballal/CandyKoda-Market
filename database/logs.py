from database.connection import conectar


def registrar_log(modulo, accion, descripcion=None, nivel="Informacion", conexion=None):
    """Guarda una traza y permite participar en una transacción existente."""
    propia = conexion is None
    db = conexion or conectar()
    if db is None:
        return False

    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO logs (modulo, nivel, accion, descripcion)
            VALUES (%s, %s, %s, %s)
            """,
            (modulo, nivel, accion, descripcion),
        )
        if propia:
            db.commit()
        return True
    except Exception as error:
        if propia:
            db.rollback()
        print("Error al registrar log:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        if propia:
            db.close()
