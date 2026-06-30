# Plan de Tareas MVP — Pengos

> Versión 1.2 | Fecha: 2026-04-28  
> Actualizado con diagnóstico de bugs reales del proyecto anterior (logs 2026-04-26).

---

## Fase 0: Preparación del entorno

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 0.1 | Instalar VB-CABLE en Windows | Tener un dispositivo de loopback para capturar el audio del sistema. | En "Dispositivos de grabación" aparece "CABLE Output". |
| 0.2 | Crear carpeta del proyecto y entorno virtual Python 3.10 (exactamente 3.10, no 3.11+ por compatibilidad con webrtcvad-wheels) | Aislar las dependencias de Pengos. | Ejecutar `venv\Scripts\activate` y `python --version` muestra 3.10.x |
| 0.3 | Crear `config.json` con API key de Groq, idiomas, hotkeys | Centralizar la configuración sin interfaz gráfica. | Leer el archivo con Python y mostrar los valores en consola. |

---

## Fase 1: Captura de audio del sistema

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 1.1 | Listar dispositivos de audio con PyAudio y encontrar "CABLE Output" | Confirmar el índice del dispositivo loopback. | El script imprime todos los dispositivos y uno se llama "CABLE Output". |
| 1.2 | Abrir stream de entrada con PyAudio (16 kHz, mono, chunks de 480 muestras = 30ms) | Leer audio del sistema en tiempo real. | Se ejecuta sin errores y `stream.read()` devuelve bytes. |
| 1.3 | Grabar 10 segundos de audio a un archivo WAV usando el stream | Verificar que el loopback captura lo que suena en el juego. | Reproducir el WAV y escuchar el audio del juego. |

---

## Fase 2: Detector de voz (VAD)

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 2.1 | Instalar `webrtcvad-wheels` (NO `webrtcvad`) e inicializar con sensibilidad 2 | Tener el VAD listo para clasificar chunks. **Nota:** `webrtcvad` puro explota en Windows sin Visual Studio Build Tools. `webrtcvad-wheels` viene precompilado. | El módulo importa sin errores. |
| 2.2 | Para cada chunk del stream, llamar a `vad.is_speech()` | Detectar si el chunk actual contiene voz. | En consola se imprime "Voz" / "Silencio" mientras suena audio. |
| 2.3 | Acumular chunks con voz en un buffer; al detectar 800ms de silencio, guardar segmento | Construir segmentos de audio de 1-2 segundos con habla. | El script genera un archivo WAV por cada segmento de habla detectado. |

---

## Fase 3: Conexión con Groq (Whisper + Llama) + Filtros de seguridad

> **Contexto:** Los logs del proyecto anterior (2026-04-26) mostraron 4 bugs críticos:
> - VAD enviaba silencio a Whisper → Llama alucinaba listas de jerga gamer
> - Llama expandía traducciones: "Fine." → "GG, estoy listo para el rush."
> - Whisper mezclaba caracteres coreanos/vietnamitas en ruido
> - Detector de idioma fallaba en segmentos cortos
>
> Esta fase los cierra antes de integrar con la UI.

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 3.1 | Enviar segmento de audio de prueba (voz clara en inglés) a Groq Whisper con `language="en"` forzado | Evitar alucinaciones multilingüe (caracteres coreanos, vietnamitas, etc.). | La respuesta es texto inglés sin caracteres extraños (ej: "Push left"). |
| 3.2 | Enviar texto transcrito a Groq Llama con prompt EN→ES estricto (instrucción explícita de no inventar ni expandir) | Traducción exacta sin creatividad descontrolada. | `"I need shield"` → `"Necesito escudo"` (no `"GG, necesito escudo para el rush"`). |
| 3.3 | Enviar texto en español a Groq Llama con prompt ES→EN corto y natural | Respuesta activa sin expansión. | `"Cúbreme"` → `"Cover me"` (no `"Cover me, I'm reloading, let's go"`). |
| 3.4 | Implementar `es_transcripcion_valida()`: descartar puntos, silencio y cadenas sin letras reales | Barrera antes de la API de traducción — nunca traduce basura. | Con `"..."` o `". . ."` → no se llama a Llama. Con `"Wait."` → sí se traduce. |
| 3.5 | Añadir reintento simple (1 reintento, timeout 3s) sin fallback de vocabulario inventado | Si falla la API, el overlay muestra estado, nunca texto falso. | Si la API falla o la transcripción es inválida, no aparece lista de palabras gamer. |
| 3.6 | Checkpoint con audio del log anterior: verificar que el pipeline nuevo no reproduce los 4 bugs. | Confirmar que los bugs están cerrados con datos reales. | El log de esta prueba no contiene `". . ."`, ni `"Noob, cap..."`, ni traducciones expandidas. |

**Prompts de referencia:**

```
# Prompt traducción pasiva EN→ES
Eres un traductor para partidas de videojuegos online. Traduce SOLO lo que está en el input al español latino. 
NO agregues palabras. NO expandas. NO mejores. Si el input es corto, la traducción también es corta.
Contexto: comunicación de voz en juegos como Fortnite y Valorant.

# Prompt respuesta activa ES→EN
Eres un asistente de comunicación para gaming. Traduce SOLO lo que está en el input al inglés natural de jugador.
NO agregues frases. NO inventes contexto. Traducción directa y corta.
```

**Tarea 3.5 — Checkpoint de latencia:**
Medir tiempo total desde fin de segmento WAV hasta recibir traducción.  
- < 3s: aceptable para el MVP  
- 3-4s: revisar si buffer de 1s mejora la situación  
- \> 4s: rediseñar antes de integrar UI

---

## Fase 4: Overlay con PyQt5

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 4.1 | Crear ventana frameless, transparente, siempre encima con PyQt5 | Esqueleto del overlay. | Aparece un rectángulo negro semitransparente flotando sobre el escritorio y otras apps. |
| 4.2 | Agregar QLabel para subtítulo en español y QLabel para texto original en inglés | Mostrar traducciones. | Al cambiar el texto con `setText()`, se actualiza en la ventana flotante. |
| 4.3 | Hacer que la ventana se oculte automáticamente tras 5 segundos | Evitar distracción permanente. | La ventana desaparece sola. |
| 4.4 | Agregar QLineEdit visible al presionar F2: al escribir + Enter, copia traducción al portapapeles y la muestra | Modo respuesta activa. | Escribir en el campo, dar Enter, pegar en el Bloc de notas muestra la frase en inglés. |
| 4.5 | Agregar indicador de conexión (puntito verde/amarillo/rojo) | Feedback visual del estado de la API. | Groq OK → verde. Falla → rojo. |

---

## Fase 5: Integración completa

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 5.0 | Cargar `config.json` al arrancar y pasar settings a todos los módulos (captura, API, UI) | Que hotkeys, API key e idioma sean configurables sin tocar código. | Cambiar F2 a F3 en config.json y que funcione sin modificar el script. |
| 5.1 | Conectar hilo de captura+VAD+`es_transcripcion_valida()`+API con hilo de UI (PyQt) usando `pyqtSignal` | La barrera de filtrado va entre VAD y API, antes de cualquier llamada a Groq. | Reproducir audio de silencio → el overlay no muestra nada. Reproducir voz clara → aparece traducción. |
| 5.2 | Manejar ciclo de vida (iniciar/cerrar streams al salir) | El script no deja procesos colgados. | Al cerrar con Ctrl+Shift+Q, el proceso muere sin errores. |
| 5.3 | Probar flujo pasivo completo con video de YouTube en inglés | Simular una partida real. | El overlay muestra traducciones correctas con delay razonable. |
| 5.4 | Probar flujo activo: F2 → escribir → recibir frase → pegar | Validar modo respuesta. | Lo pegado es correcto y natural. |

---

## Fase 6: Prueba en juego real

| # | Tarea | Objetivo | ¿Cómo sé que funciona? |
|---|-------|----------|------------------------|
| 6.1 | Configurar Fortnite/Valorant en modo **ventana sin bordes** (NO fullscreen exclusivo) | Preparar entorno de prueba real — fullscreen exclusivo mata el overlay. | El juego corre sin barras de título y el overlay se ve encima. |
| 6.2 | Jugar una partida en servidor NA con el overlay activo | Validar latencia, legibilidad y utilidad real. | El overlay muestra traducciones antes de que la situación cambie drásticamente. |
| 6.3 | Usar modo respuesta al menos 3 veces durante la partida | Validar modo activo en condiciones reales. | Las frases en inglés son correctas y el equipo responde. |
| 6.4 | Documentar bugs, latencia observada y feedback inicial | Datos para la siguiente iteración. | Lista escrita de mejoras necesarias. |

---

## Límites del MVP (no negociables)

- Solo Windows (WASAPI loopback)
- Solo juegos en modo **borderless** (ventana sin bordes) — fullscreen exclusivo bloquea el overlay
- No micrófono en modo pasivo — solo audio del sistema; el mic se usa solo para modo respuesta activa
- No historial de partidas — todo en memoria
- No interfaz gráfica de configuración — parámetros en `config.json`
- No instalador — `.zip` con script + instrucciones de dependencias
- Dependencia externa requerida: VB-CABLE (el usuario debe instalarlo antes de usar Pengos)
