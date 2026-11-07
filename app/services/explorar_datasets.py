import pandas as pd
import os

# Ruta a la carpeta de datasets
ruta = 'data/raw'

# Lista de archivos CSV
archivos = [
    'CorpusBullying.csv',
    'colombian_cyberbullying.csv',
    'twitter_racism_parsed_dataset.csv',
    'twitter_sexism_parsed_dataset.csv',
    'youtube_parsed_dataset.csv'
]

print("=" * 60)
print("EXPLORACIÓN DE DATASETS")
print("=" * 60)

for archivo in archivos:
    ruta_completa = os.path.join(ruta, archivo)
    
    if os.path.exists(ruta_completa):
        print(f"\n {archivo}")
        print("-" * 60)
        
        try:
            # Intentar leer con diferentes separadores
            try:
                df = pd.read_csv(ruta_completa, encoding='utf-8')
            except:
                df = pd.read_csv(ruta_completa, encoding='latin-1')
            
            print(f"Filas: {len(df)}")
            print(f"Columnas: {list(df.columns)}")
            print(f"\nPrimeras 3 filas:")
            print(df.head(3))
            print(f"\nDistribución de clases:")
            # Intentar encontrar la columna de etiquetas
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].nunique() < 10:
                    print(f"  {col}: {df[col].value_counts().to_dict()}")
                    break
                    
        except Exception as e:
            print(f"Error al leer: {e}")
    else:
        print(f"\n {archivo} no existe en {ruta_completa}")

print("\n" + "=" * 60)