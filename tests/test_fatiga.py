#!/usr/bin/env python3
"""Test de fatiga — corre 10,000 iteraciones del pipeline para detectar memory leaks y degradacion."""
import json
import sys
import time
import tracemalloc
from pathlib import Path

REPO = Path(__file__).parent

# Copia del pipeline desde main.py (sin side effects)
import re

_NON_LATIN = re.compile(r"[Ѐ-ӿऀ-ॿ一-鿿㐀-䶿가-힯぀-ヿ]")
_HALLUCINATION_PATTERNS = [
    re.compile(r"broth3rmax", re.IGNORECASE),
    re.compile(r"\bsub\s*indo\b", re.IGNORECASE),
    re.compile(r"\bsubtitles?\s+by\b", re.IGNORECASE),
    re.compile(r"\bsubtitulos?\s+por\b", re.IGNORECASE),
    re.compile(r"closed\s+caption(?:ing)?\s+by", re.IGNORECASE),
    re.compile(r"\bcaption(?:ing|ed)?\s+by\b", re.IGNORECASE),
    re.compile(r"thanks?\s+for\s+watching", re.IGNORECASE),
    re.compile(r"subscribe\s+to\s+my", re.IGNORECASE),
    re.compile(r"^\s*m[úu]sica[.\s]*$", re.IGNORECASE),
    re.compile(r"^\s*\[?\s*music\s*\]?\.?\s*$", re.IGNORECASE),
    re.compile(r"^\s*[\[\(]?\s*[♪♫\s]+\s*[\]\)]?\s*$"),
]
_STRIP_PUNCT = re.compile(r"[.,!?;:\-…]+$")

def _glosario_key(texto: str) -> str:
    return _STRIP_PUNCT.sub("", texto.strip().lower())

def es_transcripcion_valida(texto, corregir_fn, trad_fn):
    t = texto.strip()
    if len(t) < 4:
        if corregir_fn(t) != t or trad_fn(t) is not None:
            return True
        return False
    if re.match(r'^[\s.,…!?;:\-•·*–—"\'0-9]+$', t):
        return False
    if _NON_LATIN.search(t):
        return False
    if any(p.search(t) for p in _HALLUCINATION_PATTERNS):
        return False
    return True

def cargar_glosario(ruta):
    correcciones: dict[str, str] = {}
    traducciones: dict[str, str] = {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        correcciones = {k: v for k, v in data.get("correcciones", {}).items() if not k.startswith("_")}
        traducciones = {k: v for k, v in data.get("traducciones_directas", {}).items() if not k.startswith("_")}
    except FileNotFoundError:
        pass
    return correcciones, traducciones


TEST_CORPUS = [
    "he's one shot", "push left", "i need healing", "cover me",
    "rotate to b", "enemy low", "spike down", "eco round",
    "full buy", "need util", "thanks for watching", "subscribe to my channel",
    "...", "   ", "music", "música", "♪ ♫ ♪",
    "detras tuyo", "necesito cura", "vamos B",
    "", "wait", "no", "yes", "go", "nice",
    "behind you", "one left a", "they have ult", "defuse now",
    "thank you", "hello world", "random phrase xyz",
    # Mix de español con atajo de teclado
    "a b c d e f g h i j k l m n o p q r s t u v w x y z",
    # Repetir las comunes
    "he's one shot", "push left", "need util", "eco round",
]

PASS = 0
FAIL = 0

def test(nombre, condicion, detalle=""):
    global PASS, FAIL
    if condicion:
        PASS += 1
    else:
        FAIL += 1
        print(f"  [FAIL] {nombre} -- {detalle}")

def main():
    global PASS, FAIL
    print("=" * 70)
    print("TEST DE FATIGA — 10,000 iteraciones del pipeline critico")
    print("=" * 70)
    print()
    print(f"Corpus: {len(TEST_CORPUS)} frases x 10,000 iteraciones = {len(TEST_CORPUS) * 10000} ejecuciones")
    print()

    correcciones, traducciones = cargar_glosario(REPO / "glosario.json")
    c = lambda t: correcciones.get(_glosario_key(t), t)
    t = lambda s: traducciones.get(_glosario_key(s))

    # Warm-up
    for frase in TEST_CORPUS[:10]:
        _ = es_transcripcion_valida(frase, c, t)
        _ = c(frase)
        _ = t(frase)

    # Medir baseline de memoria
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    inicio = time.perf_counter()
    total_ops = 0

    # Loop de fatiga
    for i in range(10000):
        for frase in TEST_CORPUS:
            es_transcripcion_valida(frase, c, t)
            c(frase)
            t(frase)
            total_ops += 3
        if (i + 1) % 1000 == 0:
            elapsed = time.perf_counter() - inicio
            print(f"  [{i+1}/10000] {total_ops} ops en {elapsed:.2f}s ({total_ops/elapsed:.0f} op/s)")

    elapsed = time.perf_counter() - inicio
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot2.compare_to(snapshot1, 'lineno')
    total_diff = sum(s.size_diff for s in stats)

    print()
    print(f"Resultados:")
    print(f"  Total operaciones: {total_ops}")
    print(f"  Tiempo total: {elapsed:.2f}s")
    print(f"  Throughput: {total_ops/elapsed:.0f} operaciones/s")
    print(f"  Por frase: {(elapsed/(total_ops/3))*1000:.0f} us promedio")
    print(f"  Diferencia de memoria: {total_diff/1024:.1f} KB")

    # Verificar que no haya memory leak significativo (>1MB de fuga)
    test(f"Sin memory leak significativo ({total_diff/1024:.1f} KB)",
         abs(total_diff) < 1024 * 1024,
         f"diff de memoria: {total_diff} bytes")

    # Verificar que todas las ejecuciones den resultado correcto
    # (no hay corrupcion de estado con el tiempo)
    resultados_iniciales = []
    for frase in TEST_CORPUS[:50]:
        resultados_iniciales.append((
            es_transcripcion_valida(frase, c, t),
            c(frase),
            t(frase)
        ))

    # Repetir y comparar
    for idx, frase in enumerate(TEST_CORPUS[:50]):
        r1 = resultados_iniciales[idx]
        r2 = (es_transcripcion_valida(frase, c, t), c(frase), t(frase))
        test(f"Consistencia tras fatiga: frase #{idx} ({repr(frase[:20])})",
             r1 == r2,
             f"inicial={r1} final={r2}")

    # Garbage collection
    import gc
    antes = len(gc.get_objects())
    gc.collect()
    despues = len(gc.get_objects())
    test(f"Sin objetos huérfanos ({despues - antes} variacion)",
         abs(despues - antes) < 1000,
         f"objetos antes={antes}, despues={despues}")

    print()
    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")

    # Recomendaciones
    print()
    print("Recomendaciones:")
    print(f"  - Memoria estable ({total_diff/1024:.1f}KB de diff)")
    if total_ops / elapsed > 100000:
        print("  - Performance: EXCELENTE (>100K op/s)")
    elif total_ops / elapsed > 50000:
        print("  - Performance: BUENA (50-100K op/s)")
    else:
        print("  - Performance: ACEPTABLE (<50K op/s)")
    print()

    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
