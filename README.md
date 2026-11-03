# Detector de ciberacoso (NLP + ML + RoBERTa) — sólo el modelo

Versión reducida del proyecto: contiene únicamente el modelo ya entrenado y
la lógica de detección. Sin bots de Discord ni Bluesky, sin datasets ni
scripts de entrenamiento.

## Categorías

| Id | Categoría |
|----|-----------|
| 0 | Sin ciberacoso |
| 1 | Hostigamiento y amenazas directas |
| 2 | Insultos y ofensas personales |
| 3 | Incitación al odio y muerte |
| 4 | Difamación, calumnia y ataques políticos |

## Estructura

```
main.py                     consola de pruebas
models/classic_model.joblib modelo clásico entrenado (TF-IDF + rasgos léxicos)
models/classic_metrics.json métricas de validación
src/preprocessing.py        normalización (jerga colombiana, leetspeak, emojis)
src/features.py             rasgos léxicos (insultos, amenazas, odio)
src/predict.py              CyberbullyingDetector (cascada clásico -> RoBERTa)
src/transformer.py          RoBERTuito como segunda opinión (opcional)
src/config.py               rutas, categorías y umbrales
```

> `src/features.py` y `src/preprocessing.py` deben quedarse con esos nombres:
> el `.joblib` los referencia al cargarse.

## Instalación

```bash
pip install -r requirements.txt
```

`torch` y `transformers` son opcionales. Sin ellos (o con `--sin-roberta`)
se usa sólo el modelo clásico. Con ellos, como no se incluye
`models/roberta_finetuned/`, RoBERTa funciona en modo *zero-shot* y descarga
`pysentimiento/robertuito-hate-speech` la primera vez.

## Uso

```bash
python main.py                         # consola interactiva
python main.py --sin-roberta           # sólo modelo clásico
python main.py "eres un inútil"        # analiza un mensaje y sale
python main.py --json "eres un inútil" # resultado completo en JSON
```

Desde código:

```python
from src.predict import CyberbullyingDetector

detector = CyberbullyingDetector(use_roberta=False)
r = detector.predict('S4P4 HIJ0 D3 PUT4')
print(r['categoria_nombre'], r['confianza'], r['accion_sugerida'])
# Insultos y ofensas personales 0.8954 SANCIONAR
```

`predict()` devuelve un diccionario con `es_ciberacoso`, `categoria`,
`categoria_nombre`, `confianza`, `probabilidades` (0-4), `motor`,
`motivos_sospecha` y `accion_sugerida`
(`SANCIONAR` | `REVISAR_POR_ADMIN` | `PERMITIR_MENSAJE`).
Para muchos textos a la vez: `detector.predict_classic_batch(lista)`.
