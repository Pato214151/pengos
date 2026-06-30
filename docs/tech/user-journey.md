# User Journey — Pengos

> Versión 1.1 | Fecha: 2026-04-28

> **Nota de latencia (pendiente validar):** Groq Whisper devuelve transcripción en ~0.5–1s, más ~0.3–0.5s de traducción. Total real: **1–2 segundos**. En juegos de reacción rápida (Valorant, Fortnite) esto puede ser tarde para algunas frases críticas. Los escenarios abajo asumen latencia aceptable — esto hay que medirlo con testing real en partida antes de darlos por válidos.

---

## Escenario 1: Escucha pasiva en Fortnite (dúo con americano)

**Quién:** Carlos, jugador latinoamericano, Fortnite servidor NA.  
**Situación:** Le toca un dúo al azar. El compañero habla inglés por micrófono.

| Paso | Acción | Lo que pasa con Pengos | Emoción |
|------|--------|------------------------|---------|
| 1 | Entra a la partida | Activa Pengos antes de lanzar Fortnite. El overlay está corriendo en segundo plano, invisible hasta que haya algo que mostrar. | Listo, no nervioso. |
| 2 | El compañero dice: "I'm landing at Mega City, follow me." | El overlay muestra abajo a la izquierda: **"Aterrizo en Mega City, sígueme."** | Entiende al instante. Pica hacia allá. No se separan. |
| 3 | En combate, el compañero dice: "Push left, he's low!" | Overlay: **"Presioná por la izquierda, está con poca vida."** | Reacciona a tiempo. |
| 4 | Terminan la partida bien | El compañero dice: "Nice game!" | Overlay: **"¡Buena partida!"** Carlos responde con un emoji en el chat. Ya no necesita esconderse. |

**Resultado:** De "no entendí nada" a "jugué como si habláramos el mismo idioma."

---

## Escenario 2: Respuesta activa — necesita escudo

**Quién:** Carlos, en una partida de Valorant, con su amigo y un gringo random.  
**Situación:** Carlos está a punto de morir, necesita curarse o que le pasen escudo.

| Paso | Acción | Lo que pasa con Pengos | Emoción |
|------|--------|------------------------|---------|
| 1 | Carlos se queda sin escudo en plena ronda | — | Pánico. Sabe lo que necesita pero no sabe cómo pedirlo. |
| 2 | Presiona F2 (hotkey de Pengos) | Se abre un mini-campo de texto sobre el overlay, pequeño, sin tapar el juego. | Un segundo de calma. |
| 3 | Escribe rápido: **"dame escudo"** y presiona Enter | Pengos muestra: **"I need shield"** y lo copia al portapapeles automáticamente. | Confía en que la frase es natural. |
| 4 | Carlos pega en el chat del juego | El gringo lee, le lanza un escudo. | Salvado. No murió por falta de comunicación. |

**Resultado:** La barrera del idioma dejó de ser la razón por la que murió.

---

## Escenario 3: Quiere decir algo más que un insulto

**Quién:** Carlos, en Fortnite. Lo eliminaron con una jugada difícil.  
**Situación:** Quiere felicitar al rival o responder algo ingenioso, no solo "su mama".

| Paso | Acción | Lo que pasa con Pengos | Emoción |
|------|--------|------------------------|---------|
| 1 | Lo eliminan con un buen tiro | Antes no tenía palabras. Solo el insulto genérico de siempre. | Frustración vieja. |
| 2 | Presiona F2, escribe: **"bien jugado eso estuvo dificil"** | Pengos devuelve: **"Nice shot, that was a tough one."** | Sonríe. |
| 3 | Lo pega en el chat | El rival le responde con un "gg". | Se siente parte del juego, no un espectador. |

**Resultado:** Puede participar de la cultura del juego, no solo sobrevivir en él.

---

## Escenario 4: Partida con amigos + gringo (caso de los 3)

**Quién:** Carlos + amigo Miguel + gringo random (Jake).  
**Situación:** Carlos y Miguel hablan español, Jake solo inglés.

| Paso | Lo que pasa |
|------|-------------|
| Jake dice algo en inglés | Pengos traduce para Carlos y Miguel al instante. Los tres se coordinan. |
| Carlos quiere decirle algo a Jake | F2 → escribe en español → Pengos da frase en inglés → Jake entiende. |
| Miguel no tiene Pengos instalado | Carlos le dice en voz la traducción. Pero la meta es que Miguel también lo instale. |

**Resultado:** El idioma deja de ser la razón por la que el equipo funciona mal.

---

## Escenario 5: Fallo — el audio se corta

**Quién:** Carlos, en partida de Fortnite.  
**Situación:** Cambió de ventana un segundo y el loopback de audio se interrumpió.

| Paso | Lo que pasa con Pengos | Emoción |
|------|------------------------|---------|
| 1 | El overlay deja de mostrar texto nuevo. Aparece un ícono rojo: **"Sin audio del sistema."** | Frustración — pero sabe qué pasó. No culpa a la app de forma ciega. |
| 2 | Carlos presiona **Ctrl+Shift+R** (reconectar audio). | — |
| 3 | El overlay vuelve a mostrar traducciones. | Alivio. La partida sigue. |

**Resultado:** El fallo es visible y recuperable. No es un crash silencioso.

> **Pendiente:** definir si el reconectar es automático o manual. Para el MVP, manual está bien.

---

## Lo que NO es el User Journey (límites del MVP)

- Pengos **no traduce voz en tiempo real para que Jake escuche en español** (eso es síntesis de voz, fuera del alcance inicial).
- Pengos **no funciona en juegos que bloquean overlays** (anticheats agresivos como Vanguard/BE en ciertos modos).
- Pengos **no aprende jerga nueva automáticamente** — usa el modelo base de Groq.
