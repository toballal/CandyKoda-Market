import asyncio
import edge_tts
import vlc
import os
import re
import uuid

instancia_vlc = vlc.Instance("--no-video", "--quiet")
player = instancia_vlc.media_player_new()


async def hablar(texto):
    archivo = f"voz_{uuid.uuid4().hex}.mp3"

    try:
        texto = re.sub(r"\$(\d+)", r"\1 pesos", texto)

        communicate = edge_tts.Communicate(
            texto,
            "es-CL-CatalinaNeural",
        )

        await communicate.save(archivo)

        media = instancia_vlc.media_new(archivo)
        player.set_media(media)
        player.play()

        await asyncio.sleep(0.15)

        while player.get_state() not in (
            vlc.State.Ended,
            vlc.State.Stopped,
            vlc.State.Error,
        ):
            await asyncio.sleep(0.05)

    except Exception as error:
        print(f"Error al reproducir la voz: {error}")

    finally:
        player.stop()
        player.set_media(None)

        await asyncio.sleep(0.05)

        if os.path.exists(archivo):
            try:
                os.remove(archivo)
            except PermissionError:
                pass