# Detector de ciberacoso (NLP + ML + RoBERTuito) — modelo de detección

Detector de ciberacoso en español colombiano y lenguaje de redes sociales.
Este repositorio contiene **sólo el modelo de detección** (sin bots de Discord
ni Bluesky): la normalización de texto, el modelo clásico entrenado, la
segunda opinión con RoBERTuito, los scripts de entrenamiento y una API web.

## Categorías

| Id | Categoría |
|----|-----------|
| 0 | Sin ciberacoso |
| 1 | Hostigamiento y amenazas directas |
| 2 | Insultos y ofensas personales |
| 3 | Incitación al odio y muerte |
| 4 | Difamación, calumnia y ataques políticos |

## Cómo funciona

1. **Normalización** (`src/preprocessing.py`): jerga colombiana, leetspeak,
   emojis, alargamientos y risas.
2. **Modelo clásico en dos etapas** (`src/train.py`): TF-IDF de palabras y de
   caracteres + 9 rasgos léxicos (`src/features.py`).
   - Etapa 1: ¿es ciberacoso? (logreg_C5, umbral 0.42)
   - Etapa 2: ¿qué categoría? (svm_calibrada)
3. **Cascada** (`src/predict.py`): si el clásico duda, consulta a RoBERTuito
   (`src/transformer.py`) y fusiona las probabilidades.
4. **Acción sugerida**: `PERMITIR_MENSAJE`, `SANCIONAR` o `REVISAR_POR_ADMIN`.

## Métricas del modelo incluido (entrenado 2026-11-24)

| Etapa | Métrica | Valor |
|-------|---------|-------|
| Binaria | F1 ciberacoso | 0.827 |
| Binaria | Precisión / Recall | 0.778 / 0.883 |
| Binaria | F1 sólo datos colombianos | 0.766 |
| Categorías | F1 macro | 0.910 |

Detalle completo en `models/classic_metrics.json`.

## Estructura

```
main.py                       consola y comandos (train, train-roberta, audit, traducir)
app/                          menú de consola y adaptador (app/services/predictor.py) para la API
models/classic_model.joblib   modelo clásico entrenado
models/classic_metrics.json   métricas de validación
src/preprocessing.py          normalización de texto
src/features.py               rasgos léxicos
src/predict.py                CyberbullyingDetector (cascada clásico -> RoBERTa)
src/transformer.py            RoBERTuito (fine-tuned o zero-shot)
src/data.py                   carga y unificación de datasets
src/train.py                  entrenamiento del modelo clásico
src/train_transformer.py      fine-tuning de RoBERTuito
src/label_audit.py            auditoría de etiquetas
src/translate_english.py      traducción de datasets en inglés
src/config.py                 rutas, categorías y umbrales
data/raw/                     datasets de entrenamiento
tests/                        pruebas (pytest)
```

## Instalación

```bash
pip install -r requirements.txt
```

`torch` y `transformers` son opcionales. Sin ellos (o con `--sin-roberta`) se
usa sólo el modelo clásico. Si no existe `models/roberta_finetuned/`,
RoBERTuito funciona en modo *zero-shot* con
`pysentimiento/robertuito-hate-speech`.

## Uso

```bash
python main.py                    # consola interactiva
python main.py cli --sin-roberta  # sólo modelo clásico
python main.py train              # reentrena el modelo clásico
python main.py train-roberta      # fine-tuning de RoBERTuito (necesita GPU idealmente)
python -m pytest tests            # pruebas
```

Desde código:

```python
from src.predict import CyberbullyingDetector

detector = CyberbullyingDetector(use_roberta=False)
r = detector.predict('S4P4 HIJ0 D3 PUT4')
print(r['categoria_nombre'], r['confianza'], r['accion_sugerida'])
```

> `src/features.py` y `src/preprocessing.py` deben conservar esos nombres:
> el `.joblib` los referencia al cargarse.
