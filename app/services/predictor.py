"""Adaptador entre la API (FastAPI) y el detector híbrido de src/.

Mantiene la función predecir_ciberacoso() que usa la app, pero ahora la
predicción la hace CyberbullyingDetector (modelo clásico + RoBERTuito).
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.predict import CyberbullyingDetector  # noqa: E402

_detector = None


def get_detector() -> CyberbullyingDetector:
  """Carga el modelo una sola vez (perezoso)."""
  global _detector
  if _detector is None:
    use_roberta = os.getenv('ROBERTA_ENABLED', '1') == '1'
    _detector = CyberbullyingDetector(use_roberta=use_roberta)
  return _detector


def predecir_ciberacoso(texto: str) -> dict:
  """Analiza un texto y devuelve categoría, confianza y acción sugerida."""
  r = get_detector().predict(texto)
  return {
      'texto_original': r['texto_original'],
      'texto_limpio': r['texto_limpio'],
      'es_ciberacoso': r['es_ciberacoso'],
      'categoria': r['categoria'],
      'categoria_detectada': r['categoria_nombre'],
      'probabilidad': r['confianza'],
      'accion_sugerida': r['accion_sugerida'],
      'motor': r['motor'],
  }


if __name__ == '__main__':
  for ejemplo in ['Ojalá te mueras y te pase lo peor', 'jajaja qué buena foto']:
    res = predecir_ciberacoso(ejemplo)
    print(f"{ejemplo!r} -> {res['categoria_detectada']} "
          f"({res['probabilidad']}) {res['accion_sugerida']}")
