"""Pruebas básicas del detector (sólo modelo clásico, sin RoBERTa)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.predict import CyberbullyingDetector  # noqa: E402
from src.preprocessing import clean_text  # noqa: E402

detector = CyberbullyingDetector(use_roberta=False)


def test_normaliza_leetspeak_y_jerga():
  assert clean_text('S4P4 HPT4') == 'sapo hijueputa'
  assert clean_text('mka') == 'marica'


def test_mensaje_neutro_se_permite():
  r = detector.predict('Hola a todos, ¿cómo van hoy?')
  assert r['accion_sugerida'] == 'PERMITIR_MENSAJE'


def test_risa_sola_no_es_acoso():
  r = detector.predict('jajajaja xd')
  assert not r['es_ciberacoso']


def test_insulto_ofuscado_se_detecta():
  r = detector.predict('S4P4 HIJ0 D3 PUT4')
  assert r['es_ciberacoso']
  assert r['categoria'] == 2


def test_amenaza_se_detecta():
  r = detector.predict('te voy a matar, sé dónde vives')
  assert r['es_ciberacoso']
