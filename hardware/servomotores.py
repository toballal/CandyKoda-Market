def enviar_entrega(
    arduino,
    id_dispensador,
    cantidad
):
    from time import monotonic

    print("=== ENVIAR ENTREGA ===")

    if arduino is None or not arduino.is_open:
        print("Arduino no está conectado")
        return False

    try:
        comando = f"{id_dispensador},{cantidad}\n"

        print("Comando preparado:", repr(comando))

        arduino.write(
            comando.encode("utf-8")
        )

        arduino.flush()

        print(
            "Comando enviado:",
            comando.strip()
        )

        limite = monotonic() + 25
        while monotonic() < limite:

            linea = (
                arduino.readline()
                .decode("utf-8")
                .strip()
            )

            if not linea:
                continue

            print("Arduino respuesta:", linea)

            if linea.startswith("ENTREGADO:"):
                print("Dulce entregado")

            elif linea.startswith("REINTENTO:"):
                print("Reintentando dispensación")

            elif linea.startswith("COMPLETADO:"):
                print(
                    "Entrega completada correctamente"
                )
                return True

            elif linea.startswith("ERROR:"):
                print(
                    "Falló el dispensador:",
                    linea
                )
                return False

        print("Tiempo de espera agotado para el dispensador")
        return False

    except Exception as e:
        print(
            "Error enviando entrega:",
            e
        )
        return False
