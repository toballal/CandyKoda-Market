import serial

def conectar_arduino():
    try:
        arduino = serial.Serial(
            "COM3",
            9600,
            timeout=1
        )

        print("Arduino conectado")

        return arduino

    except Exception as e:
        print("Error al conectar Arduino:", e)
        return None