"""
Historial de traducciones en archivos JSONL dentro de historial/.
Cada sesión crea hasta 2 archivos (en2es y es2en) con una línea por traducción.
Se conservan solo las últimas MAX_SESIONES sesiones (podar_historial).
"""

import json
import re
import threading
from datetime import datetime
from pathlib import Path

from config import log

BASE_DIR = Path(__file__).parent
HIST_DIR = BASE_DIR / "historial"

# Cuántas sesiones de historial conservar (las más viejas se borran solas).
MAX_SESIONES = 10
# historial_<stamp>_<bucket>.jsonl  →  captura el stamp de sesión
_STAMP_RE = re.compile(r"^historial_(\d{4}-\d{2}-\d{2}_\d{6})_[a-z0-9]+\.jsonl$")

# Una marca de tiempo por sesión, compartida entre los dos archivos.
_SESSION_STAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")

_lock = threading.Lock()
_session_files: dict[str, Path] = {}


def podar_historial(max_sesiones: int = MAX_SESIONES) -> None:
    """Conserva solo las últimas `max_sesiones` sesiones; borra las más viejas.

    Cada sesión deja hasta 2 archivos (en2es + es2en) que comparten el mismo
    stamp. Agrupamos por stamp, ordenamos del más nuevo al más viejo y borramos
    los archivos de las sesiones sobrantes. Nunca rompe nada (todo en try/except).
    """
    try:
        if not HIST_DIR.exists():
            return
        # stamp → lista de archivos de esa sesión
        por_sesion: dict[str, list[Path]] = {}
        for p in HIST_DIR.glob("historial_*.jsonl"):
            m = _STAMP_RE.match(p.name)
            if m:
                por_sesion.setdefault(m.group(1), []).append(p)
        if len(por_sesion) <= max_sesiones:
            return
        # Stamps ordenados del más nuevo al más viejo (el stamp es ordenable como texto).
        stamps_viejos = sorted(por_sesion, reverse=True)[max_sesiones:]
        borrados = 0
        for stamp in stamps_viejos:
            for p in por_sesion[stamp]:
                try:
                    p.unlink()
                    borrados += 1
                except Exception as e:
                    log.warning(f"[HIST] No se pudo borrar {p.name}: {e}")
        if borrados:
            log.info(
                f"[HIST] Poda: {len(stamps_viejos)} sesiones viejas "
                f"({borrados} archivos) eliminadas, conservadas {max_sesiones}."
            )
    except Exception as e:
        log.warning(f"[HIST] Error al podar historial: {e}")


def _bucket(direction: str) -> str:
    """Agrupa por dirección de idioma. mic (tu voz ES→EN) va con es2en."""
    return "en2es" if direction == "en2es" else "es2en"


def _ensure_file(bucket: str) -> Path | None:
    """Crea (una sola vez por sesión) el archivo JSONL de ese bucket."""
    if bucket in _session_files:
        return _session_files[bucket]
    try:
        HIST_DIR.mkdir(exist_ok=True)
        path = HIST_DIR / f"historial_{_SESSION_STAMP}_{bucket}.jsonl"
        _session_files[bucket] = path
        log.info(f"[HIST] {bucket} → {path.name}")
        return path
    except Exception as e:
        log.warning(f"[HIST] No se pudo crear el archivo de historial ({bucket}): {e}")
        return None


def registrar(direction: str, original: str, translated: str) -> None:
    """Agrega una línea JSON al historial del bucket correspondiente.

    Nunca rompe el pipeline en vivo.
    direction: "en2es" → archivo en2es | "es2en"/"mic" → archivo es2en
    """
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "direction": direction,
        "original": original,
        "translated": translated,
    }
    try:
        with _lock:
            path = _ensure_file(_bucket(direction))
            if path is None:
                return
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log.warning(f"[HIST] Error al escribir: {e}")
