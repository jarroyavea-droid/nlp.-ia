import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.services.predictor import predecir_ciberacoso
from app.services.instagram_service import InstagramService
from app.services.monitor import CyberbullyingMonitor

# ==========================================
# CONFIGURACIÓN DE FASTAPI
# ==========================================
app = FastAPI(title="NLP-IA Detector de Ciberacoso")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Instancias globales
instagram = InstagramService()
monitor = CyberbullyingMonitor(instagram)

# Almacenamiento de logs en memoria
logs = []
MAX_LOGS = 50

# ==========================================
# MODELOS DE DATOS
# ==========================================
class TextRequest(BaseModel):
    text: str

# ==========================================
# RUTAS
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("app/static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: No se encontro index.html</h1>", status_code=404)

@app.post("/api/predict")
async def predict_text(request: TextRequest):
    try:
        resultado = predecir_ciberacoso(request.text)
        
        log_entry = {
            "text": request.text,
            "categoria": resultado["categoria_detectada"],
            "probabilidad": resultado["probabilidad"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "is_system": False
        }
        logs.append(log_entry)
        if len(logs) > MAX_LOGS:
            logs.pop(0)
        
        return resultado
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/scan-once")
async def scan_once():
    """Escanea Instagram y muestra CADA comentario individualmente."""
    global logs
    
    try:
        print("\n=== INICIANDO ESCANEO ===")
        
        # Ejecutar el escaneo
        resultados = monitor.scan_all_media()
        
        # Si no hay resultados
        if resultados is None or len(resultados) == 0:
            print("No se encontraron comentarios")
            return {
                "message": "Escaneo completado",
                "comments_analyzed": 0,
                "results": []
            }
        
        print(f"Se encontraron {len(resultados)} comentarios")
        
        # Agregar CADA comentario a los logs
        for i, comentario in enumerate(resultados):
            log_entry = {
                "text": comentario.get("text", "Sin texto"),
                "categoria": comentario.get("categoria", "Normal"),
                "probabilidad": float(comentario.get("probabilidad", 0.0)),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "action": comentario.get("action", "ninguna"),
                "is_system": False
            }
            logs.append(log_entry)
            print(f"  [{i+1}] Agregado: {log_entry['text'][:50]}... - {log_entry['categoria']}")
        
        # Agregar resumen
        resumen_log = {
            "text": f"Escaneo completado: {len(resultados)} comentarios analizados",
            "categoria": "Resumen",
            "probabilidad": 1.0,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "action": None,
            "is_system": True
        }
        logs.append(resumen_log)
        
        # Mantener solo los últimos 50
        if len(logs) > MAX_LOGS:
            logs[:] = logs[-MAX_LOGS:]
        
        print(f"Total logs en memoria: {len(logs)}")
        print("=== ESCANEO FINALIZADO ===\n")
        
        return {
            "message": "Escaneo completado",
            "comments_analyzed": len(resultados),
            "results": resultados,
            "total_logs": len(logs)
        }
    except Exception as e:
        print(f"ERROR en scan_once: {str(e)}")
        return {"error": str(e)}

@app.get("/api/logs")
async def get_logs():
    return logs[-20:]  # Últimos 20 logs

@app.post("/api/start-monitor")
async def start_monitor():
    import threading
    
    def run_monitor():
        try:
            monitor.run_loop(interval=60)
        except Exception as e:
            print(f"Error en monitoreo: {e}")
    
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    
    logs.append({
        "text": "Monitoreo iniciado correctamente",
        "categoria": "Exito",
        "probabilidad": 1.0,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "is_system": True
    })
    
    return {"message": "Monitoreo iniciado", "interval": 60}

@app.post("/api/stop-monitor")
async def stop_monitor():
    logs.append({
        "text": "Monitoreo detenido por el usuario",
        "categoria": "Advertencia",
        "probabilidad": 1.0,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "is_system": True
    })
    return {"message": "Monitoreo detenido"}

# ==========================================
# INICIO
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)