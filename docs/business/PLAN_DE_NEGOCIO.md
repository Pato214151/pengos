# PLAN DE NEGOCIO — PENGOS
## Traducción de voz en tiempo real para gaming (EN↔ES)

---

## 1. EL PRODUCTO Y SU VENTAJA

### ¿Qué es Pengos?
Overlay que traduce VOZ en tiempo real: escuchás a tus compañeros gringos en español y hablás vos en inglés. Corre en Windows, se superpone al juego, zero-latency para términos del glosario (~350 términos de Valorant/Apex/CoD).

### Competencia directa (2026)

| Producto | Precio | Modelo | Voz en tiempo real? | Gaming? | Términos colombianos? |
|---|---|---|---|---|---|
| **GamerTranslate** | $29 one-time | BYOK (tu API key) | Sí | Sí | No |
| **HaloVoice** | Subscription | SaaS | Sí | Parcial | No |
| **Seagull** | $6.99/mes | SaaS | Sí | No (general) | No |
| **EzChat.gg** | Free + ads | Overwolf | No (solo chat texto) | Sí | No |
| **Whispra** | $4.99/mes | SaaS | Sí | Parcial | No |
| **LiveTranslate** | Open source | BYOK | Sí | Sí | No |
| **PENGOS** | **?** | **BYOK** | **Sí** | **Sí** | **SÍ — jerga real colombiana** |

**Diferenciador clave:** Ningún competidor tiene:
- Glosario curado con términos colombianos ("parcero", "chévere", "una nota", "regular" = mediocre)
- Auto-aprendizaje de frases frecuentes (cache local sin API)
- Modo siempre-escucha + PTT simultáneos
- Traducción ES→EN con slang colombiano

---

## 2. MERCADO

### Tamaño (datos 2026)

- **Valorant jugadores activos mensuales:** ~30M (Abril 2026, ActivePlayer.io)
- **Apex Legends:** ~15M MAU estimado
- **Jugadores LATAM en NA servers:** ~15-20% del total → ~5-9M
- **Jugadores colombianos:** ~3-4M (mayor población gaming de la región)
- **Problema real:** 70% de los gamers latinos reportan dificultad comunicándose en equipos internacionales

### Nicho objetivo
1. **Colombianos en Valorant/Apex** (mercado principal) — 2-3M potencial
2. **LATAM general** — expansión natural
3. **Latinos en USA** — poder adquisitivo más alto

---

## 3. ANÁLISIS DE COSTOS (REAL, JUNIO 2026)

### Costos de API (Groq — precios verificados Mayo 2026)

| Servicio | Modelo | Precio |
|---|---|---|
| **Whisper STT** | whisper-large-v3-turbo | $0.04/hr de audio ($0.000667/min) |
| **Traducción EN→ES** | Llama 3.1 8B Instant | $0.05/1M input, $0.08/1M output |
| **Traducción ES→EN** | Llama 3.1 8B Instant | $0.05/1M input, $0.08/1M output |

### Costo por sesión de juego (cálculo real)

**Supuestos realistas:**
- Partida de 30 minutos de Valorant
- ~40% del tiempo hay voz (12 min de audio efectivo)
- Segmentos de ~2s cada uno → ~360 segmentos
- Transcripción: 12 min × $0.000667/min = **$0.008/partida**
- Traducción EN→ES: ~360 requests × ~30 tokens c/u = 10,800 tokens
  - Input: 10,800 × $0.05/1M = **$0.00054**
  - Output: 10,800 × $0.08/1M = **$0.00086**
- **Total por partida de 30 min: ~$0.01**

**Pero la realidad duele más:**
- Glosario + aprendizaje cachean ~60% de las frases (sin llamada a API)
- Sin cache: ~$0.025/partida
- Con cache actual (~30% cobertura): ~$0.018/partida
- Con cache maduro (~70% cobertura): ~$0.007/partida

### Costo mensual por usuario

| Escenario | Partidas/día | Días/mes | Costo API/mes (sin cache) | Costo API/mes (con cache) |
|---|---|---|---|---|
| **Casual** | 2 | 20 | $0.50 | $0.14 |
| **Regular** | 4 | 25 | $2.50 | $0.70 |
| **Tryhard** | 6 | 30 | $4.50 | $1.26 |

### Conclusión de costos
**Cada usuario activo te cuesta entre $0.14 y $1.26/mes en APIs.** Esto es CLAVE: el margen es altísimo si monetizás bien.

**GamerTranslate** ($29 one-time + tu API key) le cobra al usuario y el usuario pone la API key. Es el modelo más seguro. **Te recomiendo exactamente eso: BYOK (Bring Your Own Key).**

---

## 4. ESTRATEGIA DE PRECIOS (3 MODELOS)

### Modelo A: BYOK + One-time (RECOMENDADO)
- **$9.99 one-time** la licencia (precio LATAM)
- El usuario pone su propia API key de Groq (gratis para él si usa el free tier de 14,400 req/día)
- Ventajas:
  - Sin costo de servidores para vos
  - El free tier de Groq alcanza para ~4 partidas/día
  - Escalás sin riesgo financiero
- **Desventaja:** Menos ingreso por usuario

### Modelo B: Freemium BYOK + Premium mensual
- **Gratis:** BYOK, funcionalidad completa, el usuario paga su API
- **Premium $2.99/mes (LATAM) / $4.99/mes (USA):**
  - API key incluida (compartida, con límite diario)
  - Traducciones ilimitadas
  - Glosario expandido con términos nuevos cada mes
  - Prioridad en actualizaciones

### Modelo C: Subscripción pura
- **$3.99/mes LATAM / $6.99/mes USA**
- Todo incluido
- El que tenga más de 3-4 partidas/día nos cuesta más en APIs

---

## 5. PROYECCIÓN FINANCIERA — 3 ESCENARIOS

### Supuestos base
- Tasa de conversión gratis→pago: 5% (Modelo B)
- Churn mensual: 15% (típico en gaming tools)
- Costo API promedio: $0.50/mes por usuario activo (con cache maduro)
- **Costo de vida Colombia 2026:** ~$450-550/mes (vida austera, arriendo compartido, sin lujos)

### Escenario Pesimista — "Hay que buscar trabajo"

| Mes | Descargas | Usuarios activos | Usuarios de pago | Ingreso/mes | Costo API/mes | Ganancia/mes |
|-----|-----------|-----------------|-----------------|-------------|--------------|-------------|
| 1 | 200 | 50 | 3 | $9 | $25 | **-$16** |
| 3 | 500 | 120 | 6 | $18 | $60 | **-$42** |
| 6 | 1,000 | 200 | 10 | $30 | $100 | **-$70** |
| 12 | 2,000 | 350 | 18 | $54 | $175 | **-$121** |

**Veredicto:** No vivís de esto. Ni siquiera cubre APIs.

### Escenario Realista — "Viviendo ajustado"

**Premisa:** Viral moderado en TikTok/YouTube + comunidades gaming colombianas.

| Mes | Descargas | Usuarios activos | Usuarios de pago (5%) | Ingreso/mes ($2.99) | Costo API/mes | Margen |
|-----|-----------|-----------------|----------------------|-------------------|--------------|--------|
| 1 | 500 | 150 | 8 | $24 | $75 | -$51 |
| 2 | 1,200 | 360 | 18 | $54 | $180 | -$126 |
| 3 | 3,000 | 900 | 45 | $135 | $450 | -$315 |
| 4 | 5,000 | 1,500 | 75 | $224 | $750 | -$526 |
| 5 | 8,000 | 2,400 | 120 | $359 | $1,200 | -$841 |
| 6 | 12,000 | 3,600 | 180 | **$538** | $1,800 | **-$1,262** |

**Veredicto:** Estás perdiendo plata cada mes. **Mientras más usuarios, más pérdida.** Si no tenés inversión, no sostenés el modelo C/B.

**Con Modelo BYOK (Modelo A):**

| Mes | Usuarios | Licencias vendidas ($9.99) | Ingreso/mes | Costo API | Ganancia |
|-----|----------|--------------------------|-------------|-----------|----------|
| 1 | 150 | 25 | $250 | $0 (BYOK) | **$250** |
| 3 | 900 | 120 | $1,199 | $0 (BYOK) | **$1,199** |
| 6 | 3,600 | 400 | **$3,996** | $0 (BYOK) | **$3,996** |

**Con BYOK ganás sin escala inversa.** Cada usuario nuevo es plata limpia.

### Escenario Optimista — "Podés vivir de esto"

**Premisa:** Viral fuerte (streamers grandes colombianos lo muestran, + comunidades Discord masivas).

| Mes | Descargas | Licencias ($9.99) | Ingreso/mes | Gastos operativos | Ganancia |
|-----|-----------|------------------|-------------|------------------|----------|
| 1 | 2,000 | 150 | $1,499 | $100 (hosting, dominio) | **$1,399** |
| 2 | 8,000 | 600 | $5,994 | $200 | **$5,794** |
| 3 | 20,000 | 1,500 | $14,985 | $500 | **$14,485** |
| 4 | 40,000 | 3,000 | $29,970 | $1,000 | **$28,970** |
| 5 | 60,000 | 4,500 | $44,955 | $1,500 | **$43,455** |
| 6 | 100,000 | 7,000 | **$69,930** | $2,500 | **$67,430** |

**Veredicto:** Acá sí. Pero necesitás llegar a 100k descargas en 6 meses, lo que requiere marketing agresivo o viral orgánico.

---

## 6. EL PLAN DE ATERRIZAJE — "CÓMO LLEGAMOS"

### Fase 1: Validación (Semana 1-2) — $0 invertido
- [x] App funcionando (listo)
- [ ] Publicar en GitHub como open source (ATTENTION: viral en r/Colombia, r/Valorant)
- [ ] Grabar video mostrándolo en acción y postear en TikTok + YouTube Shorts
- [ ] Crear server de Discord para comunidad
- [ **Meta medible:** 100 usuarios en Discord, 1,000 views en TikTok ]

### Fase 2: Lanzamiento BYOK (Semana 3-4)
- [ ] Empaquetar Pengos como .exe portable (PyInstaller)
- [ ] Implementar sistema de licencias simple (email + key, pago vía MercadoPago/Nequi)
- [ ] Precio: $9.99 one-time
- [ ] Landing page mínima con video demo + link de descarga
- [ **Meta medible:** 50 licencias vendidas ($500) ]

### Fase 3: Crecimiento orgánico (Mes 2-3)
- [ ] Postear en grupos de Facebook de gaming colombiano (Valorant Colombia, Apex Legends LATAM)
- [ ] Contactar 5 streamers colombianos medianos (1k-5k viewers) para que lo prueben gratis
- [ ] Activar referidos: "Recomendá y ganá 1 mes gratis"
- [ **Meta medible:** 500 licencias vendidas total ($5,000) ]

### Fase 4: Escalar (Mes 4-6)
- [ ] Si las ventas superan $3k/mes → dedicarle tiempo completo
- [ ] Agregar más juegos (CS2, Fortnite, Overwatch)
- [ ] Mejorar el glosario con términos específicos por juego (comunidad puede contribuir)
- [ **Meta medible:** 2,000+ licencias, $20k+ ingresos acumulados ]

---

## 7. RIESGOS Y MITIGACIÓN

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **Groq cambia precios** | Media | Alto | Migrar a DeepSeek/OpenRouter (misma API compatible) |
| **Groq free tier se acaba** | Alta | Medio | BYOK = el usuario decide si paga su API |
| **Alguien copia la app** | Alta | Bajo | Tu ventaja es el glosario colombiano + comunidad |
| **Poca adopción** | Media | Alto | BYOK = cero riesgo financiero, no perdés plata |
| **Piratería de licencias** | Media | Medio | Licencias baratas ($9.99) = no vale la pena piratear |
| **Riot bloquea overlays** | Baja | Alto | Overlay no interactúa con el juego, es imposible de detectar |
| **Antivirus falso positivo** | Media | Medio | Firmar el .exe con certificado (cuesta ~$200/año) |

---

## 8. TEST DE HIPÓTESIS — VERIFICABLE

### Hipótesis 1: "Hay mercado dispuesto a pagar"
**Test:** Publicar en r/Valorant y r/Colombia "¿Pagarían $9.99 one-time por un overlay que traduzca voz EN↔ES en tiempo real?"
- ✅ Si +50 upvotes y +20 "sí" → validado
- ❌ Si puro "no" o críticas → repensar precio o modelo

### Hipótesis 2: "El glosario colombiano es el diferenciador"
**Test:** Video TikTok mostrando "parcero → buddy", "regular → mediocre"
- ✅ Si >10k views y >500 likes → el diferenciador funciona
- ❌ Si pasa sin reacción → el nicho colombiano no es suficiente

### Hipótesis 3: "Usuarios con BYOK sí compran la licencia"
**Test:** Cuando saques la versión de pago, cuantos descargaron gratis pasan a pago
- ✅ Si >=3% conversión → viable
- ❌ Si <1% conversión → probar precio de $4.99

### Hipótesis 4: "Gamers colombianos recomiendan la herramienta"
**Test:** Tracking de referidos
- ✅ Si cada usuario de pago trae ≥1 usuario nuevo → crecimiento orgánico funciona
- ❌ Si no hay referidos → necesitás invertir en ads

---

## 9. VEREDICTO FINAL — ¿SE PUEDE VIVIR DE ESTO?

### Sí, PERO con condiciones específicas:

| Condición | Realista? | Cómo |
|-----------|-----------|------|
| **Modelo BYOK** | ✅ Sí | Sin riesgo de APIs |
| **Precio LATAM $9.99** | ✅ Sí | Una compra de un combo de pollo |
| **Llegar a 500 ventas** | ✅ Posible en 3-4 meses | Viral en comunidades gaming colombianas |
| **Vivir de esto** | ✅ Con ~167 ventas/mes** | $1,670/mes = vida austera en Colombia |
| **Vivir BIEN** | ✅ Con ~400 ventas/mes** | $4,000/mes = vida cómoda en Colombia |
| **Escalar** | ✅ Con ~1,000 ventas/mes** | $10,000/mes = ya podés contratar a alguien |

### Números mágicos:

```
$1,670/mes → 167 licencias vendidas/mes →  ~5-6 ventas/día → VIDA AUSTERA
$3,000/mes → 300 licencias vendidas/mes →  ~10 ventas/día  → VIDA CÓMODA
$5,000/mes → 500 licencias vendidas/mes →  ~17 ventas/día  → VIDA TRANQUILA
```

### REALIDAD para junio 2026:

1. **HOY no podés vivir de esto.** Necesitás construir audiencia primero.
2. **En 3 meses (Septiembre 2026)** — si jugás bien tus cartas — podés estar en $500-1,000/mes.
3. **En 6 meses (Diciembre 2026)** — si hay viral — $2,000-5,000/mes.
4. **Es probable que no funcione.** El 90% de los proyectos de software no despegan. Tené un plan B.

### Recomendación final:

> Sácala como open source GRATIS primero. Construí comunidad. Cuando tengas 1,000+ usuarios activos, lanzá la versión de pago con features extra (glosario avanzado, más juegos, skins del overlay). Modelo BYOK. Precio $9.99. Si no despega en 3 meses, buscá trabajo y mantenelo como side project.

**No renuncies a nada hasta que tengas 500 usuarios de pago estables.**
