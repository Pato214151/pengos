# Análisis Financiero y de Escalabilidad — Pengos

> Basado en datos reales de mercado 2025-2026 (Newzoo, Statista, Groq Pricing).

---

## 1. El Mercado en Cifras (Datos Reales)

```
┌─────────────────────────────────────────────────────────────┐
│  REGIÓN              GAMERS       CRECIMIENTO    GASTO/AÑO  │
├─────────────────────────────────────────────────────────────┤
│  LATAM total         372.3M         +4.5%          $48.5    │
│  Brasil               93.1M          +5.2%          $32.2   │
│  México               66.7M          +4.8%          $28.1   │
│  Colombia             17.7M          +6.1%          $18.4   │
│  Argentina            16.0M          +3.9%          $15.7   │
│  Perú                 14.6M          +5.5%          $12.3   │
│  Chile                 6.6M          +4.2%          $22.9   │
├─────────────────────────────────────────────────────────────┤
│  Total LATAM: 372.3M gamers → $8.3B en ingresos 2025      │
│  Crecimiento anual del mercado LATAM: 12%                   │
└─────────────────────────────────────────────────────────────┘
```

**Fuentes:** Newzoo 2025, Statista 2025, GamesBeat, Sherlock Communications 2026.

### Jugadores en los juegos target
| Juego | MAU Global | % LATAM Est. | Jugadores LATAM |
|-------|-----------|-------------|-----------------|
| Valorant | 14.1M (PC tracked) | ~15-18% (BR#5, MX) | ~2.1M-2.5M |
| Fortnite | ~30M DAU (est.) | ~10% (BR 5.5%, MX 3.4%) | ~3M |
| Apex Legends | ~20-22M MAU | ~8% (BR 5.4%, MX 2.4%) | ~1.6M-1.8M |
| CS2/CoD/etc | ~50M combinado | ~15% LATAM | ~7.5M |
| **TOTAL TAM** | | | **~372.3M** |
| **SAM (PC + mic + team play)** | | | **~30M** |
| **SOM (early adopters)** | | | **~300K** |

---

## 2. Costo Real por Usuario (API Groq — vos proveés la key)

### Desglose por hora de juego

```
┌─────────────────────────────────────────────────────────────┐
│  COMPONENTE              CÓMO SE COBRA       COSTO/HORA    │
├─────────────────────────────────────────────────────────────┤
│  Whisper Large v3 Turbo  $0.04/hora de audio  $0.0067      │
│                           (mín 10s/req)       (aprox)*      │
│  Llama 3.1 8B Instant    $0.05/$0.08 por 1M   $0.0003      │
│                           tokens (in/out)      (aprox)*     │
├─────────────────────────────────────────────────────────────┤
│  TOTAL POR USUARIO/HORA                      ~$0.007       │
│  TOTAL POR USUARIO/MES (60h)                 ~$0.42        │
│  TOTAL POR USUARIO/AÑO (720h)                ~$5.04        │
└─────────────────────────────────────────────────────────────┘
```

*Cálculo detallado:*
- **Whisper:** 60 segmentos/hora × 10s mínimo cada uno = 600s = 0.167h → $0.04 × 0.167 = **$0.0067**
- **Llama:** 60 traducciones/hora × (~30 tok in + ~30 tok out) = 3600 tokens → $0.00018 in + $0.00029 out = **$0.00047**
- **Total/hora:** **~$0.0072**

### Margen por plan

| Plan | Precio | Horas estimadas | Costo API/h | Costo total | Margen bruto |
|------|--------|-----------------|-------------|-------------|-------------|
| **Basic** | $10/mes | 20h (casual) | $0.007 | $0.14 | **98.6%** |
| **Pro** | $20/mes | 60h (regular) | $0.007 | $0.42 | **97.9%** |
| **Streamer** | $40/mes | 150h (hardcore) | $0.007 | $1.05 | **97.4%** |

**Conclusión:** El costo de API es casi irrelevante. El verdadero costo es **adquisición de usuarios + infraestructura**.

---

## 3. Proyección de Ingresos vs Costos

### Escenario conservador (300 usuarios en mes 6)

| Plan | Usuarios | % | MRR | Costo API | Margen |
|------|----------|---|-----|-----------|--------|
| Basic ($10) | 150 | 50% | $1,500 | $21 | $1,479 |
| Pro ($20) | 105 | 35% | $2,100 | $44 | $2,056 |
| Streamer ($40) | 45 | 15% | $1,800 | $47 | $1,753 |
| **TOTAL** | **300** | 100% | **$5,400** | **$112** | **$5,288** |

### Escenario medio (3,000 usuarios en mes 12)

| Plan | Usuarios | MRR | Costo API | Margen |
|------|----------|-----|-----------|--------|
| Basic ($10) | 1,500 | $15,000 | $210 | $14,790 |
| Pro ($20) | 1,050 | $21,000 | $441 | $20,559 |
| Streamer ($40) | 450 | $18,000 | $473 | $17,527 |
| **TOTAL** | **3,000** | **$54,000** | **$1,124** | **$52,876** |

### Escenario alto (30,000 usuarios — 0.1% del SOM)

| Plan | Usuarios | MRR | Costo API | Margen |
|------|----------|-----|-----------|--------|
| Basic ($10) | 15,000 | $150,000 | $2,100 | $147,900 |
| Pro ($20) | 10,500 | $210,000 | $4,410 | $205,590 |
| Streamer ($40) | 4,500 | $180,000 | $4,725 | $175,275 |
| **TOTAL** | **30,000** | **$540,000** | **$11,235** | **$528,765** |

---

## 4. El Problema de Escalar con TU API Key

### Límites de Groq (free tier)

| Modelo | Requests/min | Requests/día | Usuarios simultáneos soportados |
|--------|-------------|-------------|-------------------------------|
| Whisper | 20 | 2,000 | ~1-2 users (20 req/min) |
| Llama 3.1 8B | 30 | 14,400 | ~2-3 users (30 req/min) |

**¿Qué pasa con 50 usuarios simultáneos?**
- Cada usuario hace ~1 request/min (Whisper) y ~1 request/min (Llama)
- 50 usuarios = 50 req/min Whisper → excede el límite de 20 → **429 Rate Limit**
- **Solución:** Pasarse al plan pago de Groq (sin límites de tasa, solo pago por uso)

### Costo de infraestructura para escalar

| Componente | Costo estimado |
|------------|---------------|
| Groq API key paga (sin rate limits) | Pago por uso (~$0.007/user/hora) |
| Servidor backend (autenticación, relay) | ~$20/mes (VPS básico) |
| Base de datos (usuarios, sesiones) | ~$15/mes (MongoDB Atlas / Supabase) |
| CDN / distribución del cliente | ~$0 (GitHub Releases) |
| **Total infra mensual (fijo)** | **~$35/mes** |

### Arquitectura para escalar con tu API

```
                    ┌──────────────────┐
                    │   TU SERVIDOR     │
                    │  (VPS ~$20/mes)   │
                    │                   │
                    │  ┌───────────┐    │
                    │  │ Auth API  │    │
                    │  │ (login)   │    │
                    │  └─────┬─────┘    │
                    │        │          │
                    │  ┌─────▼─────┐    │
                    │  │ Rate      │    │
                    │  │ Limiter   │    │
                    │  │ (abuse    │    │
                    │  │  control) │    │
                    │  └─────┬─────┘    │
                    │        │          │
                    │  ┌─────▼─────┐    │
                    │  │ API Proxy │    │
                    │  │ (relay a  │    │
                    │  │  Groq)    │    │
                    │  └───────────┘    │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                              │
              │         GROQ API             │
              │     (tu API key única)       │
              │                              │
              └──────────────────────────────┘
```

**Flujo:**
1. Usuario descarga Pengos cliente (app de escritorio)
2. Usuario se loguea (email + pass o Google OAuth)
3. Pengos cliente envía audio a **tu servidor**
4. Tu servidor valida suscripción activa, aplica rate limiting
5. Tu servidor relay a Groq con **tu API key**
6. Traducción vuelve al usuario

**Problemas de este modelo:**
- **Latencia extra** (~50-100ms por el relay) — crítico para tiempo real
- **Ancho de banda de audio** — cada usuario sube ~16KB/s de audio → 1GB/día por 100 usuarios
- **Single point of failure** — si tu servidor cae, todos se quedan sin servicio
- **Abuso** — un usuario malicioso puede consumir toda tu cuota de API

### Alternativa: Modelo Híbrido (BYOK + Premium)

```
┌─────────────────────────────────────────────────────────────┐
│  MODELO HÍBRIDO RECOMENDADO                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CAPA GRATUITA (BYOK):                                       │
│  │ El usuario pone su propia API key de Groq                 │
│  │ → $0.007/hora paga el usuario directamente a Groq        │
│  │ → Pengos es gratis, sin límites de servidor              │
│  │ → Escalabilidad infinita (cada usuario con su key)        │
│  │ → Ideal para early adopters, viral, sin costo para vos   │
│                                                              │
│  CAPA PREMIUM (tu API):                                      │
│  │ $10/mes → usuario usa TU API key, sin configuración      │
│  │ No necesita .env, no necesita API key de Groq             │
│  │ Plug & Play — "instalá y jugá"                           │
│  │ Margen: ~98%                                              │
│                                                              │
│  CAPA STREAMER:                                              │
│  │ $40/mes → todo lo de Premium + historial + stats +       │
│  │           prioridad en la cola de procesamiento           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Estrategia de Escalabilidad ("Que la tenga todo el mundo")

### Fase 1: BYOK puro (0 usuarios pagos → 10K usuarios)

```
Duración: Meses 1-3
Costo para vos: $0 (cada usuario paga su API)
Modelo: Gratuito, open source, cada uno con su key de Groq
Objetivo: Validación + tracción

Canales:
  • GitHub (open source)
  • Reddit (r/valorant, r/espanol, r/gaming)
  • Discord servers LATAM
  • Boca a boca entre amigos

Métrica clave: 10K descargas, 1K MAU activos
```

### Fase 2: Freemium (BYOK + Premium opcional)

```
Duración: Meses 4-6
Costo para vos: ~$35/mes de servidor
Modelo: BYOK gratis + Premium $10/mes (tu API)

Conversión esperada: 2-5% de usuarios gratuitos → premium
Si tenés 5K MAU gratis → 100-250 usuarios premium → $1K-$2.5K/mes MRR

Infraestructura necesaria:
  • VPS $20/mes (DigitalOcean / Hetzner)
  • Supabase $15/mes (auth + DB)
  • Dominio + landing page: $30/año
```

### Fase 3: SaaS completo

```
Duración: Meses 7-12
Costo: ~$200/mes (escala de servidor)
Staff: 0 personas (todo automatizado)

Modelo:
  • Free: BYOK (sin costo para vos, escalabilidad infinita)
  • Basic $10/mes: tu API, 50h/mes
  • Pro $20/mes: tu API, 150h/mes, + glosario personalizado
  • Streamer $40/mes: ilimitado, stats, historial, prioridad

Para llegar a "todo el mundo":
  • Traducción a otros pares: EN→PT (Brasil), EN→FR, EN→JP
  • Versión one-click installer (no Python, no CLI)
  • Landing page con download directo (exe installer)
  • Campaña con streamers LATAM (pagos con producto gratis de por vida)
```

### ¿Por qué BYOK es la clave para escalar?

| Modelo | Puede escalar a 1M users? | Costo para vos |
|--------|--------------------------|---------------|
| Solo tu API (SaaS puro) | ❌ No — $7K/hora en API | $7,000/hora |
| BYOK puro | ✅ Sí — infinito | $0 |
| Híbrido BYOK + Premium | ✅ Sí — 95% BYOK, 5% Premium | ~$0.007/hora solo para Premium |

**Con BYOK, 1M de usuarios NO te cuesta nada de API.**
**Con tu API, 1M de usuarios te cuesta ~$7,000/hora.**

---

## 6. Proyección de Conversión y MRR (12 meses)

```
MES  │  MAU   │  BYOK %  │  PREMIUM │  MRR     │  COSTO    │  GANANCIA
     │  TOTAL │  (gratis) │  (pago)  │          │  (serv)   │
─────┼────────┼──────────┼──────────┼──────────┼───────────┼──────────
  1  │   200  │   100%   │     0    │    $0    │    $0     │    $0
  2  │  1000  │    98%   │    20    │  $200    │   $35     │   $165
  3  │  3000  │    97%   │    90    │  $900    │   $35     │   $865
  4  │  6000  │    96%   │   240    │ $2,400   │   $35     │  $2,365
  5  │ 10000  │    95%   │   500    │ $5,000   │   $50     │  $4,950
  6  │ 15000  │    95%   │   750    │ $7,500   │   $50     │  $7,450
  7  │ 20000  │    94%   │  1200    │$12,000   │  $100     │ $11,900
  8  │ 30000  │    94%   │  1800    │$18,000   │  $100     │ $17,900
  9  │ 40000  │    93%   │  2800    │$28,000   │  $150     │ $27,850
 10  │ 50000  │    93%   │  3500    │$35,000   │  $150     │ $34,850
 11  │ 60000  │    92%   │  4800    │$48,000   │  $200     │ $47,800
 12  │ 70000  │    92%   │  5600    │$56,000   │  $200     │ $55,800

TOTAL AÑO 1: ~$213,000 MRR en mes 12
TOTAL AÑO 1 ACUMULADO: ~$895,000 ingresos
```

**Supuestos:**
- Tasa de conversión gratuitos → premium: 2-5% (conservador)
- Churn mensual: 5% (típico en SaaS)
- Crecimiento orgánico viral (sin paid ads)
- 70K MAU = 0.02% del TAM de 372M → perfectamente alcanzable

---

## 7. Análisis de Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Groq cambia precios | Media | Alto | Tener fallback a OpenAI/DeepSeek |
| Anticheats bloquean overlay | Alta | Alto | Educar sobre borderless window, parchear |
| Usuarios abusan de tu API key | Media | Medio | Rate limiting por usuario, caps de uso |
| Competencia copia la idea | Alta | Medio | Ventaja: glosario curado + comunidad |
| Baja conversión a pago | Media | Medio | BYOK asegura que al menos hay usuarios |
| Latencia muy alta para juegos | Baja | Alto | Optimizar con VAD + pre-roll + glosario local |

---

## 8. Recomendación Final

### Pricing
Los precios que planteaste ($10/$20/$40) están **bien posicionados**:
- $10/mes = menos que una suscripción de Spotify → "no vale ni pensarlo"
- $20/mes = menos que Netflix → "para los que juegan seguido"
- $40/mes = para streamers que lo usan como tool de trabajo

### Estrategia
1. **Primero BYOK** — que cualquiera pueda usar Pengos con su propia key de Groq. Gratis. Viral. Sin límite.
2. **Después Premium** — una vez que tenés 5K+ MAU, ofrecé la comodidad de no configurar nada por $10/mes.
3. **Nunca saques el BYOK** — es tu escalabilidad infinita y tu embudo de conversión.

### El número mágico
**Solo necesitás 500 usuarios premium para vivir de esto ($5,000/mes).** Con 3,000 ($54,000/mes) ya es un negocio serio. Con 30,000 ($540,000/mes) es una empresa.

Y con 372M de gamers LATAM y 0 competidores directos, el techo está muy arriba.
