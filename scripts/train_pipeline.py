import pandas as pd
import numpy as np
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

def limpiar_texto(texto):
    """Limpia el texto para el modelo."""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    # Quitar URLs
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
    # Quitar menciones (@usuario) y hashtags (#)
    texto = re.sub(r'\@\w+|\#', '', texto)
    # Quitar emojis, signos de puntuación y caracteres especiales (mantener solo letras, números y espacios)
    texto = re.sub(r'[^\w\s]', '', texto)
    # Quitar números sueltos (opcional, a veces ayudan, pero a veces hacen ruido)
    texto = re.sub(r'\b\d+\b', '', texto)
    # Quitar espacios extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def cargar_todos_los_datasets():
    """Carga y unifica todos los datasets con sus configuraciones específicas."""
    dataframes = []
    
    # Configuración de cada dataset: (ruta, separador, columna_texto, columna_label)
    configuraciones = [
        {
            'ruta': 'data/raw/colombian_cyberbullying.csv',
            'sep': ',',
            'text_col': 'texto',
            'label_col': 'ciberacoso'
        },
        {
            'ruta': 'data/raw/CorpusBullying.csv',
            'sep': ';',  # ¡Este usa punto y coma!
            'text_col': 'SpanishTweet',
            'label_col': 'Label'
        },
        {
            'ruta': 'data/raw/twitter_racism_parsed_dataset.csv',
            'sep': ',',
            'text_col': 'Text',
            'label_col': 'oh_label'
        },
        {
            'ruta': 'data/raw/twitter_sexism_parsed_dataset.csv',
            'sep': ',',
            'text_col': 'Text',
            'label_col': 'oh_label'
        },
        {
            'ruta': 'data/raw/youtube_parsed_dataset.csv',
            'sep': ',',
            'text_col': 'Text',
            'label_col': 'oh_label'
        }
    ]
    
    print("\nCargando datasets...")
    for config in configuraciones:
        ruta = config['ruta']
        if not os.path.exists(ruta):
            print(f"   No encontrado: {ruta}")
            continue
            
        try:
            # Intentar cargar con diferentes codificaciones
            try:
                df = pd.read_csv(ruta, sep=config['sep'], encoding='utf-8')
            except:
                df = pd.read_csv(ruta, sep=config['sep'], encoding='latin-1')
            
            # Verificar que las columnas existan
            if config['text_col'] in df.columns and config['label_col'] in df.columns:
                # Crear un dataframe unificado con nombres estándar
                df_unificado = pd.DataFrame()
                df_unificado['text'] = df[config['text_col']].astype(str)
                df_unificado['label'] = df[config['label_col']]
                
                # Asegurar que la etiqueta sea 0 o 1 (numérico)
                df_unificado['label'] = pd.to_numeric(df_unificado['label'], errors='coerce').fillna(0).astype(int)
                
                # Eliminar filas vacías o con etiqueta inválida
                df_unificado = df_unificado[df_unificado['text'].str.strip() != '']
                df_unificado = df_unificado[df_unificado['label'].isin([0, 1])]
                
                dataframes.append(df_unificado)
                print(f"   {os.path.basename(ruta)}: {len(df_unificado)} filas válidas")
            else:
                print(f"   Columnas no encontradas en {os.path.basename(ruta)}")
                
        except Exception as e:
            print(f"   Error al leer {os.path.basename(ruta)}: {e}")
    
    if len(dataframes) == 0:
        raise ValueError("No se pudo cargar ningún dataset válido.")
    
    # Combinar todos los dataframes en uno solo
    df_final = pd.concat(dataframes, ignore_index=True)
    
    print(f"\nTOTAL UNIFICADO: {len(df_final)} filas")
    print(f"Distribución de clases:")
    print(f"   - No tóxico (0): {len(df_final[df_final['label'] == 0])}")
    print(f"   - Tóxico (1): {len(df_final[df_final['label'] == 1])}")
    
    return df_final

def ejecutar_pipeline():
    print("\n" + "=" * 70)
    print("ENTRENAMIENTO DE MODELO DETECTOR DE CIBERACOSO (MULTI-DATASET)")
    print("=" * 70)
    
    # 1. Cargar datos
    df = cargar_todos_los_datasets()
    
    # 2. Limpiar textos
    print("\n🧹 Limpiando textos (esto puede tardar un poco)...")
    df['text_limpio'] = df['text'].apply(limpiar_texto)
    
    # Filtrar textos demasiado cortos (menos de 3 caracteres)
    df = df[df['text_limpio'].str.len() >= 3]
    print(f"  Después de filtrar textos cortos: {len(df)} filas")
    
    # 3. Dividir en entrenamiento y prueba
    print("\nDividiendo datos (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['text_limpio'],
        df['label'],
        test_size=0.2,
        random_state=42,
        stratify=df['label'] # Mantiene la proporción de clases
    )
    
    print(f"   Entrenamiento: {len(X_train)} muestras")
    print(f"   Prueba: {len(X_test)} muestras")
    
    # 4. Crear pipeline: TF-IDF + SVM
    print("\nCreando pipeline (TF-IDF + SVM)...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=15000,      # Máximo de palabras a considerar
            ngram_range=(1, 2),      # Unigramas y bigramas (ej: "no me gusta")
            min_df=5,                # Ignorar palabras que aparecen en menos de 5 documentos
            max_df=0.8,              # Ignorar palabras que aparecen en más del 80% de documentos
            sublinear_tf=True        # Escalado logarítmico de frecuencia
        )),
        ('svm', SVC(
            kernel='linear',         # Kernel lineal funciona mejor para texto
            C=1.0,                   # Parámetro de regularización
            probability=True,        # Necesario para predecir probabilidades
            random_state=42,
            class_weight='balanced'  # Compensa si hay más ejemplos de una clase que de otra
        ))
    ])
    
    # 5. Entrenar
    print("\nEntrenando modelo...")
    pipeline.fit(X_train, y_train)
    
    # 6. Evaluar
    print("\nEvaluando modelo...")
    y_pred = pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'=' * 70}")
    print(f"ACCURACY GLOBAL: {accuracy * 100:.2f}%")
    print(f"{'=' * 70}")
    
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=['No Tóxico (0)', 'Tóxico (1)']))
    
    print("Matriz de confusión:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print("   [Verdaderos Negativos,  Falsos Positivos]")
    print("   [Falsos Negativos,      Verdaderos Positivos]")
    
    # 7. Guardar modelo
    print("\nGuardando modelo en la carpeta 'models/'...")
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(pipeline.named_steps['tfidf'], 'models/vectorizer.pkl')
    joblib.dump(pipeline.named_steps['svm'], 'models/best_model.pkl')
    
    print("Modelo guardado exitosamente.")
    
    # 8. Prueba rápida en vivo
    print("\n" + "=" * 70)
    print("PRUEBA RÁPIDA CON TEXTOS DE EJEMPLO")
    print("=" * 70)
    
    textos_prueba = [
        "Parce soltame ya deja tu sapa hijueputa envidia",
        "Qué linda foto me encanta mucho",
        "Eres un idiota no sirves para nada",
        "Te odio vete a la mrd",
        "Hola cómo estás buen día para todos"
    ]
    
    for texto in textos_prueba:
        texto_limpio = limpiar_texto(texto)
        prediccion = pipeline.predict([texto_limpio])[0]
        # Obtenemos la probabilidad de la clase predicha
        probas = pipeline.predict_proba([texto_limpio])[0]
        probabilidad = probas[prediccion]
        
        etiqueta = " TÓXICO" if prediccion == 1 else " LIMPIO"
        print(f"\n   Texto: '{texto}'")
        print(f"   Resultado: {etiqueta} (confianza: {probabilidad*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print(" ENTRENAMIENTO COMPLETADO CON ÉXITO")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_pipeline()