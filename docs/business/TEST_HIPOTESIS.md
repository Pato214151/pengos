# TEST DE HIPÓTESIS — PENGOS
## Experimentos para validar el negocio antes de tiempo completo

---

Cada hipótesis tiene un experimento diseñado para **falsarla**. Si falla, no seguís perdiendo tiempo. Si pasa, avanzás con confianza.

---

## H1: "Gamers colombianos necesitan esto"

### Experimento: Post en comunidades

**Día 1:** Posteá en estos lugares exactos:

| Canal | Qué postear | Timing |
|-------|------------|--------|
| r/Colombia | "Programé un overlay que traduce VOZ de tus compañeros gringos en Valorant — ¿les sirve?" | Lunes 10am |
| r/Valorant | "Free real-time voice translation overlay EN↔ES for LATAM players — any interest?" | Lunes 10am |
| Discord "Valorant Colombia" | Mostrar video de 30s funcionando | Lunes 8pm (hora pico gaming) |
| Grupos Facebook "Gamers Colombia" | Mismo video + link | Lunes 8pm |

**Métrica de éxito:** ✅ ≥100 upvotes combinados O ≥50 personas en Discord nuevo O ≥20 "me interesa" en comentarios.

**Métrica de fracaso:** ❌ <20 upvotes, <10 personas en Discord, comentarios negativos mayoritarios.

**Si falla:** Repensá el nicho. Quizás el problema no es tan grave como creés. Probá en Apex Legends o CS2.

---

## H2: "La gente pagaría $9.99 por esto"

### Experimento: Landing page + pre-venta

**Día 8:** Creá una landing page simple (puede ser Carrd o incluso un post de Twitter/X bien hecho):

```
PENGOS — Overlay de traducción de voz para gaming
- EN → ES en tiempo real
- ES → EN con slang colombiano
- Funciona en Valorant, Apex, CS2
- No afecta FPS
$9.99 one-time (sin suscripción)

[Registrame para el lanzamiento]
```

**No necesitás el producto listo para vender.** Solo medí cuántos ponen su email.

**Métrica de éxito:** ✅ ≥50 emails en 2 semanas (conversión de ~5% de visitantes).

**Métrica de fracaso:** ❌ <10 emails en 2 semanas.

**Si falla:** El precio es muy alto. Probá a $4.99, o cambiá a free con donaciones. También podría ser que el marketing no está llegando a la audiencia correcta.

---

## H3: "El diferenciador colombiano importa"

### Experimento: Video A/B test

Creá 2 videos de TikTok/YouTube Shorts de 30s:

| Video A (inglés genérico) | Video B (jerga colombiana) |
|---|---|
| "Traduce tus compañeros gringos en tiempo real" | "Escuchás 'he's one shot' y ves 'está a un tiro' — parce, esto es una nota" |
| Mismo gameplay | Mismo gameplay |
| Sin acento colombiano | Con vos hablando colombiano |

**Métrica de éxito:** ✅ Video B tiene ≥2x los views/likes/compartidos del Video A.

**Métrica de fracaso:** ❌ Video B rinde igual o peor que A.

**Si falla:** No subestimes la estrategia; capaz el nicho colombiano no es el diferenciador que creés. Probá con "gamer LATAM" genérico sin slang específico.

---

## H4: "La gente descarga y lo usa"

### Experimento: Beta gratuita

**Día 15:** Lanzá la versión gratuita con BYOK.

| Semana | Usuarios que descargaron | Usuarios que completaron 1+ partida | Tasa retención |
|--------|------------------------|-------------------------------------|----------------|
| 1 | 100 | — | — |
| 2 | 200 | 60 (de los 100) | 60% |
| 3 | 350 | 80 (de los que quedan) | 40% |
| 4 | 500 | 75 | 30% |

**Métrica de éxito:** ✅ Retención semanal >40% y 500+ descargas en el primer mes.

**Métrica de fracaso:** ❌ Retención <20% o <100 descargas en el primer mes.

**Si falla:** El producto tiene un problema de UX, latencia, o simplemente no es tan útil como pensabas. Necesitás feedback de usuarios para entender por qué.

---

## H5: "Los usuarios pagan por la licencia"

### Experimento: Conversión gratis → pago

**Día 30:** Agregá el modelo de licencia. Los usuarios gratuitos ven un banner:

```
🟢 Traduciendo (gratis)
🔒 Glosario expandido + skins del overlay + soporte prioritario por $9.99
```

**No bloquees nada.** Que el gratis sea 100% funcional. La licencia es más bien un "apoyo al desarrollo" con perks estéticos.

**Métrica de éxito:** ✅ ≥5% de usuarios activos compran en el primer mes.

**Métrica de fracaso:** ❌ <1% compra.

**Si falla:** El valor percibido no alcanza. Probá diferentes precios ($4.99, $14.99) y diferentes perks. O cambiá a modelo de donaciones + Patreon en vez de licencia forzada.

---

## H6: "Crece orgánicamente por referidos"

### Experimento: Programa de referidos

**Día 45:** Implementá un sistema simple: "Compartí tu código único, por cada amigo que compre recibís 1 mes de glosario premium gratis."

**Métrica de éxito:** ✅ ≥1 referido por cada 10 compradores.

**Métrica de fracaso:** ❌ Casi nadie comparte.

**Si falla:** El incentivo no es suficiente, o la gente no siente que vale la pena recomendar. Probá con comisión en efectivo o con features exclusivas para el que refiere.

---

## TIMELINE DE VALIDACIÓN (DÍAS 1-60)

```
Día 1  ─ H1: Post en comunidades
Día 8  ─ H2: Landing page + pre-venta
Día 15 ─ H3: Video A/B test TikTok
Día 30 ─ H4: Beta gratuita
Día 45 ─ H5: Agregar licencias de pago
Día 60 ─ H6: Programa de referidos

Puntos de decisión:
├─ Día 15: Si H1 + H2 fallan → parar, esto no funciona
├─ Día 30: Si H3 + H4 flaquean → pivotear a otro nicho
├─ Día 45: Si H5 no convierte → cambiar modelo de precios
└─ Día 60: Si H6 no funciona → necesitás invertir en ads
```

---

## ¿CÓMO SABER SI SEGUIR O NO?

### REGLA DEL 80/20

Después de 60 días, evaluá:

| Si tenés... | Conclusión |
|------------|-----------|
| <100 usuarios activos y <$200 ganados | **Pará.** Esto no despegó. Buscá trabajo y mantenelo como hobby. |
| 100-500 usuarios y $200-$1,000/mes | **Side project.** Seguí pero sin dejar el trabajo. Prometedor pero no seguro. |
| 500+ usuarios y >$1,000/mes | **Full time.** Renunciá solo si tenés 3 meses de ahorros y la curva sube. |
| 2000+ usuarios y >$3,000/mes | **Escalá.** Contratá ayuda, expandí a más juegos, invertí en marketing. |

### UNA COSA MÁS

Si después de 60 días tenés **menos de $200** ganados, no lo veas como fracaso. Son $200 que no tenías antes. Seguí codeando, mejorá el producto, y esperá tu momento. El próximo viral puede llegar en 6 meses sin avisar.
