# MODELO FINANCIERO — PENGOS
## Proyecciones, costos y puntos de equilibrio

---

## 1. ESTRUCTURA DE COSTOS (MENSUAL)

### Costos fijos (independientes de usuarios)

| Concepto | Costo/mes | Notas |
|----------|-----------|-------|
| Dominio (pengos.app) | $1.50 | anual prorrateado |
| Hosting landing page (Vercel/Netlify) | $0 | gratis |
| Hosting API de licencias (Railway/Render) | $5-7 | si usás backend para validación |
| Certificado de firma de código | $17 | $200/año, solo si querés evitar antivirus |
| **Total fijos** | **~$8.50-25.50/mes** | |

### Costos variables (por usuario activo con API de él — $0)

| Concepto | Costo | Notas |
|----------|------|-------|
| Procesamiento de pago (MercadoPago 4.9% + $0.30) | $0.79/venta de $9.99 | |
| **Total variable** | **~7.9% del ingreso** | |

---

## 2. PROYECCIÓN MENSUAL — 3 ESCENARIOS

### Supuestos compartidos
- Conversión descarga → compra: 10% del total de descargas
- BYOK: el usuario pone su API key → $0 costo API para vos
- Precio: $9.99 one-time

### Escenario A: PESIMISTA — "No despega"

| Mes | Descargas | Licencias vendidas | Ingreso | Costos | Ganancia | Acumulado |
|-----|-----------|-------------------|---------|--------|----------|-----------|
| 1 | 100 | 10 | $100 | $9 | **$91** | $91 |
| 2 | 80 | 8 | $80 | $9 | **$71** | $162 |
| 3 | 60 | 6 | $60 | $9 | **$51** | $213 |
| 4 | 50 | 5 | $50 | $9 | **$41** | $254 |
| 5 | 40 | 4 | $40 | $9 | **$31** | $285 |
| 6 | 30 | 3 | $30 | $9 | **$21** | $306 |

**Total 6 meses: $306 ganados.** No alcanza ni para un mercado. **Buscá trabajo.**

### Escenario B: REALISTA — "Viral moderado en gaming colombiano"

**Premisa:** Video de TikTok/YouTube con 50k views, + buena recepción en comunidades.

| Mes | Descargas acum. | Licencias/mes (10% de descargas nuevas) | Ingreso/mes | Costos | Ganancia/mes |
|-----|----------------|----------------------------------------|-------------|--------|-------------|
| 1 | 300 | 30 | $300 | $24 | **$276** |
| 2 | 800 | 50 | $500 | $40 | **$460** |
| 3 | 2,000 | 120 | $1,199 | $95 | **$1,104** |
| 4 | 3,500 | 150 | $1,499 | $119 | **$1,380** |
| 5 | 5,000 | 150 | $1,499 | $119 | **$1,380** |
| 6 | 7,000 | 200 | $1,998 | $159 | **$1,839** |

**Total 6 meses: $6,439 ganados.**
- Mes 3: ya estás en $1,104/mes → **vivís ajustado en Colombia**
- Mes 6: $1,839/mes → **vivís tranquilo en Colombia**
- **Pero la curva se aplanó: necesitás otro golpe viral**

### Escenario C: OPTIMISTA — "Viral fuerte + streamers"

**Premisa:** Streamer colombiano grande (Zerato, Pipa, etc.) lo muestra + TikTok llega a 500k views.

| Mes | Descargas acum. | Licencias/mes | Ingreso/mes | Ganancia/mes |
|-----|----------------|--------------|-------------|-------------|
| 1 | 1,000 | 100 | $999 | **$919** |
| 2 | 5,000 | 400 | $3,996 | **$3,676** |
| 3 | 15,000 | 1,000 | $9,990 | **$9,190** |
| 4 | 35,000 | 2,000 | $19,980 | **$18,380** |
| 5 | 60,000 | 2,500 | $24,975 | **$22,975** |
| 6 | 100,000 | 4,000 | $39,960 | **$36,760** |

**Total 6 meses: $91,900 ganados.** Ya vivís y contratás gente. Pero esto es MUY improbable sin suerte viral.

---

## 3. PUNTO DE EQUILIBRIO

### Costo de vida COLOMBIA 2026 (datos reales)

| Concepto | Vida austera | Vida cómoda |
|----------|-------------|-------------|
| Arriendo (habitación/apartamento) | $150-200 | $300-450 |
| Comida | $150-200 | $250-350 |
| Servicios (luz, agua, internet) | $50-70 | $80-120 |
| Transporte | $30-50 | $50-100 |
| Salud (EPS) | $30-40 | $60-80 |
| Ocio/Extras | $40-60 | $100-200 |
| **TOTAL MENSUAL** | **~$450-620** | **~$840-1,300** |

### Licencias necesarias para cubrir gastos

**Modelo BYOK ($9.99/licencia, después de fees ~$9.20/licencia):**

| Escenario de vida | Ingreso necesario/mes | Licencias/mes | Ventas/día |
|-------------------|---------------------|---------------|------------|
| Sobrevivir (arriendo compartido, arroz+huevo) | $450 | **49 licencias** | ~2/día |
| Vida austera (habitación propia, mercado básico) | $600 | **66 licencias** | ~2-3/día |
| Vida cómoda (apto propio, salidas, ahorro) | $1,000 | **109 licencias** | ~4/día |
| Vida buena (ahorro, viajes, darse gustos) | $1,500 | **164 licencias** | ~5-6/día |
| Vida muy buena (departamento bueno, carro, ahorro) | $2,500 | **273 licencias** | ~9-10/día |

---

## 4. CÁLCULO DE CHURN Y LTV

### Lifecycle del cliente

| Métrica | Valor estimado | Fuente |
|---------|---------------|--------|
| Churn mensual | 15% | Benchmark apps de gaming |
| Vida útil promedio del cliente | ~6.7 meses | 1/0.15 |
| Licencias por cliente | 1 (one-time) | Modelo actual |
| LTV (Lifetime Value) | $9.99 | Sin upsells |
| CAC (Costo de adquisición) | $0 (orgánico) | Ideal |
| Payback period | 1 mes | Inmediato |

### Si agregás upsells (Modelo B + C):

| Producto | Precio | Tasa de conversión | LTV adicional |
|----------|--------|-------------------|---------------|
| Licencia base | $9.99 | 100% | $9.99 |
| Glosario premium (DLC de términos) | $4.99 | 20% | $1.00 |
| Suscripción API incluida | $3.99/mes | 10% | ~$3.99 × 6.7 = $26.73 |
| **LTV total posible** | | | **~$37.72** |

---

## 5. ¿CUÁNDO DEJAR EL TRABAJO?

### Regla de los 3 meses de colchón

Necesitás tener **ahorrado para 3 meses de vida** antes de dedicarte full-time.

| Escenario de vida | Colchón necesario | Ingreso mensual de Pengos | Tiempo estimado para lograrlo |
|-------------------|------------------|--------------------------|------------------------------|
| Vida austera | $1,350-1,860 | $600+ | Mes 3-4 (realista) |
| Vida cómoda | $2,520-3,900 | $1,000+ | Mes 4-5 (realista) |

### Señales para saber si renunciar o no:

**🚩 RENUNCIÁ SOLO SI:**
- [ ] 3+ meses seguidos de crecimiento sostenido (>20% mes a mes)
- [ ] Ingresos mensuales > tus gastos mensuales * 1.5
- [ ] Tenés 3 meses de ahorros aparte
- [ ] El churn no está aumentando
- [ ] Tenés un plan para el próximo golpe (nueva feature, campaña, etc.)

**✅ QUEDATE CON TRABAJO + PENGOS SI:**
- Crecimiento es plano o bajando
- Dependés de un solo viral
- No tenés ahorros
- Los ingresos no cubren ni el arriendo

---

## 6. KPIS PARA MEDIR CADA SEMANA

| KPI | Cómo medirlo | Meta semanal (realista) |
|-----|-------------|----------------------|
| Descargas nuevas | Contador en landing page | 50-200/semana |
| Licencias vendidas | Backend de licencias | 5-30/semana |
| Tasa de conversión (descarga→compra) | Analytics | >5% |
| Revenue | Stripe/MercadoPago | $50-300/semana |
| Usuarios activos (que usan >1h/semana) | Telemetry opcional | >30% de descargas |
| Community Discord | Miembros en server | +50/semana |
| TikTok/YouTube views | Analytics | 5k-50k/semana |

---

## 7. SIMULACIÓN: SI TIRÁS ADS

Con $100/mes en ads (Google Ads + TikTok Ads):

| Inversión | Impresiones | Clicks (2% CTR) | Descargas (5% conversión) | Licencias (10%) | Ingreso | ROI |
|-----------|------------|-----------------|--------------------------|-----------------|---------|-----|
| $100/mes | 50,000 | 1,000 | 50 | 5 | $49.95 | **-$50** |

**Conclusión:** Con $100/mes de ads no llegás a positivo. Necesitás:
- O ads muy dirigidos (gente buscando "traductor gaming" — búsqueda específica, no hay mucho tráfico)
- O viral orgánico

**No recomiendo invertir en ads hasta que tengas >$1,000/mes de revenue orgánico.**
