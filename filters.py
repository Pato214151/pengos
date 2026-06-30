import re

from glosario import corregir_transcripcion, traduccion_directa

_NON_LATIN = re.compile(r"[Ѐ-ӿऀ-ॿ一-鿿㐀-䶿가-힯぀-ヿ]")

# Para rechazar CUALQUIER alfabeto no latino (árabe, hebreo, griego, tailandés,
# etc.) sin enumerar cada rango: si el texto no es mayoritariamente latino, es una
# alucinación de Whisper en este contexto EN/ES.
_LATIN_LETTER = re.compile(r"[A-Za-zÀ-ÿ]")          # latín básico + acentuado
_ANY_LETTER   = re.compile(r"[^\W\d_]", re.UNICODE)  # cualquier letra unicode
_LATIN_RATIO_MIN = 0.5

# ── Detección de idioma por texto ────────────────────────────────────────────

_ES_ACCENTED = re.compile(r"[áéíóúüñÁÉÍÓÚÜÑ]")

_ES_MARKERS: frozenset[str] = frozenset({
    # Artículos y determinantes
    "del", "los", "las", "una", "unos", "unas", "la", "lo",
    # Preposiciones y conjunciones
    "con", "para", "por", "desde", "hacia", "entre", "sobre",
    "que", "pero", "como", "cuando", "porque", "aunque", "sino",
    "también", "tampoco",
    # Demostrativos
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas",
    # Adverbios
    "ya", "mas", "muy", "bien", "asi", "aqui", "aca", "alla",
    "entonces", "ahora", "antes", "siempre", "nunca", "pues",
    # Formas verbales (inconfundibles en inglés)
    "hay", "habia", "tengo", "tiene", "tienen", "tenemos", "tenia",
    "estoy", "esta", "estan", "estaba",
    "puedo", "puede", "podemos", "pueden", "puedes",
    "quiero", "quiere", "queremos", "quieren",
    "voy", "vamos", "van",
    "hago", "hace", "hacemos", "hacen", "hice", "hizo",
    "soy", "eres", "somos", "son",
    "digo", "dice", "decimos",
    "miro", "mira", "vemos", "vengo", "viene", "vienen",
    "creo", "cree", "creemos",
    # Adjetivos comunes
    "bueno", "buena", "buenos", "buenas",
    "nuevo", "nueva", "nuevos", "nuevas",
    "todo", "toda", "todos", "todas",
    "otro", "otra", "otros", "otras",
    "mismo", "misma", "mismos", "mismas",
    "tranquilo", "tranquila",
    # Sustantivos comunes en gaming
    "equipo", "arma", "escudo", "muerto", "muertos",
    "bala", "balas", "equipo", "vida", "daño",
    # Verbos de gaming en español
    "curar", "curate", "revivir", "rotar", "matar",
    # Palabras de confirmación/callouts (muy frecuentes en el log)
    "dale", "listo", "sale", "vale", "claro",
    # Colombianismos y jerga del Discord
    "parcero", "parce", "chevere", "pato",
})

_HALLUCINATION_PATTERNS = [
    re.compile(r"broth3rmax", re.IGNORECASE),
    re.compile(r"\bsub\s*indo\b", re.IGNORECASE),
    re.compile(r"\bsubtitles?\s+by\b", re.IGNORECASE),
    re.compile(r"\bsubtitulos?\s+por\b", re.IGNORECASE),
    re.compile(r"closed\s+caption(?:ing)?\s+by", re.IGNORECASE),
    re.compile(r"\bcaption(?:ing|ed)?\s+by\b", re.IGNORECASE),
    re.compile(r"thanks?\s+for\s+watching", re.IGNORECASE),
    re.compile(r"subscribe\s+to\s+my", re.IGNORECASE),
    re.compile(r"\bsubscribe\s+for\s+more\b", re.IGNORECASE),
    re.compile(r"sous[-\s]titrage", re.IGNORECASE),
    re.compile(r"sous[-\s]titres?\s+(?:par|de|:)", re.IGNORECASE),
    re.compile(r"amara\.org", re.IGNORECASE),
    re.compile(r"\bcommunaut[ée]\s+d['e]amara\b", re.IGNORECASE),
    re.compile(r"radio[-\s]canada", re.IGNORECASE),
    re.compile(r"\bsociété\s+radio\b", re.IGNORECASE),
    re.compile(r"^\s*m[úu]sica[.\s]*$", re.IGNORECASE),
    re.compile(r"^\s*\[?\s*music\s*\]?\.?\s*$", re.IGNORECASE),
    re.compile(r"^\s*[\[\(]?\s*[♪♫\s]+\s*[\]\)]?\s*$"),
    # Whisper prompt self-hallucinations (echoes its own system prompt)
    re.compile(r"\bdo\s+not\s+translate\b", re.IGNORECASE),
    re.compile(r"\btranscribe\s+only\b", re.IGNORECASE),
    re.compile(r"\bspanish\s+or\s+english\b", re.IGNORECASE),
    re.compile(r"\bbilingual\s+gaming\b", re.IGNORECASE),
    re.compile(r"\bgaming\s+conversation\b", re.IGNORECASE),
    re.compile(r"\bgaming\s+voice\b", re.IGNORECASE),
    re.compile(r"\bspeaker\s+may\s+switch\b", re.IGNORECASE),
    # Echo de las listas de vocabulario del prompt (Whisper las transcribe en
    # silencios, empezando por el principio de la lista)
    re.compile(r"rush,\s*push,\s*peek", re.IGNORECASE),
    re.compile(r"push,\s*rush,\s*flankear", re.IGNORECASE),
    # Restos del prompt viejo en prosa (por si vuelve a aparecer)
    re.compile(r"\bcomunicaci[oó]n\s+en\s+partida\b", re.IGNORECASE),
    re.compile(r"\bfrases\s+cortas\b", re.IGNORECASE),
    # Whisper generating speaker labels from multi-speaker audio
    re.compile(r"^\s*speaker\s*[:\-]?\s*\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*\[speaker\s*\d+\]\s*$", re.IGNORECASE),
    # Common filler phrases Whisper hallucinates from background audio
    re.compile(r"^\s*thank\s+you\.?\s*$", re.IGNORECASE),
    re.compile(r"^\s*you\.?\s*$", re.IGNORECASE),
]


def detectar_idioma(texto: str) -> str:
    """Retorna 'es' si el texto es predominantemente español, 'en' si es inglés."""
    # Los acentos son el indicador más confiable — Whisper los agrega al español
    if _ES_ACCENTED.search(texto):
        return "es"
    # Si no hay acentos, buscar palabras marcadoras inconfundiblemente españolas
    palabras = re.findall(r"\b[a-z]+\b", texto.lower())
    if any(p in _ES_MARKERS for p in palabras):
        return "es"
    return "en"


def es_transcripcion_valida(texto: str) -> bool:
    t = texto.strip()
    if len(t) < 4:
        if corregir_transcripcion(t) != t or traduccion_directa(t) is not None:
            return True
        return False
    if re.match(r'^[\s.,…!?;:\-•·*–—"\'0-9]+$', t):
        return False
    if _NON_LATIN.search(t):
        return False
    # Rechazo general por alfabeto: si la mayoría de las letras NO son latinas
    # (árabe, hebreo, griego, tailandés…), es alucinación. Cubre lo que los rangos
    # de _NON_LATIN no listan explícitamente.
    letras = _ANY_LETTER.findall(t)
    if letras:
        latinas = len(_LATIN_LETTER.findall(t))
        if latinas / len(letras) < _LATIN_RATIO_MIN:
            return False
    if any(p.search(t) for p in _HALLUCINATION_PATTERNS):
        return False
    palabras = [w.strip(".,!?;:") for w in t.split() if w.strip(".,!?;:")]
    if len(palabras) >= 4 and len(set(p.lower() for p in palabras)) == 1:
        return False
    return True
