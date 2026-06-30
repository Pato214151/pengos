import io

from config import client, config, log
from filters import detectar_idioma

# Umbrales para descartar alucinaciones de Whisper en silencio/ruido. Whisper
# inventa frases cortas ("a la cintura", "a la la la") cuando el VAD dispara sin
# voz real. En esos segmentos no_speech_prob es alto y avg_logprob muy bajo.
_NO_SPEECH_MAX   = 0.6    # > esto = probablemente silencio
_LOGPROB_MIN     = -0.8   # < esto = transcripción de baja confianza
_LOGPROB_HARD    = -1.0   # < esto = descartar aunque no_speech_prob sea bajo
_COMPRESSION_MAX = 2.4    # > esto = texto repetitivo (alucinación)


def _seg_get(seg, key, default):
    """Lee un campo de un segmento de Whisper (dict u objeto)."""
    if isinstance(seg, dict):
        val = seg.get(key, default)
    else:
        val = getattr(seg, key, default)
    return default if val is None else val


def _es_alucinacion_silencio(segments) -> bool:
    """True si los segmentos parecen alucinación de silencio/ruido (no voz real)."""
    if not segments:
        return False
    no_speech = [float(_seg_get(s, "no_speech_prob", 0.0)) for s in segments]
    logprob   = [float(_seg_get(s, "avg_logprob", 0.0)) for s in segments]
    compress  = [float(_seg_get(s, "compression_ratio", 0.0)) for s in segments]
    mean_ns = sum(no_speech) / len(no_speech)
    mean_lp = sum(logprob) / len(logprob)
    max_cr  = max(compress)
    if mean_lp < _LOGPROB_HARD:
        return True
    if mean_ns > _NO_SPEECH_MAX and mean_lp < _LOGPROB_MIN:
        return True
    if max_cr > _COMPRESSION_MAX and mean_lp < _LOGPROB_MIN:
        return True
    return False

# Prompts de Whisper = SOLO vocabulario (sin oraciones en prosa). Whisper
# transcribe literalmente las frases del prompt cuando el audio es silencio/ruido
# (de ahí salía "Fruits de comunicación en partida", eco del prompt viejo).
# Una lista de términos sesga la ortografía sin generar ese eco.
_WHISPER_PROMPT_EN = (
    "rush, push, peek, clutch, eco, spike, plant, rotate, flank, ult, "
    "defuse, retake, util, smoke, frag, callout"
)

_WHISPER_PROMPT_ES = (
    "push, rush, flankear, curar, smoke, spike, rotar, retake, clutch, "
    "dale, listo, parcero, parce, chevere"
)

_TRANSLATE_EN_ES_SYSTEM = (
    "Translate the following English text to natural Colombian Spanish. "
    "Translate ONLY what is written, word for word. Do not add or explain anything. "
    "Keep proper names, nicknames and gamertags unchanged (e.g. Pato, James, Bruno). "
    "Output only the translation. No quotes, no prefix."
)

_TRANSLATE_ES_EN_SYSTEM = (
    "Translate the following Spanish gaming voice line to natural English. "
    "It is Colombian Spanish slang: e.g. 'regular' = mediocre/so-so (NOT good), "
    "'bacano'/'chevere' = cool, 'parcero'/'parce' = buddy, 'una nota' = great. "
    "Keep proper names, nicknames and gamertags unchanged (e.g. Pato, James, Bruno). "
    "Translate the COMPLETE meaning faithfully — "
    "do not summarize, shorten, or omit any part. "
    "Output ONLY the English translation. No explanation, no quotes, no prefix."
)


def _whisper_call(audio_bytes: bytes, language: str | None) -> tuple[str, str]:
    """Una llamada a Whisper. Devuelve (texto, idioma_del_audio).

    Usa verbose_json para obtener el campo `language` que Whisper detecta del
    AUDIO (no del texto). Groq lo devuelve como palabra completa: 'Spanish'/'English'.
    """
    prompt = _WHISPER_PROMPT_ES if language == "es" else _WHISPER_PROMPT_EN
    with io.BytesIO(audio_bytes) as f:
        kwargs: dict = dict(
            model="whisper-large-v3-turbo",
            file=("audio.wav", f),
            response_format="verbose_json",
            prompt=prompt,
        )
        if language is not None:
            kwargs["language"] = language
        result = client.audio.transcriptions.create(**kwargs)

    text = (getattr(result, "text", "") or "").strip()
    audio_lang = (getattr(result, "language", "") or "").strip().lower()

    segments = getattr(result, "segments", None)
    if text and _es_alucinacion_silencio(segments):
        log.info("[ALUCINACIÓN] Descartado por silencio/baja confianza: %r", text)
        return "", audio_lang

    return text, audio_lang


def _lang_code(audio_lang: str) -> str | None:
    """Mapea el campo language de Groq ('Spanish'/'English'/...) a 'es'/'en'/None."""
    if audio_lang.startswith("span") or audio_lang == "es":
        return "es"
    if audio_lang.startswith("eng") or audio_lang == "en":
        return "en"
    return None


def transcribe_audio(audio_bytes: bytes, language: str | None = None) -> tuple[str, str]:
    """Transcribe audio. Returns (transcribed_text, detected_language_code: 'en'|'es').

    Si language is None, auto-detecta usando el idioma del AUDIO (campo language de
    Whisper), fiable incluso cuando Whisper auto-traduce el texto a inglés. Si el audio
    es español pero el texto salió en inglés (auto-traducción), re-transcribe forzando
    español para recuperar el texto original. Pasar language='es' fuerza español (mic).
    """
    text, audio_lang = _whisper_call(audio_bytes, language)

    if language is not None:
        # Idioma forzado (modo mic) — no detectar
        return text, language

    code = _lang_code(audio_lang)

    if code == "es":
        # Audio en español. Si el texto salió en inglés, Whisper auto-tradujo →
        # re-transcribir forzando español para recuperar el texto real.
        if text and detectar_idioma(text) == "en":
            text_es, _ = _whisper_call(audio_bytes, "es")
            if text_es:
                text = text_es
        return text, "es"

    if code == "en":
        return text, "en"

    # Idioma del audio desconocido → caer a detección por texto
    return text, detectar_idioma(text)


def translate_en_to_es(english: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": _TRANSLATE_EN_ES_SYSTEM},
            {"role": "user", "content": english},
        ],
        temperature=0.1,
        max_tokens=180,
    )
    return resp.choices[0].message.content.strip().strip('"\'`')


def translate_es_to_en(spanish: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": _TRANSLATE_ES_EN_SYSTEM},
            {"role": "user", "content": spanish},
        ],
        temperature=0.1,
        max_tokens=180,
    )
    return resp.choices[0].message.content.strip().strip('"\'`')
