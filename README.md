# Pengos

<p align="center">
  <img src="imagen/pengos_icon.png" width="120" alt="Pengos">
  <br>
  <em>Overlay de traducción de voz en tiempo real para gaming</em>
  <br>
  <strong>Inglés ↔ Español</strong>
</p>

---

**Escuchás el juego en inglés → ves subtítulos al instante**  
**Hablas en español → Pengos traduce y copia al portapapeles**

---

## Cómo funciona

```
  ┌─ MODO ESCUCHA (F4) ────────────────────────────────────────────────┐
  │                                                                     │
  │   Audio sistema (VB-CABLE) → VAD (webrtcvad) → Buffer 300ms         │
  │     → Groq Whisper (transcripción) → Filtros                       │
  │     → Glosario (correcciones + traducción directa, 0ms) ─┬─ Sí →   │
  │     → Groq Llama (traducción EN→ES)                    ─┘   No →   │
  │     → Overlay (EN gris + ES verde) + Historial JSONL               │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
  
  ┌─ MODO HABLAR (F5) ─────────────────────────────────────────────────┐
  │                                                                     │
  │   Micrófono → VAD → Groq Whisper (ES) → Groq Llama (ES→EN)         │
  │     → Portapapeles + Overlay + Historial JSONL                     │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## Requisitos

- **Windows 10/11**
- **Python 3.10** (webrtcvad-wheels no funciona en 3.11+)
- [VB-CABLE](https://vb-audio.com/Cable/) — driver de audio virtual
- Cuenta en [Groq](https://console.groq.com) — API key gratuita

## Instalación

```bash
git clone <repo>
cd Pengos
python3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crear `.env`:
```
GROQ_API_KEY=gsk_tu_key_aqui
```

Configurar VB-CABLE como dispositivo de grabación predeterminado en Windows y ejecutar:

```bash
python main.py
```

---

## Launcher UI

Al iniciar, Pengos muestra un launcher oscuro con:

| Elemento | Descripción |
|----------|-------------|
| ▶ Iniciar | Arranca el overlay y procesamiento de audio |
| ⚙ Configuración | Abre panel de 6 pestañas (General, Audio, Hotkeys, Overlay, Frases, Acerca) |
| 📖 Glosario | _Próximamente_ |
| ● API | Verifica conexión a Groq al abrir |
| ● Audio | Detecta dispositivo de audio configurado |

El laucher se cierra automáticamente al iniciar Pengos.

---

## Hotkeys

| Tecla | Acción |
|-------|--------|
| F4 (mantener) | Escuchar compañeros (EN → ES) |
| F5 (mantener) | Hablar vos (ES → EN + clipboard) |
| F2 | Frases rápidas |
| F3 | Fijar overlay (toggle pin) |
| 1-4 | Seleccionar frase rápida |
| Ctrl+Shift+Q | Salir |

Configurables desde el panel de ajustes.

---

## Panel de Configuración

Seis pestañas con ajustes visuales en vivo:

| Pestaña | Ajustes |
|---------|---------|
| ⚙ General | API Key, modo escucha (siempre/mantener), idioma entrada, log level |
| 🎤 Audio | Modo (vbcable/stereo_mix/auto), dispositivo sistema, micrófono, VAD, silencio, buffer |
| ⌨ Hotkeys | Captura de tecla por tecla — presioná la combinación que quieras |
| 📐 Overlay | Posición predefinida + coordenadas X/Y + tiempo visible |
| 💬 Frases | Editor de frases rápidas con agregar/eliminar/reordenar |
| ℹ Acerca de | Versión y créditos |

---

## Arquitectura del proyecto

```
Pengos/
├── main.py              # Entry point → PengosApp (launcher, processor, overlay, tray)
├── config.py            # Carga config.json + .env + inicializa Groq
├── audio.py             # AudioProcessor — VAD, streams, throttle, pipeline
├── overlay.py           # Widget PyQt5 frameless siempre-visible (MAX_LINES=2)
├── api.py               # Groq wrapper: Whisper STT + Llama traducción
├── filters.py           # Validación de transcripciones + anti-hallucinaciones
├── glosario.py          # Glosario (correcciones Whisper + traducciones directas)
├── glosario.json        # ~500 términos gaming (Valorant, Apex, CoD...)
├── historial.py         # Logging de sesión a JSONL
├── launcher.py          # Ventana de inicio con logo, status checks y botones
├── settings_panel.py    # Panel de configuración completo (6 tabs, hotkey capture)
├── tray.py              # System tray icon con menú contextual
├── config.json          # Configuración persistente del usuario
├── requirements.txt
│
├── tests/               # Tests unitarios e integrales
├── docs/                # Documentación técnica y de negocio
│   ├── tech/            # Guía de uso, mockups visuales, MVP plan
│   └── business/        # Análisis financiero, pitch, plan inversores
├── draw.io/             # Diagramas de arquitectura
├── imagen/              # Assets visuales (íconos, capturas)
└── historial/           # Logs de sesión (gitignored)
```

---

## Pipeline de audio

```
Audio sistema (16kHz, 30ms chunks)
  → VAD (webrtcvad, sensibilidad 0-3, 300ms pre-roll)
  → Segmento de voz (~1-2s)
  → Groq Whisper-large-v3-turbo (~$0.04/hora)
  → Filtro: es_transcripcion_valida() (≥4 chars, latín, no hallucinaciones)
  → Glosario: correcciones() (Whisper mishears → fix)
  → Glosario: traduccion_directa() (match → 0ms, bypass LLM)
  → Groq Llama 3.1-8b-instant (solo si no hay match directo)
  → Overlay PyQt5 (EN gris + ES verde)
  → Historial JSONL (timestamp, modo, source, target, latencia)
```

### Throttle adaptativo

El gap entre llamadas a Groq se ajusta solo:

```
1.8s ── 429 ─→ ×1.6 ──→ hasta 8s máx
        éxito ─→ ×0.92 ─→ vuelve al piso
```

- Gap compartido entre sys+mic (el rate limit es de toda la cuenta)
- Límite diario (RPD) → se rinde hasta medianoche UTC

### Idioma

- Whisper auto-detecta el idioma del audio por defecto
- Si detecta español y lo traduce a inglés → re-transcribe forzando español
- Se fija en config.json con `idioma_entrada: "en"|"es"|"auto"`

---

## Costos

~$0.007/hora por usuario en API de Groq. BYOK (Bring Your Own Key).

## Tests

```bash
python tests/test_glosario.py        # Glosario lookups
python tests/test_falsos_positivos.py # Detección de falsos positivos
python tests/test_fatiga.py          # Stress / VAD bajo carga
python tests/test_costo.py           # Estimación de costos API
python tests/test_integral.py        # Pipeline completo (mockeado)
python tests/test_prompts.py         # Validación de prompts
```

---

## Stack

| Componente | Tecnología |
|------------|-----------|
| UI/Overlay | PyQt5 |
| Captura audio | PyAudio |
| VAD | webrtcvad |
| STT | Groq Whisper-large-v3-turbo |
| Traducción | Groq Llama 3.1-8b-instant |
| Hotkeys | pynput |
| Portapapeles | pyperclip |
