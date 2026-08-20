import os

import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("CANDYKODA_DB_HOST", "192.168.100.15"),
            port=int(os.getenv("CANDYKODA_DB_PORT", "3306")),
            user=os.getenv("CANDYKODA_DB_USER", "market"),
            password=os.getenv("CANDYKODA_DB_PASSWORD", "candykoda1234"),
            database=os.getenv("CANDYKODA_DB_NAME", "candy_koda"),
            charset="utf8mb4",
            autocommit=False,
        )

        return conexion
    except Exception as e:
        print("No se pudo conectar a la base de datos:", e)

def verificar_conexion():
    conexion = conectar()

    if conexion is None:
        return  False

    try:
        return conexion.is_connected()

    except Exception as e:
        print("Error al verificar la base de datos:", e)
        return False

    finally:
        conexion.close()

