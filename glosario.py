"""
Glosario curado a mano (glosario.json):
  - correcciones: arregla palabras que Whisper transcribe mal
  - traducciones_directas: frases con traducción fija, sin llamar a la API
    (0 ms y gratis)
Se carga al iniciar con cargar_glosario(); las claves se comparan normalizadas.
"""

import json
import re

from config import BASE_DIR, log

_glosario_correcciones:          dict[str, str] = {}
_glosario_traducciones_directas: dict[str, str] = {}
_STRIP_PUNCT = re.compile(r"^[.,!?;:\-…]+|[.,!?;:\-…]+$")


def normalizar(texto: str) -> str:
    """Normalización canónica: minúsculas + sin puntuación al borde.

    Única fuente de verdad — la importa también aprendizaje.py para que ambas
    normalizaciones (glosario curado y cache aprendida) nunca diverjan.
    """
    return _STRIP_PUNCT.sub("", texto.strip().lower())


def _glosario_key(texto: str) -> str:
    return normalizar(texto)


def cargar_glosario():
    """Lee glosario.json a memoria (ignora claves que empiezan con '_')."""
    global _glosario_correcciones, _glosario_traducciones_directas
    try:
        with open(BASE_DIR / "glosario.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        _glosario_correcciones = {
            k: v for k, v in data.get("correcciones", {}).items()
            if not k.startswith("_")
        }
        _glosario_traducciones_directas = {
            k: v for k, v in data.get("traducciones_directas", {}).items()
            if not k.startswith("_")
        }
        log.info(
            f"[GLOSARIO] {len(_glosario_correcciones)} correcciones, "
            f"{len(_glosario_traducciones_directas)} traducciones directas."
        )
    except FileNotFoundError:
        log.warning("[GLOSARIO] glosario.json no encontrado — continuando sin glosario.")


def corregir_transcripcion(texto: str) -> str:
    """Devuelve la corrección del glosario, o el texto tal cual si no hay."""
    key = _glosario_key(texto)
    return _glosario_correcciones.get(key, texto)


def traduccion_directa(texto: str) -> str | None:
    """Devuelve la traducción fija de la frase, o None si no está en el glosario."""
    key = _glosario_key(texto)
    return _glosario_traducciones_directas.get(key)
