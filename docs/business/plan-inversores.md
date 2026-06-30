# Plan de Inversión y Donación — Pengos

> Buscar inversores, donadores, grants y financiamiento para Pengos.

---

## 1. Mi Opinión del Proyecto (Re-Review Mayo 2026)

### Estado actual

Ya usaste Pengos en partidas reales y los logs de `historial/` lo confirman:
- Traducciones en vivo funcionando
- ~200 traducciones por sesión de GTA RP
- Modo escucha (F4) + modo mic (F5) funcionando
- Historial ya implementado y guardando a JSONL

### Lo que está sólido

| Aspecto | Estado |
|---------|--------|
| Pipeline VAD → Whisper → filtros → glosario → Llama | ✅ Funcional |
| Overlay transparente + auto-hide + pin | ✅ Funcional |
| Frases rápidas + hotkeys | ✅ Funcional |
| Historial de sesión (JSONL) | ✅ Implementado |
| Filtro antialucinaciones | ✅ Robusto |
| Dedup + rate limiting | ✅ Funcional |
| 500+ términos en glosario | ✅ Cargado |
| Tests automatizados (6 suites) | ✅ Pasando |

### Lo que necesita mejora (que ya identificaste)

| Problema | Prioridad |
|----------|-----------|
| Precisión de Whisper en términos específicos | Alta |
| Overflow del overlay (texto se corta en 520px) | Alta |
| Saturación de pantalla (muchas líneas tapan el juego) | Alta |
| Instalación requiere Python + CLI (barrera de entrada) | Media |

### El gap real

El proyecto técnicamente funciona. El gap no es técnico — **es distribución y UX**. La app existe, traduce bien, pero:
- Solo vos y unos pocos pueden usarla (requiere Python, CLI, VB-CABLE)
- No hay un installer one-click
- No hay landing page
- No hay onboarding automatizado
- No hay métricas de uso

---

## 2. ¿Qué Opciones Hay para Conseguir Financiamiento?

```
┌──────────────────────────────────────────────────────────────────┐
│                      OPCIONES DE FINANCIAMIENTO                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DONACIONES (Open Source / Patreon / Ko-fi)                   │
│  2. GRANTS / ACELERADORAS (Google for Startups, YC, etc.)       │
│  3. INVERSIÓN ÁNGEL (AngelList, family office)                   │
│  4. VENTA DIRECTA (SaaS: BYOK gratis + Premium)                 │
│  5. BOOTSTRAPPING (crecimiento orgánico, $0 invertido)          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Opción 1: Donaciones (Patreon / Ko-fi / GitHub Sponsors)

### Cómo funciona
- Pengos es open source
- La gente te dona porque **el proyecto les resolvió un problema real**
- Plataformas: GitHub Sponsors (0% fees 1er año), Ko-fi, Patreon, Buy Me a Coffee

### Pros
- ✅ Sin presión de dar equity
- ✅ Validación directa del usuario → si donan, es que sirve
- ✅ Comunidad se forma alrededor del proyecto
- ✅ Sin expectativas de crecimiento forzado

### Contras
- ❌ El latinoamericano promedio no dona (cultura de "gratis")
- ❌ Teto bajo (~$200-500/mes en el mejor caso)
- ❌ Requiere visibilidad constante (posts, updates, comunidad)

### Qué necesitás para que funcione

```
1. VISIBILIDAD
   └── Posteá en r/valorant, r/espanol, r/gaming
       "Hice un overlay que traduce inglés a español en vivo"
   └── Incluí link a GitHub Sponsors / Ko-fi

2. PROBAR QUE FUNCIONA
   └── Video corto (30s) de partida real con overlay funcionando
   └── Mostrar el antes/después

3. PEDIR LA DONACIÓN
   └── "Si esto te salvó una partida, invitame un café → link"
   └── "Pengos corre con mi propia API key, cada hora de uso me cuesta"
```

### Plataformas recomendadas

| Plataforma | Fee | Ideal para |
|------------|-----|------------|
| GitHub Sponsors | 0% (1er año) | Devs open source |
| Ko-fi | 0% (fijo) | Donaciones únicas |
| Patreon | 5-12% | Suscripciones mensuales |
| Buy Me a Coffee | 5% | Donaciones rápidas |

**Estimado realista:** $50-300/mes en donaciones, depende de tu alcance.

---

## 4. Opción 2: Grants / Aceleradoras (Recomendado)

### ¿Qué son?
Organizaciones que dan **dinero no reembolsable** (grants) o **inversión + mentorship** (aceleradoras) para proyectos con impacto.

### Grants disponibles para LATAM / Gaming / AI

```
┌─────────────────────────────────────────────────────────────┐
│  PROGRAMA                MONTO        REGIÓN    ENFOQUE     │
├─────────────────────────────────────────────────────────────┤
│  Google for Startups     $100K+       LATAM     AI + impacto│
│    (Latam Founders Fund)  créditos                           │
│  Microsoft AI for Good   $50-250K     Global    AI social    │
│  Nvidia Inception        $5K-100K     Global    AI + gaming  │
│    (+ GPU credits)                                          │
│  GitHub Accelerator      $20K+        Global    Open Source  │
│  Epic MegaGrants         $10-500K     Global    Unreal/gaming│
│  Y Combinator            $500K+       Global    Startups     │
│    (YC Startup School)                                       │
│  IDB Lab (BID)           $50-200K     LATAM     Tecnología  │
│  Startup Chile            $40K+       LATAM     Startups     │
│  Corfo (Chile)           $25-100K     Chile     Innovación   │
│  iNNpulsa (Colombia)     $10-50K      Colombia  Emprend.     │
│  Aceleradora de Apps.co  $10-20K      Colombia  Tech         │
└─────────────────────────────────────────────────────────────┘
```

### ¿Por qué Pengos califica para grants?

```
✅ INNOVACIÓN TECNOLÓGICA
   Overlay + VAD + Whisper + Llama + glosario
   No hay nada igual en el mercado

✅ IMPACTO SOCIAL
   Derriba la barrera del idioma para 372M gamers LATAM
   Inclusión digital de hispanohablantes en gaming global

✅ OPEN SOURCE
   Preferido por la mayoría de los grants
   Democratiza el acceso a AI

✅ AI / MACHINE LEARNING
   Usa Groq Whisper + Llama
   Tiene potencial para fine-tuning propio

✅ LATAM FOCUS
   Resuelve un problema LATAM
   Fundador LATAM
```

### Cómo aplicar a grants (paso a paso)

```
SEMANA 1-2: Preparación
└── Crear landing page del proyecto
└── Armar deck de 10 slides
└── Grabar demo funcional (video 2 min)
└── Escribir 1-pager (qué es, problema, solución, tracción)

SEMANA 3-4: Aplicaciones
└── Google for Startups: apply.googleforstartups.com
└── GitHub Accelerator: accelerator.github.com
└── Nvidia Inception: nvidia.com/inception
└── Epic MegaGrants: epicgames.com/megagrants

SEMANA 5-8: Seguimiento
└── Emails de follow-up a cada aplicación
└── Mejorar deck según feedback
└── Publicar en Product Hunt para tracción
```

### Qué debe decir el deck (estructura)

```
Slide 1:  Penguin — Traducción de voz en tiempo real para gaming
Slide 2:  300M gamers LATAM no entienden inglés → pierden partidas
Slide 3:  Overlay transparente: escuchás inglés, ves español
Slide 4:  Demo: 30s de gameplay con overlay funcionando
Slide 5:  Arquitectura: VAD + Whisper + filtros + glosario + Llama
Slide 6:  Tracción: logs reales de partidas, ~200 traducciones/sesión
Slide 7:  Costo: ~$0.007/hora por usuario (99% margen en Premium)
Slide 8:  TAM: 372M gamers LATAM → SAM: 30M PC → SOM: 300K
Slide 9:  Monetización: BYOK gratis + Premium $10/mes
Slide 10: Roadmap: installer 1-click, más idiomas, modo streamer
```

---

## 5. Opción 3: Inversión Ángel / Venture Capital

### ¿Cuándo buscar inversión?
NO ahora. Buscar inversión sin tracción es perder tiempo.

### Checklist para inversión

```
[ ] 1,000+ usuarios activos (MAU)
[ ] Tasa de retención >30% día 7
[ ] MRR > $1,000/mes
[ ] Crecimiento orgánico consistente
[ ] Demo que funciona sin bugs visibles
[ ] Equipo dedicado (full-time)
[ ] Proyección clara de uso de fondos
```

### Si cumplís el checklist, ¿dónde buscar?

| Tipo | Plataforma | Ticket promedio |
|------|------------|-----------------|
| Ángel LATAM | angelinvestmentnetwork.com | $10K-100K |
| Ángel US | AngelList | $25K-500K |
| VC Seed | Y Combinator, 500 Startups | $500K-2M |
| VC LATAM | Kaszek, Monashees, Canary | $500K-5M |

### ¿Cuánto pedir?

```
Escenario: 3,000 usuarios, $54K MRR → ~$648K ARR
Valuación típica SaaS: 5-10x ARR = $3.2M - $6.4M
Inversión recomendada: $300K-$500K (15-20% equity)

Uso de fondos sugerido:
  ┌────────────────────────────────────┐
  │ Full-stack developer     $120K     │
  │ Marketing + ads          $100K     │
  │ Infraestructura          $40K      │
  │ Instalador 1-click       $30K      │
  │ Legal + contabilidad     $10K      │
  │ Reserve                  $200K     │
  └────────────────────────────────────┘
```

---

## 6. Opción 4: Bootstrapping (Auto-sustentarse)

### La ruta más realista para Pengos

```
MES 1-3:  0 usuarios → $0
          Solo invertís tiempo
          Objetivo: 100 usuarios BYOK (gratis)

MES 4-6:  1,000 MAU → 20 premium → $200/mes
          $200 cubre servidor + API + café
          Objetivo: 5K MAU

MES 7-12: 10K MAU → 200 premium → $2K/mes
          YA podés vivir de esto
          Objetivo: 30K MAU

MES 12-18: 30K+ MAU → 600+ premium → $6K+/mes
           Ingreso cómodo. Contratar ayuda.
```

### ¿Cuánto necesitás realmente?

```
MÍNIMO PARA VIVIR (si estás en LATAM):
  ─────────────────────────────────────
  $500/mes  = comida + internet + servicios
  $1,000/mes = lo mismo + salir + ahorro
  $2,000/mes = cómodo + darse gustos

USUARIOS PREMIUM NECESARIOS:
  $500/mes  → 50 premium ($10 c/u) → 2,500 MAU
  $1,000/mes → 100 premium → 5,000 MAU
  $2,000/mes → 200 premium → 10,000 MAU
```

---

## 7. Recomendación Final — ¿Qué Hacer?

### Mi recomendación: Bootstrapping + Donaciones + Grants (en ese orden)

```
FASE 1 (AHORA — MES 1): Bootstrapping + Donaciones
└── NO busques inversión aún
└── Publicá en Reddit (r/valorant, r/espanol)
└── Poné GitHub Sponsors + Ko-fi
└── Objetivo: 100 usuarios BYOK
└── Esto no te cuesta nada

FASE 2 (MES 2-3): Grants
└── Aplicá a GitHub Accelerator + Google for Startups
└── Pedí $10K-$20K para desarrollo del installer 1-click
└── Con eso arreglás overhead + UX + distribución

FASE 3 (MES 4-6): Evaluar
└── Si tenés 5K+ MAU y $1K+/mes MRR → podés vivir de esto
└── Si no, decidí si seguís como hobby o buscás inversión
```

### ¿Donaciones o inversión?

| Si querés | Hacé |
|-----------|------|
| Que sea un proyecto open source que ayude a la comunidad | Donaciones (Ko-fi / GitHub Sponsors) |
| Que sea un negocio y vivir de esto | Premium SaaS + eventual inversión |
| Crecimiento rápido (5K+ usuarios en 3 meses) | Grants + aceleradora |
| No depender de nadie, ir lento pero seguro | Bootstrapping puro |

### Mi opinión honesta

Pengos técnicamente funciona y resuelve un problema real. Pero **hoy no es invertible** porque:
1. Cero usuarios (solo vos)
2. Cero ingresos
3. Distribución inexistente (solo funciona si sabés Python)

**Lo que sí podés hacer AHORA mismo:**

1. **Publicá en Reddit** — r/valorant, r/espanol, r/gaming. Mostrá un video de 30s del overlay funcionando. Poné link a GitHub con instrucciones BYOK. Esto te da los primeros 100 usuarios SIN GASTAR UN PESO.

2. **Poné GitHub Sponsors** — si a 100 personas les sirve, aunque sea 1-2 van a donar. Es gratis y no perdés nada.

3. **Aplicá a GitHub Accelerator** — la convocatoria es continua, $20K para open source. Pengos califica.

4. **Prepará el installer 1-click** — mientras más fácil sea probarlo, más usuarios. Esa es la verdadera inversión.

**TL;DR:** No necesitás inversión. Necesitás usuarios. Conseguí 100 usuarios primero, después hablamos de money.
