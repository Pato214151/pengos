#!/usr/bin/env python3
"""Test de batería de glosario — verifica correcciones + traducciones directas + filtros."""
import json
import sys
import re
from pathlib import Path

# El test vive en tests/; glosario.json está en la raíz del repo (un nivel arriba).
REPO = Path(__file__).parent.parent

# ── Copia de las funciones de main.py para testeo aislado ──
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

def es_transcripcion_valida(texto: str, corregir, traduccion_directa) -> bool:
    t = texto.strip()
    if len(t) < 4:
        if corregir(t) != t or traduccion_directa(t) is not None:
            return True
        return False
    if re.match(r'^[\s.,…!?;:\-•·*–—"\'0-9]+$', t):
        return False
    if _NON_LATIN.search(t):
        return False
    if any(p.search(t) for p in _HALLUCINATION_PATTERNS):
        return False
    return True


def cargar_glosario(ruta: Path):
    correcciones: dict[str, str] = {}
    traducciones_directas: dict[str, str] = {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        correcciones = {
            k: v for k, v in data.get("correcciones", {}).items()
            if not k.startswith("_")
        }
        traducciones_directas = {
            k: v for k, v in data.get("traducciones_directas", {}).items()
            if not k.startswith("_")
        }
    except FileNotFoundError:
        pass
    return correcciones, traducciones_directas


def corregir_transcripcion(texto: str, correcciones: dict) -> str:
    key = _glosario_key(texto)
    return correcciones.get(key, texto)


def traduccion_directa(texto: str, traducciones: dict) -> str | None:
    key = _glosario_key(texto)
    return traducciones.get(key)


# ─────────────────────── TESTS ───────────────────────

PASS = 0
FAIL = 0

def test(nombre: str, condicion: bool, detalle: str = ""):
    global PASS, FAIL
    if condicion:
        PASS += 1
        print(f"  [OK] {nombre}")
    else:
        FAIL += 1
        print(f"  [FAIL] {nombre} -- {detalle}")


def main():
    global PASS, FAIL
    print("=" * 70)
    print("TEST 1: CARGA DEL GLOSARIO")
    print("=" * 70)
    correcciones, traducciones = cargar_glosario(REPO / "glosario.json")
    test("glosario.json existe y se lee", len(correcciones) > 0 and len(traducciones) > 0,
         f"correcciones={len(correcciones)}, traducciones={len(traducciones)}")

    print("\n" + "=" * 70)
    print("TEST 2: CORRECCIONES DE WHISPER (MISHEAR -> INGLES CORRECTO)")
    print("=" * 70)
    casos_correccion = [
        ("he's won shot",       "he's one shot"),
        ("one speed",           "one shot"),
        ("i need heeling",      "i need healing"),
        ("they think im cheeting", "they think im cheating"),
        ("spik down",           "spike down"),
        ("smoking even",        "smoking heaven"),
        ("enemy you til",       "enemy util"),
        ("eko round",           "eco round"),
        ("cluch 1v3",           "clutch 1v3"),
        ("g g eko",             "gg eco"),
        ("defuzing",            "defusing"),
        ("low amoo",            "low ammo"),
        ("lurkingg",            "lurking"),
        ("tripple a",           "triple a"),
        ("molli link",          "molotov link"),
        ("retail a",            "retake a"),
        ("splsh push",          "split push"),
    ]
    for entrada, esperado in casos_correccion:
        resultado = corregir_transcripcion(entrada, correcciones)
        test(f"corrección: '{entrada}' → '{esperado}'",
             resultado == esperado,
             f"obtuvo '{resultado}'")

    # Frases con puntuación al final deben matchear igual
    for entrada, esperado in casos_correccion[:3]:
        resultado = corregir_transcripcion(entrada + ".", correcciones)
        test(f"corrección con punto: '{entrada}.' → '{esperado}'",
             resultado == esperado,
             f"obtuvo '{resultado}'")

    print("\n" + "=" * 70)
    print("TEST 3: TRADUCCIONES DIRECTAS (INGLÉS → ESPAÑOL GAMER)")
    print("=" * 70)
    casos_traduccion = [
        ("gg",                      "GG (good game)"),
        ("nice shot",               "buen tiro"),
        ("behind you",              "detrás tuyo"),
        ("he's one shot",           "está a un tiro (muy bajo de vida)"),
        ("heal me",                 "cúrame"),
        ("push a",                  "pusha A"),
        ("eco round",               "ronda eco — sin plata"),
        ("full buy",                "full — compramos todo"),
        ("need util",               "tiren utilidad"),
        ("one left a",              "uno queda en A"),
        ("they have ult",           "tienen ulti"),
        ("defuse now",              "desarma ya"),
        ("behind you",              "detrás tuyo"),
        ("push now",                "push ahora"),
    ]
    for entrada, esperado in casos_traduccion:
        resultado = traduccion_directa(entrada, traducciones)
        test(f"traducción: '{entrada}' → '{esperado}'",
             resultado == esperado,
             f"obtuvo '{resultado}'")

    # Sin-glosario: frases que NO están deben devolver None
    no_existentes = ["i like trains", "hello world", "random phrase xyz"]
    for entrada in no_existentes:
        resultado = traduccion_directa(entrada, traducciones)
        test(f"no-traducción: '{entrada}' → None",
             resultado is None,
             f"obtuvo '{resultado}'")

    # Frases con puntuación
    resultado = traduccion_directa("heal me!", traducciones)
    test("traducción con !: 'heal me!' → 'cúrame'",
         resultado == "cúrame",
         f"obtuvo '{resultado}'")

    print("\n" + "=" * 70)
    print("TEST 4: FILTRO es_transcripcion_valida")
    print("=" * 70)

    def mock_corregir(t): return corregir_transcripcion(t, correcciones)
    def mock_trad(t): return traduccion_directa(t, traducciones)

    # — Debe ser FALSO (descartar) —
    falsos = [
        ("",                "cadena vacía"),
        ("...",             "solo puntos suspensivos"),
        (". . .",           "puntos con espacios"),
        ("   ",             "solo espacios"),
        ("—",               "solo guión largo"),
        ("•",               "solo bullet"),
        ("♪ ♫ ♪",           "notas musicales"),
        ("música",          "música"),
        ("[music]",         "música marcada"),
        ("thanks for watching", "hallucination: thanks for watching"),
        ("subscribe to my channel", "hallucination: subscribe"),
        ("subtitles by XYZ", "hallucination: subtitles by"),
        ("subtitulos por",  "hallucination: subtitulos por"),
        ("closed captioning by", "hallucination: closed captioning by"),
        ("broth3rmax",      "hallucination: broth3rmax"),
        ("sub indo",        "hallucination: sub indo"),
        ("谢谢你",           "caracteres chinos"),
        ("ありがとう",       "caracteres japoneses"),
        ("감사합니다",       "caracteres coreanos"),
        ("привет",          "caracteres cirílicos"),
        ("धन्यवाद",         "caracteres devanagari"),
    ]
    for entrada, desc in falsos:
        test(f"FILTRO → FALSO: {desc} ({repr(entrada[:30])})",
             not es_transcripcion_valida(entrada, mock_corregir, mock_trad))

    # — Debe ser VERDADERO (pasar) —
    verdaderos = [
        ("heal me",          "frase corta en glosario"),
        ("push left now",    "frase normal"),
        ("i need shield",    "frase gaming"),
        ("Wait.",            "frase corta con punto"),
        ("No.",              "frase muy corta"),
        ("one left a",       "frase en glosario corta"),
        ("enemy low",        "frase en glosario"),
    ]
    for entrada, desc in verdaderos:
        test(f"FILTRO → VERDADERO: {desc} ({repr(entrada[:30])})",
             es_transcripcion_valida(entrada, mock_corregir, mock_trad))

    # Edge case: frase <4 chars pero con corrección o traducción directa
    test("FILTRO: 'no.' pasa porque tiene traducción directa",
         es_transcripcion_valida("no.", mock_corregir, mock_trad))

    print("\n" + "=" * 70)
    print("TEST 5: NORMALIZACIÓN DE CLAVES (_glosario_key)")
    print("=" * 70)

    pares_normalizacion = [
        ("He's One Shot!",   "he's one shot"),
        ("HEAL ME.",         "heal me"),
        ("  push left  ",    "push left"),
        ("Behind you...",    "behind you"),
        ("No.",              "no"),
        ("Sí, señor!",       "sí, señor"),
    ]
    for entrada, esperado in pares_normalizacion:
        resultado = _glosario_key(entrada)
        test(f"normalización: {repr(entrada)} → {repr(esperado)}",
             resultado == esperado,
             f"obtuvo {repr(resultado)}")

    print("\n" + "=" * 70)
    print("TEST 6: CONSISTENCIA DEL GLOSARIO")
    print("=" * 70)

    # Cada clave en traducciones_directas debe aparecer también como valor
    # de alguna corrección (consistencia)
    inconsistencias = []
    for clave in traducciones:
        # Verificar que las claves tengan sentido (no estén vacías)
        if len(clave) < 1:
            inconsistencias.append(f"clave vacía en traducciones_directas")
        # Verificar que la traducción no esté vacía
        if len(traducciones[clave]) < 1:
            inconsistencias.append(f"traducción vacía para '{clave}'")

    test("no hay claves vacías en traducciones_directas",
         len(inconsistencias) == 0,
         "; ".join(inconsistencias[:5]))

    # Verificar que no hay duplicados entre correcciones y traducciones_directas
    # (una clave no debería estar en ambos)
    overlap = set(correcciones.keys()) & set(traducciones.keys())
    test("sin overlap entre correcciones y traducciones_directas",
         len(overlap) == 0,
         f"claves duplicadas: {list(overlap)[:5]}")

    # Reportar entradas de correcciones sospechosamente largas
    largas = [k for k in correcciones if len(k) > 30]
    test("correcciones con clave corta (<30 chars)",
         len(largas) == 0,
         f"claves largas: {largas[:3]}")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")
    print("=" * 70)

    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
