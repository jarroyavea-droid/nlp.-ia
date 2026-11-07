"""Configuración del detector (rutas del modelo, categorías y umbrales)."""

import os
from pathlib import Path

try:
  from dotenv import load_dotenv

  load_dotenv()
except ImportError:  # python-dotenv es opcional
  pass

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / 'models'

# Artefactos de modelos
CLASSIC_MODEL_PATH = MODELS_DIR / 'classic_model.joblib'
CLASSIC_METRICS_PATH = MODELS_DIR / 'classic_metrics.json'
ROBERTA_FINETUNED_DIR = MODELS_DIR / 'roberta_finetuned'

PRETRAINED_DIR = MODELS_DIR / 'pretrained'


def _local_or_hub(repo_id: str) -> str:
  """Usa la copia descargada en models/pretrained/ si está completa."""
  local = PRETRAINED_DIR / repo_id.split('/')[-1]
  return str(local) if (local / '.complete').exists() else repo_id


# Modelo de respaldo cuando no existe el fine-tuning propio
ROBERTA_ZERO_SHOT_MODEL = os.getenv(
    'ROBERTA_ZERO_SHOT_MODEL', _local_or_hub('pysentimiento/robertuito-hate-speech')
)
ROBERTA_ENABLED = os.getenv('ROBERTA_ENABLED', '1') == '1'
ROBERTA_MAX_LENGTH = 128

CATEGORIES = {
    0: 'Sin ciberacoso',
    1: 'Hostigamiento y amenazas directas',
    2: 'Insultos y ofensas personales',
    3: 'Incitación al odio y muerte',
    4: 'Difamación, calumnia y ataques políticos',
}
CATEGORY_SHORT = {
    0: 'Seguro',
    1: 'Amenaza',
    2: 'Insulto',
    3: 'Odio/Muerte',
    4: 'Calumnia',
}

# --- Cascada clásico -> RoBERTa ---
# Confianza mínima para sancionar automáticamente
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.70'))
# Banda alrededor del umbral binario donde el modelo clásico "duda"
UNCERTAINTY_MARGIN = float(os.getenv('UNCERTAINTY_MARGIN', '0.20'))
# F1 de validación por debajo del cual una clase se considera poco fiable
MIN_CLASS_F1 = float(os.getenv('MIN_CLASS_F1', '0.60'))
# Peso de RoBERTa al fusionar probabilidades
ROBERTA_WEIGHT = float(os.getenv('ROBERTA_WEIGHT', '0.70'))
