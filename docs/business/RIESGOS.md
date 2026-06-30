# ANÁLISIS DE RIESGOS — PENGOS
## Estrategia de mitigación y plan B

---

## MATRIZ DE RIESGOS

```
Alto  │ ┌─────────────────────────────────────────────────────┐
      │ │                                                     │
      │ │  ① Groq cambia       ④ Antivirus                   │
      │ │  precios/TPM          falso positivo                │
      │ │                                                     │
      │ │  ② Competidor        ⑤ Churn alto                  │
      │ │  copia app           ⑥ Poca adopción                │
      │ │                                                     │
      │ │  ③ Piratería                                       │
      │ │                                                     │
Bajo  │ └─────────────────────────────────────────────────────┘
         Baja            Probabilidad              Alta
```

---

## RIESGO 1: Groq cambia precios o limita el free tier

**Probabilidad:** 50% | **Impacto:** Alto | **Prioridad:** 🚨

### Escenario pesimista
Groq elimina el free tier o sube precios del whisper/llama 3.1 8B. El usuario deja de usar la app porque su API key ya no es gratis.

### Mitigación
- **BYOK** — el usuario tiene su propia key, no dependés de un pool compartido
- **Soportá múltiples proveedores** — DeepSeek, OpenAI, OpenRouter, Together AI
- **Hacé transparente el costo** — decile al usuario cuánto gasta por hora de juego
- **Ofrecé modelos locales como opción** — whisper.cpp corre en CPU/GPU local

### Trigger de acción
Si Groq anuncia cambios de pricing, tenés 30 días para migrar. Implementá soporte para OpenAI compatible API (la mayoría de providers usan el mismo formato).

---

## RIESGO 2: Competidor copia la app

**Probabilidad:** 80% | **Impacto:** Medio | **Prioridad:** ⚠️

### Escenario pesimista
GamerTranslate, HaloVoice, o un nuevo proyecto open source agrega glosario en español y te come mercado.

### Mitigación
- **Comunidad > features** — el que tenga más glosario comunitario gana
- **Slang colombiano auténtico** — no es traducible automáticamente, necesitás hablarlo
- **Auto-aprendizaje** — mientras más se usa, mejor traduce (ventaja de datos)
- **Velocidad de iteración** — si sos rápido, siempre vas un paso adelante

### ¿Qué hacer si pasa?
No entres en guerra de precios. Doblá la apuesta por tu nicho: **colombianos primero**. Que tu app SEA la app de los colombianos en el exterior. Eso no te lo copia un equipo en Silicon Valley.

---

## RIESGO 3: Piratería de licencias

**Probabilidad:** 70% | **Impacto:** Medio | **Prioridad:** ⚠️

### Escenario pesimista
Tu .exe termina en un foro de MegaGames o en un grupo de Telegram de juegos piratas. 10,000 personas lo descargan sin pagar.

### Mitigación COMPLETA — no hagás DRM agresivo
- El DRM nunca funciona (Denuvo se crackea, imaginate lo tuyo)
- En vez de prevenirlo, **convertilo en marketing**
- Agregá un watermark visible: "Pengos — Comprado por [USUARIO]"
- La versión pirata tiene un delay de 2s agregado a propósito
- Mostrá un banner en la versión pirata: "Disfrutando Pengos? Apoyá al dev colombiano → $9.99"
- **Licencia social**: "Si te gusta, compartí el link oficial con tus amigos"

### Filosofía
> Que te pirateen es mejor que que no te conozcan. Cada pirata es un embajador no pago. Si 100 piratean y 1 termina comprando, ganaste.

---

## RIESGO 4: Antivirus detecta el .exe como falso positivo

**Probabilidad:** 60% | **Impacto:** Bajo-Alto | **Prioridad:** ⚠️

### Escenario pesimista
Windows Defender/AVG/McAfee detecta el .exe como amenaza porque:
- No tiene firma digital
- Usa pynput (monitoreo de teclas)
- Usa PyAudio (grabación de audio)
- Es un .exe compilado con PyInstaller (patrón conocido de malware)

### Mitigación
1. **Código abierto** — cualquiera puede ver que no hay malware
2. **Firma digital** — comprar certificado de código (~$200/año, Extended Validation)
3. **Reportar falso positivo** — submit a Microsoft Security Intelligence
4. **AppImage/portable** — si es solo el .exe portable, menos problemas
5. **Alternative installer** — MSI installer firmado en vez de .exe portable

### Sin firma digital
Sin firma, esperá que ~30% de los usuarios tengan problemas con antivirus. El soporte técnico te va a consumir tiempo.

---

## RIESGO 5: Churn alto (gente deja de usar)

**Probabilidad:** 70% | **Impacto:** Alto | **Prioridad:** 🚨

### Escenario pesimista
La gente descarga, usa 1 semana y nunca más abre Pengos. Churn del 80-90% en el primer mes.

### Causas típicas
- La latencia es muy alta (>2s)
- Se olvidan de abrirlo antes del juego
- Configuración de audio complicada (VB-CABLE, Stereo Mix)
- Solo juegan 1 vez a la semana y no vale la pena

### Mitigación
- **Auto-inicio con Windows** — opción toggleable
- **Instalación 1-click** — que VB-CABLE se configure automáticamente
- **Modo "recordar"** — guardá última configuración, que abra y funcione sin clicks
- **Feedback visible** — que el usuario VEA que está funcionando (los indicadores del overlay)
- **Notificaciones** — "Pengos está listo para traducir" al iniciar juego
- **50% del churn se va en la primera configuración.** Hacé que sea imposible configurarlo mal.

---

## RIESGO 6: Poca adopción

**Probabilidad:** 60% | **Impacto:** Muy Alto | **Prioridad:** 🚨

### Causas raíz
- No hay suficiente gente que NECESITE esto
- El problema no duele lo suficiente como para pagar
- No llegaste a la audiencia correcta

### Plan B (pivot)
Si después de 60 días no despegó:

| Pivot | Cómo | Por qué funcionaría |
|-------|------|---------------------|
| **Enfoque Apex Legends** | Traducí términos específicos de Apex | Menos competencia que Valorant |
| **Overlay para Streamers** | Mostrá la traducción en pantalla para la audiencia | Streamers tienen presupuesto |
| **Herramienta para servers de Discord** | Bot de Discord que traduce VOZ de canales de voz | Ya hay bots de texto, no de voz |
| **Versión mobile** | App Android que captura audio del juego | Mercado mobile es enorme en LATAM |
| **Open source + donaciones** | Liberalo 100% y viví de GitHub Sponsors/Donaciones | Si es útil, la comunidad mantiene |
| **Vendérselo a Overwolf** | Overwolf compra apps de gaming | Ellos ya tienen el marketplace |

---

## PLAN DE CONTINGENCIA — SI TODO FALLA

### Día 60 — Señales de que NO funciona
- [ ] <200 descargas totales
- [ ] <10 licencias vendidas
- [ ] <20 usuarios activos semanales
- [ ] Discord con <50 miembros y sin actividad
- [ ] No hay crecimiento orgánico (cero menciones, cero compartidos)

### Si tenés 3+ checks, pará la inversión de tiempo.

### Pero no borres el proyecto:
1. **Open source** el código
2. Poné un link de donaciones (PayPal, Ko-fi, Buy Me a Coffee)
3. Escribí un post-mortem en Medium/Dev.to sobre lo que aprendiste
4. Dejá que la comunidad lo mantenga si quiere

### Mientras tanto:
- Buscá trabajo (remoto para afuera si podés, ~$800-1500/mes como dev junior)
- Seguí codeando Pengos en tus tiempos libres
- Las ganas no se te van a ir — tus skills mejoran con cada línea

---

## RESUMEN EJECUTIVO

| Riesgo | Prob | Impacto | Qué hacés HOY |
|--------|------|---------|---------------|
| Groq cambia precios | 50% | Alto | Soporte para múltiples APIs |
| Competidor copia | 80% | Medio | Doblá por nicho colombiano |
| Piratería | 70% | Medio | Convertila en marketing |
| Antivirus FP | 60% | Bajo-Alto | Código abierto + firma |
| Churn alto | 70% | Alto | Simplificá el onboarding |
| Poca adopción | 60% | Muy Alto | Probá, medí, pivotá a tiempo |

**El riesgo más grande es perder tiempo en algo que no funciona.**
**El segundo más grande es rendirte antes de tiempo.**
Saber cuál es cuál es la habilidad más difícil.
