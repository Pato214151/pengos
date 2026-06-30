import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

_CONFIG_PATH = BASE_DIR / "config.json"
try:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print(
        f"\n[Pengos] No se encontró el archivo de configuración:\n  {_CONFIG_PATH}\n\n"
        "Asegurate de ejecutar Pengos desde la carpeta del proyecto, o crea un "
        "config.json válido (podés copiar el de ejemplo del repositorio).\n",
        file=sys.stderr,
    )
    sys.exit(1)
except json.JSONDecodeError as e:
    print(
        f"\n[Pengos] El archivo de configuración tiene un error de formato (JSON inválido):\n"
        f"  {_CONFIG_PATH}\n  Línea {e.lineno}, columna {e.colno}: {e.msg}\n\n"
        "Revisá que no falten comas o comillas. Podés validarlo en https://jsonlint.com\n",
        file=sys.stderr,
    )
    sys.exit(1)

_level = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
logging.basicConfig(
    level=_level,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "pengos.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("pengos")

api_key = os.environ.get("GROQ_API_KEY") or config.get("api_key", "")
if not api_key:
    log.error("API key no encontrada. Configurá GROQ_API_KEY en .env o en config.json")
    sys.exit(1)

# max_retries=0: desactivamos el reintento interno del SDK (que esperaba ~44s × 2
# en silencio). Así el 429 sube de inmediato a audio.py, que decide: si es límite
# DIARIO (RPD) se rinde al instante; si es transitorio, reintenta con su propio gap.
# timeout=30s: con UN solo worker por stream, una request colgada (TCP que no
# responde) congelaría TODA la traducción. El timeout la corta, el error sube a
# audio.py como reintentable ("timeout") y el worker sigue con el audio siguiente.
client = Groq(api_key=api_key, max_retries=0, timeout=30.0)


def save_config(data: dict, new_api_key: str | None = None) -> None:
    """Guarda config.json y opcionalmente actualiza la API key en .env.

    - data: diccionario completo con la misma estructura de config.json
    - new_api_key: si se pasa, se actualiza GROQ_API_KEY en .env
    """
    # Escribir config.json
    with open(BASE_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info("[CONFIG] config.json guardado.")

    # Actualizar .env si cambió la API key
    if new_api_key is not None:
        env_path = BASE_DIR / ".env"
        lines: list[str] = []
        found = False
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GROQ_API_KEY"):
                        lines.append(f"GROQ_API_KEY={new_api_key}\n")
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f"GROQ_API_KEY={new_api_key}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        os.environ["GROQ_API_KEY"] = new_api_key
        log.info("[CONFIG] .env actualizado con nueva API key.")

    # Recargar en memoria
    config.clear()
    config.update(data)
    log.info("[CONFIG] Configuración recargada en memoria.")
