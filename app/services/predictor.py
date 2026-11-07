import joblib
import os
import re
import pandas as pd

# Encontrar la ruta absoluta a la carpeta 'models'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
models_dir = os.path.join(project_root, 'models')

ruta_modelo = os.path.join(models_dir, 'best_model.pkl')
ruta_vectorizer = os.path.join(models_dir, 'vectorizer.pkl')

print(f"Buscando modelo en: {ruta_modelo}")

if not os.path.exists(ruta_modelo) or not os.path.exists(ruta_vectorizer):
    raise FileNotFoundError("No se encontraron los archivos del modelo (.pkl). Ejecuta primero: python scripts/train_pipeline.py")

print("Cargando modelo en memoria...")
modelo = joblib.load(ruta_modelo)
vectorizer = joblib.load(ruta_vectorizer)
print("Modelo cargado exitosamente.")

# MAPEO DE CLASES (Ajusta los nombres si el dataset usa otros)
# Basado en el dataset colombiano de ciberacoso estándar:
CLASES = {
    0: "Normal",
    1: "Insulto",
    2: "Amenaza",
    3: "Acoso",
    4: "Discriminación"
}

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\@\w+|\#', '', texto)
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\b\d+\b', '', texto)
    return re.sub(r'\s+', ' ', texto).strip()

def predecir_ciberacoso(texto):
    texto_limpio = limpiar_texto(texto)
    texto_vectorizado = vectorizer.transform([texto_limpio])
    
    # Predecir la clase (0, 1, 2, 3 o 4)
    prediccion = int(modelo.predict(texto_vectorizado)[0])
    probabilidades = modelo.predict_proba(texto_vectorizado)[0]
    probabilidad = float(probabilidades[prediccion])
    
    # Obtener el nombre real de la categoría
    categoria = CLASES.get(prediccion, f"Desconocido ({prediccion})")
    
    return {
        'texto_limpio': texto_limpio,
        'categoria_detectada': categoria,
        'probabilidad': probabilidad
    }