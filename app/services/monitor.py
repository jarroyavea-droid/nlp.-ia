import time
from datetime import datetime
from app.services.instagram_service import InstagramService
from app.services.predictor import predecir_ciberacoso

class CyberbullyingMonitor:
    RESPONSES = {
        "high": "Tu comentario ha sido ocultado por violar nuestras normas de comunidad.",
        "medium": "Por favor, mantén un lenguaje respetuoso.",
    }

    def __init__(self, instagram: InstagramService):
        self.instagram = instagram
        self._processed_comments = set()

    def scan_all_media(self):
        """Escanea todos los medios y retorna la lista de comentarios analizados."""
        print("\n[MONITOR] Escaneando medios de Instagram...")
        comentarios_analizados = []
        
        try:
            media_list = self.instagram.get_media()
            print(f"[MONITOR] Encontrados {len(media_list)} medios")

            for media in media_list:
                media_id = media["id"]
                print(f"[MONITOR] Procesando post: {media_id}")
                
                comments = self.instagram.get_comments(media_id)
                print(f"[MONITOR]   Comentarios encontrados: {len(comments)}")

                for comment in comments:
                    comment_id = comment["id"]
                    if comment_id in self._processed_comments:
                        print(f"[MONITOR]   Ya procesado, saltando: {comment_id}")
                        continue

                    text = comment.get("text", "")
                    if not text:
                        continue

                    try:
                        print(f"[MONITOR]   Analizando: {text[:50]}...")
                        resultado = predecir_ciberacoso(text)
                        categoria = resultado.get("categoria_detectada", "Normal")
                        probabilidad = resultado.get("probabilidad", 0.0)
                        
                        print(f"[MONITOR]   Resultado: {categoria} ({probabilidad*100:.1f}%)")
                        
                        comentarios_analizados.append({
                            "text": text,
                            "categoria": categoria,
                            "probabilidad": probabilidad,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "action": None
                        })
                        
                        action = self._handle_prediction(comment_id, categoria, probabilidad, text)
                        comentarios_analizados[-1]["action"] = action
                        
                    except Exception as e:
                        print(f"[MONITOR]   ERROR al predecir: {e}")
                        continue

                    self._processed_comments.add(comment_id)
                    
        except Exception as e:
            print(f"[MONITOR] ERROR en escaneo: {e}")
        
        print(f"[MONITOR] Total analizados: {len(comentarios_analizados)}")
        return comentarios_analizados

    def _handle_prediction(self, comment_id, categoria, probabilidad, text):
        """Toma acción según el resultado."""
        es_malo = categoria.lower() not in ["normal", "limpio"]

        if es_malo and probabilidad > 0.7:
            print(f"[MONITOR]   ALERTA: {categoria} - OCULTANDO")
            try:
                self.instagram.hide_comment(comment_id)
                self.instagram.reply_to_comment(comment_id, self.RESPONSES["high"])
                return "ocultado"
            except Exception as e:
                print(f"[MONITOR]   ERROR al ocultar: {e}")
                return "error"
                
        elif es_malo and probabilidad > 0.5:
            print(f"[MONITOR]   ADVERTENCIA: {categoria}")
            try:
                self.instagram.reply_to_comment(comment_id, self.RESPONSES["medium"])
                return "advertencia"
            except Exception as e:
                print(f"[MONITOR]   ERROR al advertir: {e}")
                return "error"
        else:
            return "ninguna"

    def run_loop(self, interval: int = 60):
        """Loop continuo."""
        print(f"\n[MONITOR] Iniciando monitoreo cada {interval}s...")
        while True:
            try:
                self.scan_all_media()
                print(f"[MONITOR] Esperando {interval}s...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[MONITOR] Detenido por usuario")
                break
            except Exception as e:
                print(f"[MONITOR] Error: {e}")
                time.sleep(interval)