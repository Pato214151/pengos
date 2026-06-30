# VALIDACIÓN — Posts listos para copiar/pegar (H1 + H2)

Objetivo: medir **interés real** esta semana, gratis. No vendemos nada todavía —
medimos si a la gente le importa y si dejaría su email.

**Antes de postear necesitás 2 cosas:**
1. Un **clip de 20-40s** mostrando Pengos funcionando en una partida real (Valorant/Apex).
   Sin video, los posts rinden 10x menos. Grabalo con la captura de Windows (Win+G) o OBS.
2. La **landing publicada** (ver "Cómo publicar la landing" abajo) para tener el link.

---

## MÉTRICAS — cuándo es ✅ y cuándo es ❌ (de tu plan)

| Señal | ✅ Validado | ❌ Fracaso |
|---|---|---|
| Reacción en comunidades (H1) | ≥100 upvotes combinados **o** ≥50 en Discord **o** ≥20 "me interesa" | <20 upvotes, <10 Discord, comentarios mayormente negativos |
| Emails en la landing (H2) | ≥50 emails en 2 semanas | <10 emails en 2 semanas |

Si H1 y H2 fallan → el problema no duele tanto como creemos. No seguís invirtiendo tiempo.

---

## POST 1 — r/Valorant / subs de gaming en inglés (LATAM en NA servers)

> ⚠️ Reddit odia el autospam. Reglas: leé las normas del sub, NO pongas el link en el
> título, respondé TODOS los comentarios, y si el sub tiene hilo semanal de "self-promo"
> o "feedback", usá ese. Mejor pedir feedback que vender.

**Título:**
`I built a real-time voice translator overlay for LATAM players stuck on NA servers — looking for feedback`

**Cuerpo:**
```
Soy dev y jugador. Como muchos latinos, juego en servers de NA y a veces no entiendo
los callouts de mis compañeros gringos a tiempo ("he's one shot", "rotate", "save").

Armé un overlay que escucha la voz del equipo y la traduce a español EN VIVO encima del
juego, y cuando hablo yo en español lo pasa a inglés. Está tuneado para callouts de
Valorant/Apex, no es un traductor genérico.

[acá va tu clip de 20-40s]

No estoy vendiendo nada — quiero saber si a alguien más le sirve esto o si soy solo yo.
¿Lo usarían? ¿Qué le falta?

(dejé una página por si quieren que les avise cuando esté: [link a tu landing])
```

---

## POST 2 — r/Colombia, r/VALORANT en español, Discords/Facebook de gaming latino

**Título:**
`Programé un overlay que traduce la VOZ de tus compañeros gringos en Valorant/Apex — ¿les serviría?`

**Cuerpo:**
```
Qué más parceros. Soy dev colombiano y jugador. Me cansé de jugar en servers gringos y
no entender los callouts a tiempo, así que me armé un overlay que:

- Escucha a tu equipo en inglés y te lo muestra en español ENCIMA del juego, en vivo.
- Cuando hablás vos en español, lo pasa a inglés (lo copia para pegar en el chat).
- Entiende jerga de verdad: callouts de Valorant/Apex y hasta slang colombiano
  ("una nota", "regular" = mediocre, etc.), no traduce robótico.

[acá va tu clip de 20-40s en una partida real]

No estoy vendiendo nada todavía — necesito saber si esto le sirve a alguien más o si
estoy loco. ¿Lo usarían? ¿En qué juego les haría más falta?

Dejé una página por si quieren que les avise cuando salga 👉 [link a tu landing]
```

---

## POST 3 — versión corta para Discord / WhatsApp / grupos de Facebook

```
Parceros, armé un programa que traduce la VOZ de tus compañeros gringos en Valorant/Apex
en tiempo real (y tu voz al inglés). ¿Les serviría algo así? 👀
Acá un clip 👇 [video]  ·  si quieren que les avise: [link landing]
```

---

## CÓMO PUBLICAR LA LANDING (gratis, 5 min)

1. **Email del formulario:** entrá a https://formspree.io, creá una cuenta gratis,
   creá un form, copiá tu endpoint (algo como `https://formspree.io/f/abcd1234`) y
   reemplazá `REEMPLAZA_TU_ID` en `docs/landing/index.html`.
2. **Publicar (elegí una):**
   - **Netlify Drop** (lo más fácil): andá a https://app.netlify.com/drop y arrastrá
     la carpeta `docs/landing`. Te da un link al instante.
   - **GitHub Pages:** subí el repo, Settings → Pages → carpeta `/docs` → te da una URL.
   - **Vercel:** importás el repo y listo.
3. **Discord:** creá un server, sacá un link de invitación permanente y reemplazá los
   `href="#"` de `id="discord-link"` en la landing.
4. **(Opcional) GitHub:** si lo subís open source, poné el link en `id="gh-link"`.

---

## QUÉ MEDIR CADA DÍA (anotalo, son tus datos REALES)

- Views del clip (TikTok/YouTube/Reddit)
- Upvotes / comentarios / "me interesa"
- Miembros nuevos en Discord
- **Emails en Formspree** ← la métrica más importante (interés con fricción real)

En 2 semanas tenés más verdad que en 4 documentos de proyecciones. Si la señal es buena,
recién ahí vale la pena invertir más. Si no, ya lo sabés barato.
