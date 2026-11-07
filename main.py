"""Detector de ciberacoso — consola de pruebas.

    python main.py                 consola interactiva (clásico + RoBERTa)
    python main.py --sin-roberta   consola sólo con el modelo clásico
    python main.py "texto"         analiza un mensaje y sale
"""

import argparse
import sys


def run_interactive_cli(use_roberta: bool):
  from src.predict import CyberbullyingDetector

  print('=' * 65)
  print('   DETECTOR DE CIBERACOSO (NLP + ML + RoBERTa) - CONSOLA')
  print('=' * 65)
  print('Cargando modelos...')
  try:
    detector = CyberbullyingDetector(use_roberta=use_roberta)
    detector.warmup()
  except Exception as e:
    print(f' Error al cargar el detector: {e}')
    sys.exit(1)
  print(f' Modelos cargados. RoBERTa: {detector.roberta_mode}')
  print("\nEscribe un texto para analizarlo ('salir' para terminar).")

  while True:
    try:
      user_input = input('\n Mensaje > ').strip()
    except (KeyboardInterrupt, EOFError):
      print('\nSaliendo...')
      break
    if not user_input:
      continue
    if user_input.lower() in ('salir', 'exit', 'quit'):
      break

    r = detector.predict(user_input)
    print('─' * 60)
    print(f' Preprocesado      : "{r["texto_limpio"]}"')
    if r['es_ciberacoso']:
      print(' DIAGNÓSTICO       : [ POSIBLE CIBERACOSO ]')
      print(f' CATEGORÍA         : {r["categoria"]} - {r["categoria_nombre"]}')
    else:
      print(' DIAGNÓSTICO       : [ MENSAJE SEGURO ]')
    print(f' CONFIANZA         : {r["confianza"] * 100:.2f}%')
    print(f' MOTOR             : {r["motor"]}')
    print(f' P(acoso) clásico  : {r["prob_clasico"]}   RoBERTa: {r["prob_roberta"]}')
    print(' DISTRIBUCIÓN 0-4  : ' + '  '.join(
        f'{c}:{p:.2f}' for c, p in r['probabilidades'].items()))
    if r['motivos_sospecha']:
      print(' SOSPECHAS         : ' + '; '.join(r['motivos_sospecha']))
    print(f' ACCIÓN SUGERIDA   : {r["accion_sugerida"]}')
    print('─' * 60)


def main():
  parser = argparse.ArgumentParser(description='Detector de ciberacoso')
  parser.add_argument('texto', nargs='*', help='Mensaje a analizar (opcional)')
  parser.add_argument('--sin-roberta', action='store_true',
                      help='Usar sólo el modelo clásico')
  parser.add_argument('--json', action='store_true',
                      help='Imprimir el resultado completo en JSON')
  args = parser.parse_args()

  if args.texto:
    import json
    from src.predict import CyberbullyingDetector

    detector = CyberbullyingDetector(use_roberta=not args.sin_roberta)
    detector.warmup()
    r = detector.predict(' '.join(args.texto))
    if args.json:
      print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
      print(f'{r["categoria_nombre"]} | confianza {r["confianza"]:.2f} | '
            f'{r["accion_sugerida"]} | motor {r["motor"]}')
    return

  run_interactive_cli(use_roberta=not args.sin_roberta)


if __name__ == '__main__':
  main()
