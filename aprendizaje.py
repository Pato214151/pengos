"""Auto-aprendizaje de traducciones frecuentes.

Idea: cada vez que Llama traduce una frase, se cuenta. Cuando una frase corta
se repite con la MISMA traducción varias veces, se "promueve" a traducción
directa (igual que el glosario curado): la próxima vez sale instantánea y GRATIS
(sin llamar a la API). Esto estira la cuota diaria de Groq y baja la latencia.

Seguridad:
- Solo frases cortas (callouts), no monólogos que nunca se repiten igual.
- Solo se promueve si la traducción fue ESTABLE (mismo resultado cada vez): si
  Llama da otra traducción, se reinicia el contador (no graba un error puntual).
- Nunca toca glosario.json (el curado). Vive en aprendido.json, aparte.
- Tope LRU para no crecer infinito.
- Nunca rompe el pipeline en vivo (todo en try/except).
"""

import json
import threading
import time

from config import BASE_DIR, log
from glosario import normalizar

_RUTA = BASE_DIR / "aprendido.json"

# Parámetros
UMBRAL_PROMOCION = 3      # repeticiones (con misma traducción) para promover
MAX_PALABRAS     = 6      # frases más largas no se cachean (no se repiten igual)
MAX_ENTRADAS     = 1000   # tope LRU del contador

_lock = threading.Lock()
# clave normalizada → {"direction", "original", "translated", "count", "last_seen"}
_contador: dict[str, dict] = {}
# clave (direction|norm) → traducción promovida (lookup rápido)
_aprendidas: dict[str, str] = {}


def _norm(texto: str) -> str:
    """Misma normalización que el glosario (importada para que nunca diverjan)."""
    return normalizar(texto)


def _clave(direction: str, norm: str) -> str:
    return f"{direction}|{norm}"


def _es_cacheable(texto: str) -> bool:
    """Solo frases cortas y con contenido real (callouts), no párrafos largos."""
    t = texto.strip()
    if not t:
        return False
    n_palabras = len([w for w in t.split() if w.strip(".,!?;:")])
    return 1 <= n_palabras <= MAX_PALABRAS


def cargar_aprendido() -> None:
    """Carga aprendido.json y reconstruye las traducciones ya promovidas."""
    global _contador, _aprendidas
    try:
        with open(_RUTA, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        log.info("[APRENDIZAJE] aprendido.json no existe aún — empezando de cero.")
        return
    except Exception as e:
        log.warning(f"[APRENDIZAJE] No se pudo cargar aprendido.json: {e}")
        return

    with _lock:
        _contador = data.get("contador", {})
        _aprendidas = {}
        for k, e in _contador.items():
            if e.get("count", 0) >= UMBRAL_PROMOCION and e.get("translated"):
                _aprendidas[k] = e["translated"]
    log.info(
        f"[APRENDIZAJE] {len(_contador)} frases vistas, "
        f"{len(_aprendidas)} promovidas (cache gratis)."
    )


def _guardar_sin_lock() -> None:
    """Persiste el contador a disco. Asume que el caller ya tiene _lock."""
    try:
        # Tope LRU: si nos pasamos, descartar las menos frecuentes / más viejas.
        if len(_contador) > MAX_ENTRADAS:
            ordenadas = sorted(
                _contador.items(),
                key=lambda kv: (kv[1].get("count", 0), kv[1].get("last_seen", 0)),
            )
            for k, _ in ordenadas[: len(_contador) - MAX_ENTRADAS]:
                _contador.pop(k, None)
                _aprendidas.pop(k, None)
        tmp = _RUTA.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"contador": _contador}, f, ensure_ascii=False, indent=2)
        tmp.replace(_RUTA)
    except Exception as e:
        log.warning(f"[APRENDIZAJE] No se pudo guardar aprendido.json: {e}")


def traduccion_aprendida(texto: str, direction: str) -> str | None:
    """Devuelve la traducción promovida para esta frase/dirección, o None."""
    k = _clave(direction, _norm(texto))
    with _lock:
        return _aprendidas.get(k)


def registrar_traduccion(direction: str, original: str, translated: str) -> None:
    """Cuenta una traducción REAL de Llama. Promueve si se vuelve estable.

    Llamar SOLO tras una traducción genuina de la API (no tras un acierto de
    cache/glosario, o el contador se inflaría solo).
    direction: "en2es" o "es2en".
    """
    try:
        if not _es_cacheable(original) or not translated.strip():
            return
        norm = _norm(original)
        if not norm:
            return
        k = _clave(direction, norm)
        now = time.time()
        with _lock:
            e = _contador.get(k)
            if e is None:
                _contador[k] = {
                    "direction": direction, "original": original.strip(),
                    "translated": translated.strip(), "count": 1, "last_seen": now,
                }
            elif e.get("translated") == translated.strip():
                # Misma traducción → más confianza
                e["count"] = e.get("count", 0) + 1
                e["last_seen"] = now
                if e["count"] == UMBRAL_PROMOCION and k not in _aprendidas:
                    _aprendidas[k] = translated.strip()
                    log.info(f"[APRENDIZAJE] promovida ({direction}): "
                             f"{original.strip()[:40]!r} → {translated.strip()[:40]!r}")
            else:
                # Traducción distinta → inestable: reiniciar con la nueva
                e["translated"] = translated.strip()
                e["count"] = 1
                e["last_seen"] = now
                _aprendidas.pop(k, None)
            _guardar_sin_lock()
    except Exception as e:
        log.warning(f"[APRENDIZAJE] error al registrar: {e}")


def top_frases(n: int = 10) -> list[tuple[str, str, int]]:
    """Las n frases más dichas (original, dirección, veces). Para stats/UI futuro."""
    with _lock:
        items = sorted(_contador.values(), key=lambda e: e.get("count", 0), reverse=True)
    return [(e["original"], e["direction"], e["count"]) for e in items[:n]]
