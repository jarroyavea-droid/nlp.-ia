import uvicorn
from app.main import app

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO SERVIDOR WEB")
    print("=" * 60)
    print("\nAbre tu navegador en: http://localhost:8000")
    print("Desde tu celular (misma red Wi-Fi): http://TU-IP-LOCAL:8000")
    print("\nPresiona Ctrl+C para detener\n")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)