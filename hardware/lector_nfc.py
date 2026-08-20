def leer_tarjeta(arduino):

    if arduino is None or not arduino.is_open:
        return None

    try:
        if arduino.in_waiting > 0:

            linea = (
                arduino.readline()
                .decode("utf-8")
                .strip()
            )

            if linea.startswith("NFC:"):
                uid = (
                    linea
                    .replace("NFC:", "")
                    .strip()
                    .upper()
                )

                return uid

        return None

    except Exception as e:
        print("Error leyendo Arduino:", e)
        return None
