# Mockups Visuales — Pengos (Overlay de Traducción Gamer)

> 6 visualizaciones del overlay en diferentes estados y contextos de uso.

---

## 1. Overlay — Estado Inactivo (Fondo)

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                    (Fortnite / Valorant / Apex)         │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│                                        ┌─┐             │
│                                        │●│ ── verde = OK│
│                                        └─┘             │
│                                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │      │
│  └──────────────────────────────────────────────┘      │
│   Barra delgada semitransparente en la esquina          │
│   Mide ~520×4px — apenas visible                        │
│   Indica que Pengos está vivo, sin molestar             │
└──────────────────────────────────────────────────────────┘
```

**Especificaciones:**
- Ancho: 520px | Alto: 4px (mínimo)
- Posición: esquinero (configurable: bottom-left, top-right, etc.)
- Opacidad: 15% de fondo + borde 1px
- No captura clicks (atributo `WA_ShowWithoutActivating` + `WA_TransparentForMouseEvents`)
- Animación: aparece solo cuando hay datos o eventos activos

---

## 2. Overlay — Escucha Pasiva (F4) mostrando traducción

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│  ┌────────────────────────────────────────┐  ┌─┐      │
│  │ ● PTT                                 │  │●│      │
│  └────────────────────────────────────────┘  └─┘      │
│                        ⟳ procesando...                  │
│  ┌──────────────────────────────────────────────┐      │
│  │ he's one shot                                 │ EN  │
│  │                                              │ gris│
│  ├──────────────────────────────────────────────┤      │
│  │ está a un tiro                               │ ES  │
│  │                                              │verde│
│  ├──────────────────────────────────────────────┤      │
│  │ push left now                                │ EN  │
│  ├──────────────────────────────────────────────┤      │
│  │ presiona por la izquierda ahora              │ ES  │
│  └──────────────────────────────────────────────┘      │
│                                                        │
└──────────────────────────────────────────────────────────┘
```

**Especificaciones:**
- Indicador `● PTT` naranja = F4 presionado, capturando audio del sistema
- `⟳ procesando...` amarillo = audio yendo a Groq, esperando respuesta
- Cada línea EN (texto original) → gris claro, tamaño 12px
- Cada línea ES (traducción) → verde brillante `#00ff99`, tamaño 16px bold
- Padding interno: 4px | Border-radius: 4px | Fondo: `rgba(0,0,0,160)`
- Auto-hide: 6 segundos después del último texto

**Principio de diseño:**
> El EN está en gris porque es ruido de fondo — el ES en verde porque es lo que importa.
> El ojo va directo al verde. Si necesitás verificar el original, está ahí en gris.

---

## 3. Overlay — Modo Micrófono (F5) respuesta activa

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                                                        │
│                                                        │
│                                                        │
│  ┌────────────────────────────────────────┐  ┌─┐      │
│  │ ● MIC                                 │  │●│      │
│  └────────────────────────────────────────┘  └─┘      │
│                        ⟳ procesando...                  │
│  ┌──────────────────────────────────────────────┐      │
│  │ Vos: necesito cura                           │ ES  │
│  │                                              │azul │
│  ├──────────────────────────────────────────────┤      │
│  │ I need healing                               │ EN  │
│  │                                              │blan │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ ✓ I need healing — copiado al portapapeles   │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
└──────────────────────────────────────────────────────────┘
```

**Especificaciones:**
- Indicador `● MIC` azul = F5 presionado, capturando micrófono
- Label `Vos:` en celeste para diferenciar de voz externa
- Traducción EN en blanco (es lo que vas a enviar)
- Confirmación "copiado al portapapeles" con checkmark verde
- Aparece toast de 2s confirmando la copia

**Flujo UX:**
```
F5 hold → hablás → soltás F5 → ⟳ → "I need healing" + clipboard
                                  → overlay muestra resultado
                                  → pegás en el chat del juego (Ctrl+V)
```

---

## 4. Overlay — Frases Rápidas (F2) expandido

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                                                        │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [1. Necesito cura] [2. Cúbreme] [3. Vamos B]   │  │
│  │  [4. Espera]       [5. Push ahora] [6. Detrás]   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ Tú: Cúbreme                                   │ ES  │
│  ├──────────────────────────────────────────────┤      │
│  │ Cover me                                      │ EN  │
│  │                                              │azul │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ ✓ Cover me — copiado al portapapeles         │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
└──────────────────────────────────────────────────────────┘
```

**Mejora propuesta vs actual:**
| Actual | Propuesto |
|--------|-----------|
| 4 botones fijos | 6 botones con scroll si hay más |
| Sin íconos | Con emoji/ícono por categoría 🏥👁️⚔️ |
| Sin tooltip | Tooltip al hover: "Presioná 1-6 o hacé click" |
| Sin búsqueda | Campo de búsqueda rápido si hay >8 frases |
| Se oculta al presionar | Se oculta al presionar **o** al hacer click fuera |

**Wireframe del botón individual:**
```
┌──────────────────────┐
│  3. Vamos B          │
│  ⚔️ Push B           │ ← tooltip: texto en inglés
└──────────────────────┘
```

---

## 5. Overlay — Estado de Error / Sin Conexión

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│                                        ┌─┐             │
│                                        │●│ ── rojo     │
│                                        └─┘             │
│  ┌──────────────────────────────────────────────┐      │
│  │ ⚠ Error de conexión con Groq API             │      │
│  │ Reintentando en 5 segundos...                │      │
│  │ ┌────────────────────────────────────────┐   │      │
│  │ │ Tentar reconexión ahora                  │   │      │
│  │ └────────────────────────────────────────┘   │      │
│  └──────────────────────────────────────────────┘      │
│                                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ Última traducción antes del error:           │      │
│  │ he's one shot                                 │      │
│  │ está a un tiro                               │      │
│  └──────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

**Estados del puntito de estado:**
| Color | Significado | Acción del usuario |
|-------|-------------|-------------------|
| 🟢 Verde | Groq OK, todo normal | — |
| 🟡 Amarillo | Procesando (esperando API) | Esperar |
| 🔴 Rojo | Error de conexión | Click en "Reconectar" o esperar |
| ⚪ Gris | Overlay desactivado por hotkey | Presionar F4/F5 para activar |

---

## 6. Overlay — Modo "Streamer" (Propuesta v2.0)

```
┌──────────────────────────────────────────────────────┐
│  [🔴 EN VIVO] traduciendo: inglés → español          │
│                                                        │
│                    JUEGO A PANTALLA COMPLETA            │
│                                                        │
│  ┌──────────────────────────────────────────┐          │
│  │ 🎤 Compañero (EN): "he's one shot"       │          │
│  │ 📺 Traducción: "está a un tiro"          │          │
│  ├──────────────────────────────────────────┤          │
│  │ 🎤 Tú (ES→EN): "necesito cura"           │          │
│  │ 📺 "I need healing" ✓ copiado            │          │
│  ├──────────────────────────────────────────┤          │
│  │ ⏱ 1:23 ─── 12 traducciones esta sesión   │          │
│  │ 📊 79% precisión estimada                │          │
│  │ 💰 $0.04 consumido esta sesión           │          │
│  └──────────────────────────────────────────┘          │
│                                                        │
│  ┌──────────────────────────────────────────┐          │
│  │ 📋 Historial                          ▼ │          │
│  │ [he's one shot → está a un tiro]        │          │
│  │ [push left → presiona izquierda]        │          │
│  │ [need shield → necesito escudo]         │          │
│  └──────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────┘
```

**Features del modo Streamer (propuesta):**
- Panel de estadísticas en vivo
- Historial expandible de traducciones
- Contador de costo de API (transparencia para el streamer)
- Indicador de idioma detectado por cada hablante
- Overlay más ancho (720px) para mostrar más información

---

## Variaciones de Posición del Overlay

```
┌──────────────────────────────────────────┐
│  ┌──────────────────┐                    │
│  │ TOP-LEFT         │                    │
│  │ • traducción     │    ┌─────────────┐ │
│  │ • original       │    │ TOP-RIGHT   │ │
│  └──────────────────┘    │ • traducción│ │
│                          │ • original  │ │
│                          └─────────────┘ │
│                                          │
│     ┌─────────────────────────┐          │
│     │ BOTTOM-LEFT             │          │
│     │ • traducción (verde)    │          │
│     │ • original (gris)       │          │
│     └─────────────────────────┘          │
│                    ┌────────────────────┐│
│                    │ BOTTOM-RIGHT       ││
│                    │ • traducción       ││
│                    │ • original         ││
│                    └────────────────────┘│
└──────────────────────────────────────────┘
```

**Flujo de diseño recomendado:**
1. Por defecto: bottom-left (menos obstructivo para HUD de juegos)
2. En Valorant: top-left (minimapa está abajo-izquierda)
3. En Fortnite: bottom-center (HUD está en esquinas)
4. En Apex: top-right (minimapa está arriba-izquierda)

---

## Concepto Visual Mejorado (Pengos v2.0)

```
┌──────────────────────────────────────────────────────────┐
│                      PENGOS                              │
│              ════ overlay de traducción ════              │
│                                                          │
│  ┌─ V2.0 ──────────────────────────────────────────┐     │
│  │                                                  │     │
│  │  Propuesta de UI rediseñada:                     │     │
│  │                                                  │     │
│  │  ┌─────────────────────────────────────────┐     │     │
│  │  │  [ENG] he's one shot                     │     │     │
│  │  │  [ESP] está a un tiro 🟢                 │     │     │
│  │  │  ───────────────────────────────────     │     │     │
│  │  │  [ENG] push left now                     │     │     │
│  │  │  [ESP] presiona izquierda ahora 🟢       │     │     │
│  │  │  ───────────────────────────────────     │     │     │
│  │  │  [TÚ]  I need healing ✓ clipboard        │     │     │
│  │  └─────────────────────────────────────────┘     │     │
│  │                                                  │     │
│  │  ┌────────────────────┐ ┌──────────────────┐     │     │
│  │  │ 🟢 Conectado       │ │ ⚙️ Config        │     │     │
│  │  └────────────────────┘ └──────────────────┘     │     │
│  │                                                  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Animaciones y Transiciones

| Evento | Animación | Duración |
|--------|-----------|----------|
| Overlay aparece | Fade in (opacidad 0→1) | 150ms |
| Nueva línea de traducción | Slide up desde abajo | 200ms |
| Indicador "procesando" | Pulse sutil (escala 1→1.05) | 500ms loop |
| Copiado al clipboard | Checkmark aparece + fade out | 2s |
| Error de conexión | Puntito rojo + shake sutil | 300ms |
| Auto-hide | Fade out + deslizar hacia abajo | 300ms |

---

## Paleta de Colores Propuesta

```
Overlay fondo:      rgba(0, 0, 0, 160)  # negro semi-transparente
Texto EN (original):  #aaaaaa            # gris medio
Texto ES (traduc.):   #00ff99            # verde neón (modo listen)
Texto TÚ (propio):    #00aaff            # azul claro (modo mic)
Texto EN respuesta:   #ffffff            # blanco (lo que vas a enviar)
Acento / alertas:     #ffdd44            # amarillo
Error:                #ff4444            # rojo
Borde sutil:          rgba(255,255,255,30) # blanco 12% opacidad
```

---

## Próximas Visualizaciones a Diseñar (Roadmap)

1. ⬜ Modo configuración visual (ventana de settings)
2. ⬜ Dashboard de estadísticas de sesión
3. ⬜ Versión mobile (mockup de overlay en celular con juego mobile)
4. ⬜ Comparación lado a lado: sin Pengos vs con Pengos
5. ⬜ Diagrama de flujo de onboarding del usuario
