# Guía de Uso Completa — Pengos

> Para quién es, qué problema resuelve, cómo usarlo paso a paso.

---

## 1. ¿Qué es Pengos?

**Pengos es un overlay de traducción de voz en tiempo real para videojuegos.**

Funciona así:
- **Jugadores en inglés** → vos escuchás en español [modo escucha]
- **Vos hablás en español** → ellos escuchan/leen en inglés [modo respuesta]

Todo sin minimizar el juego, sin pantallas divididas, sin sacar las manos del teclado.

---

## 2. ¿Para quién es?

### Persona principal: "Carlos"
- Edad: 18-30
- Juega: Valorant, Fortnite, Apex Legends, CS2, Minecraft
- Servidores: NA (Norteamérica)
- Idioma: español nativo, inglés básico o nulo
- Dolor principal: "Entiendo algunas palabras pero cuando hablan rápido me pierdo y quedó como el malo del equipo"
- Dolor secundario: "Sé lo que quiero decir pero no sé cómo se dice en inglés, y para cuando Google Translate abrió, ya me mataron"

### ¿Por qué existe Pengos?

Porque hay 300M+ de gamers latinoamericanos jugando en servidores norteamericanos. Porque el matchmaking te empareja con quien sea. Porque saber inglés no debería ser requisito para jugar bien en equipo.

---

## 3. ¿Cómo se interpreta el overlay? (guía visual)

```
┌──────────────────────────────────────────────┐
│ he's one shot                                 │ ← gris: texto ORIGINAL (inglés que dijo
│                                              │          tu compañero)
├──────────────────────────────────────────────┤
│ está a un tiro                               │ ← verde: TRADUCCIÓN al español (esto
│                                              │          es lo que importa leer)
├──────────────────────────────────────────────┤
│ Vos: necesito cura                           │ ← azul: lo que VOS dijiste en español
│                                              │          (confirmación)
├──────────────────────────────────────────────┤
│ I need healing                               │ ← blanco: cómo se dice en INGLÉS
│                                              │          (ya copiado al clipboard)
└──────────────────────────────────────────────┘
```

**Regla de oro:** SIEMPRE mirá primero el texto de color — verde o blanco. El gris es contexto. El azul es confirmación de vos mismo.

---

## 4. Instalación paso a paso

### Requisitos
- Windows 10/11
- Python 3.10 (exactamente 3.10.x)
- VB-CABLE (driver de audio virtual, gratuito)
- Conexión a internet

### Paso 1: Instalar VB-CABLE
1. Descargar VB-CABLE desde https://vb-audio.com/Cable/
2. Ejecutar `VBCABLE_Setup.exe` como administrador
3. Reiniciar PC
4. Verificar: en "Dispositivos de grabación" aparece "CABLE Output"

### Paso 2: Configurar audio en Windows
```
🔊 Sonido → Panel de control de sonido → Reproducción
   → Parlantes (predeterminado) ✅
   → CABLE Input ❌ (deshabilitado — no lo uses)

🔊 Sonido → Grabación
   → CABLE Output (predeterminado) ✅
```
**En el juego:** Configurá el audio del juego para que salga por tus parlantes normales. Pengos captura lo que escuchás vía CABLE Output.

### Paso 3: Instalar Pengos
```bash
git clone <repo> o descargá el zip
cd Pengos
python3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 4: Configurar API key (Groq)
Crear archivo `.env` en la carpeta `Pengos/`:
```
GROQ_API_KEY=gsk_tu_key_aqui
```
Obtener key gratis en https://console.groq.com (tiene crédito inicial gratuito).

### Paso 5: Configurar config.json
```json
{
  "audio_mode": "vbcable",
  "audio_device_name": "CABLE Output",
  "hotkeys": {
    "push_to_talk": "f4",
    "push_to_mic": "f5",
    "frases_rapidas": "f2",
    "pin_overlay": "f3"
  },
  "overlay": {
    "posicion": "bottom-left"
  }
}
```

### Paso 6: Iniciar
```bash
venv\Scripts\activate
python main.py
```

---

## 5. Escenarios de uso real

### 🎯 Escenario 1: Partida con gringos (modo escucha)

**Setup:** Abrí el juego y luego Pengos. El overlay está invisible esperando.

**Durante la partida:**
1. Tu compañero gringo dice: *"He's one shot, push him!"*
2. Automáticamente el overlay muestra:
   ```
   he's one shot, push him!
   está a un tiro, presionalo!
   ```
3. Entendés que el enemigo está muy bajo. Lo eliminás.
4. Fin de la jugada.

**Sin Pengos:** No entendiste un carajo, entraste a lo loco y te mataron.

### 🎯 Escenario 2: Responder (modo micrófono + clipboard)

1. Necesitás escudo. Estás a punto de morir.
2. **Apretás y sostenés F5:**
   - El overlay muestra `● MIC` en azul
   - Decís al micrófono: *"Necesito escudo"*
3. **Soltás F5:**
   - El overlay muestra `⟳ procesando...`
   - En 1-2 segundos aparece:
     ```
     Vos: necesito escudo
     I need shield
     ✓ I need shield — copiado al portapapeles
     ```
4. **Pegás en el chat del juego (Ctrl+V):** `I need shield`
5. Tu compañero te lanza un escudo.

### 🎯 Escenario 3: Frases rápidas sin micrófono

1. Presionás **F2** → aparece barra de frases rápidas
2. Presionás **2** (Cúbreme):
   ```
   Tú: Cúbreme
   Cover me
   ✓ Cover me — copiado al portapapeles
   ```
3. Pegás en el chat. Ya coordinaste sin hablar.

### 🎯 Escenario 4: Español detectado automáticamente

Cuando un compañero dice algo en español, Whisper lo detecta y se traduce a inglés en vez de a español:
```
[ES] compañero: "va a push"
[→EN] "he's going to push"
```
Esto permite que equipos mixtos (ES + EN) se entiendan bidireccionalmente.

---

## 6. Referencia rápida de hotkeys

| Tecla | Acción | Qué pasa |
|-------|--------|----------|
| **F4** (mantener) | Escuchar compañeros | Captura audio del sistema EN → ES |
| **F5** (mantener) | Hablar vos | Captura micrófono ES → EN + clipboard |
| **F2** | Frases rápidas | Muestra/oculta botones de frases predefinidas |
| **1-4** | Seleccionar frase rápida | Copia frase en inglés al clipboard |
| **F3** | Fijar overlay | Overlay visible permanente (no se oculta) |
| **F3** (otra vez) | Soltar overlay | Vuelve a auto-ocultarse |
| **Ctrl+Shift+Q** | Salir | Cierra todo |

---

## 7. Interpretando el overlay

### Indicadores visuales

```
● PTT       → F4 activo, capturando audio del sistema (naranja)
● MIC       → F5 activo, capturando micrófono (azul)
⟳ procesando → yendo a Groq API, esperar 1-2s (amarillo)

┌─┐
│●│  puntito de estado:
└─┘  ● verde  = Groq funcionando
     ● rojo   = Groq falló (reintentando)
     ● amarillo = procesando
```

### Colores del texto

| Color | Significado |
|-------|-------------|
| Gris `#bbbbbb` | Texto original en inglés (de tu compañero) |
| Verde `#00ff99` | Traducción al español (modo escucha) |
| Celeste `#aaddff` | "Vos:" — confirmación de lo que dijiste |
| Blanco | Traducción al inglés lista para copiar |
| Amarillo `#ffdd44` | Traducción de español a inglés (otro modo) |

### ¿Qué significa que no aparezca nada?

| Situación | Por qué |
|-----------|---------|
| Tu compañero habla y no aparece nada | **Filtro activo:** Whisper detectó silencio, música o ruido. Es normal — el filtro evita basura |
| El overlay no se ve encima del juego | Asegurate de estar en **modo ventana sin bordes** (borderless window) — fullscreen exclusivo NO funciona |
| El puntito está rojo | Groq API no responde. Esperá unos segundos, reconecta automáticamente |
| F4 activo pero no escucha | Verificá que CABLE Output esté configurado como dispositivo de grabación predeterminado |

---

## 8. Tips avanzados

### Reducir latencia
- Configurá `vad_silencio_ms: 300` en config.json (más agresivo = corta frases más rápido)
- Bajá `_MIN_CALL_GAP` en audio.py a 1.5 (no recomendado si tenés límite de tasa de Groq)

### Mejorar precisión
- Agregá términos nuevos a `glosario.json` en `correcciones` (Whisper mishears) y `traducciones_directas` (traducciones instantáneas sin API)
- Ajustá `vad_sensibilidad` de 0 a 3 (3 = más sensible, captura susurros)

### Modo "siempre escuchando"
Cambiá en config.json:
```json
"modo_escucha": "siempre"
```
Ahora F4 ya no es mantener — es toggle (prende/apaga). Ideal para partidas donde todos hablan inglés constantemente.

### Para streamers
- Usá `pin_overlay: f3` para mantener el overlay visible durante toda la partida
- El modo siempre + pin te da subtítulos en vivo para tu stream

---

## 9. Troubleshooting

| Problema | Solución |
|----------|----------|
| "No device found" | ABRÍ VB-CABLE. Si no aparece, reinstalalo y reiniciá |
| Overlay no se ve en juego | Cambiá el juego a **ventana sin bordes** (borderless) |
| Traducciones muy lentas | Revisá tu internet. Groq necesita <50ms de latencia |
| Consola se cierra al instante | La API key es inválida. Verificá .env o config.json |
| "Error 429" | Llegaste al límite de tasa de Groq. Esperá 30s |
| Audio distorsionado | Bajá el volumen del juego. Audio muy alto satura el VAD |
| Whisper devuelve coreano/chino | Ruido de fondo fuerte. Activá filtro de ruido o bajá el volumen |
| F5 no funciona | No hay micrófono conectado o no tiene permisos en Windows |

---

## 10. Glosario gamer incluido

Pengos viene con ~500 términos pre-cargados para:

| Juego | Términos cubiertos |
|-------|-------------------|
| Valorant | spike, rotate, eco, force buy, ult, retake, site, heaven, CT, T, etc. |
| Apex Legends | shield, drop, loot, ping, third party, rez, ult, etc. |
| CS2 / CS:GO | eco, force, save, rush, clutch, plant, defuse, pick, etc. |
| Fortnite | healing, shield, mats, build, edit, box, piece control, etc. |
| Call of Duty | UAV, killstreak, bomb, hardpoint, rotate, pinch, etc. |

Si una frase está en el glosario, **la respuesta es instantánea (0ms)** — ni siquiera se llama a la API.

---

## 11. ¿Y si no tengo VB-CABLE?

Podés usar **Stereo Mix** en lugar de VB-CABLE:
1. Panel de control → Sonido → Grabación
2. Clic derecho → "Mostrar dispositivos deshabilitados"
3. Activá "Stereo Mix"
4. En config.json: `"audio_mode": "stereo_mix"`

O modo **auto** que intenta VB-CABLE primero y cae a Stereo Mix si no lo encuentra:
```json
"audio_mode": "auto"
```
