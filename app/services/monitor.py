import time
from app.services.instagram_service import InstagramService
from app.services.predictor import predecir_ciberacoso

class CyberbullyingMonitor:
    RESPONSES = {
        "high": " Tu comentario ha sido ocultado por violar nuestras normas de comunidad.",
        "medium": " Por favor, mantén un lenguaje respetuoso.",
    }

    def __init__(self, instagram: InstagramService):
        self.instagram = instagram
        self._processed_comments = set()

    def scan_all_media(self):
        print("\n Escaneando medios de Instagram...")
        try:
            media_list = self.instagram.get_media()
            print(f" Encontrados {len(media_list)} medios para escanear")

            for media in media_list:
                media_id = media["id"]
                comments = self.instagram.get_comments(media_id)
                print(f"    Post {media_id}: {len(comments)} comentarios")

                for comment in comments:
                    comment_id = comment["id"]
                    if comment_id in self._processed_comments:
                        continue

                    text = comment.get("text", "")
                    if not text:
                        continue

                    try:
                        resultado = predecir_ciberacoso(text)
                        categoria = resultado.get("categoria_detectada", "normal")
                        probabilidad = resultado.get("probabilidad", 0.0)
                    except Exception as e:
                        print(f"    Error al predecir: {e}")
                        continue

                    self._handle_prediction(comment_id, categoria, probabilidad, text)
                    self._processed_comments.add(comment_id)
        except Exception as e:
            print(f" Error en escaneo: {e}")

    def _handle_prediction(self, comment_id, categoria, probabilidad, text):
    es_malo = "amenaza" in categoria.lower() or "insulto" in categoria.lower() or "ofensa" in categoria.lower()

        if es_malo and probabilidad > 0.8:
            print(f"    GROSERÍA DETECTADA ({probabilidad*100:.1f}%): {text[:50]}")
            try:
                self.instagram.hide_comment(comment_id)
                self.instagram.reply_to_comment(comment_id, self.RESPONSES["high"])
                print("       Comentario ocultado y respuesta enviada")
            except Exception as e:
                print(f"       Error al responder: {e}")
        elif es_malo and probabilidad > 0.5:
            print(f"    Posible grosería ({probabilidad*100:.1f}%): {text[:50]}")
            try:
                self.instagram.reply_to_comment(comment_id, self.RESPONSES["medium"])
                print("       Respuesta de advertencia enviada")
            except Exception as e:
                print(f"       Error al responder: {e}")
        else:
            print(f"    Comentario limpio: {text[:50]}")

    def run_loop(self, interval: int = 60):
        print(f"\n Iniciando monitoreo cada {interval}s... (Presiona Ctrl+C para detener)")
        while True:
            try:
                self.scan_all_media()
                print(f"\n Próximo escaneo en {interval} segundos...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n Monitoreo detenido por el usuario.")
                break
            except Exception as e:
                print(f" Error en loop: {e}")
                time.sleep(interval)