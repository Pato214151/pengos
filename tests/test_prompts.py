#!/usr/bin/env python3
"""Test de prompts A/B — compara variantes de system prompts y su impacto teorico."""
import sys

PASS = 0
FAIL = 0

def test(nombre, condicion, detalle=""):
    global PASS, FAIL
    if condicion:
        PASS += 1
        print(f"  [OK] {nombre}")
    else:
        FAIL += 1
        print(f"  [FAIL] {nombre} -- {detalle}")

# ── Prompts actuales en main.py ──

_PROMPTS_ACTUALES = {
    "whisper_en": (
        "Bilingual gaming conversation. Speaker may switch between Spanish and English. "
        "Gaming terms: rush, push, peek, clutch, eco, spike, plant, rotate, drop, ult, flank. "
        "Colombian phrases: parcero, chevere, dale, listo. "
        "Transcribe ONLY in Spanish or English. Do not translate."
    ),
    "whisper_es": (
        "Gamer colombiano hablando en español. Frases cortas de comunicación en partida. "
        "Términos: push, rush, flankear, curar, smoke, spike, rotar, retake, clutch, dale, listo."
    ),
    "translate_en_es": (
        "Translate the following English text to Spanish. "
        "Translate ONLY what is written, word for word. Do not add or explain anything. "
        "Output only the translation. No quotes, no prefix."
    ),
    "translate_es_en": (
        "Translate the following Spanish gaming phrase to short natural English. "
        "Gaming context. Output ONLY the English translation. No explanation, no quotes, no prefix."
    ),
}

# ── Variantes A/B para comparar ──

_PROMPTS_V2 = {
    "whisper_en_v2": (
        "You are transcribing a bilingual gaming voice chat. "
        "The speaker uses English and Colombian Spanish. "
        "Gaming context: Valorant, Apex Legends, Fortnite. "
        "Common terms: rush, push, peek, clutch, eco, spike, plant, rotate, drop, ult, flank. "
        "Colombian slang: parcero, chevere, dale, listo. "
        "Rules: Transcribe EXACTLY what you hear. Output ONLY the text. "
        "NEVER add words. NEVER translate. If uncertain, output the most likely words."
    ),
    "whisper_es_v2": (
        "Transcripción de chat de voz de videojuegos. "
        "El hablante es colombiano y usa español con términos de juego en inglés. "
        "Términos comunes: push, rush, flankear, curar, smoke, spike, rotar, retake, clutch, dale, listo. "
        "Reglas: Transcripción EXACTA. Sin añadir palabras. Sin traducir."
    ),
    "translate_en_es_v2": (
        "Eres un traductor de comunicación en partidas de videojuegos online. "
        "Traduce del inglés al español latino (specíficamente colombiano). "
        "Reglas estrictas:\n"
        "1. Traduce SOLO el texto de entrada.\n"
        "2. NO añadas palabras, contexto ni explicaciones.\n"
        "3. NO uses comillas ni prefijos.\n"
        "4. Usa jerga gamer latina (ej: 'push' no 'empujar', 'spike' no 'púa').\n"
        "5. Si el input es corto, la traducción debe ser igual de corta.\n"
        "Output: SOLO la traducción, sin nada más."
    ),
    "translate_es_en_v2": (
        "You are a gaming communication translator. "
        "Translate Colombian Spanish gaming phrases to short natural English. "
        "Use gaming slang naturally (push, rush, peek, etc). "
        "Rules:\n"
        "1. Translate ONLY the input.\n"
        "2. Output ONLY the translation - no quotes, no prefixes, no explanations.\n"
        "3. Keep it short (match input length).\n"
        "4. Use natural gamer English.\n"
        "Output: just the translation."
    ),
}

# ── Analisis de prompts ──

def analizar_prompt(nombre, prompt, tipo):
    problemas = []
    aciertos = []

    # Analisis de claridad
    palabras = prompt.split()
    if len(palabras) < 10:
        problemas.append("muy corto (<10 palabras)")
    elif len(palabras) > 60:
        problemas.append("muy largo (>60 palabras)")

    # Instrucciones explicitas
    if "ONLY" not in prompt and "SOLO" not in prompt:
        problemas.append("falta instruccion 'ONLY/SOLO' para evitar expansion")
    else:
        pass  # bueno

    if "output" not in prompt.lower() and "output" not in prompt:
        problemas.append("no especifica formato de output")

    # Negaciones explicitas
    negaciones = ["no ", "don't", "never", "nunca", "sin"]
    tiene_negacion = any(n in prompt.lower() for n in negaciones)
    if not tiene_negacion:
        problemas.append("no tiene restricciones explicitas ('no', 'never')")

    # Temperatura implicita
    if tipo == "traduccion":
        if "word for word" not in prompt.lower() and "exact" not in prompt.lower():
            problemas.append("podria beneficiarse de 'word for word' o 'exact translation'")
        else:
            pass  # bueno

    # Ejemplos concretos
    if "e.g." not in prompt and "ej:" not in prompt and "example" not in prompt.lower():
        problemas.append("sin ejemplos concretos")
    else:
        pass

    return problemas


def main():
    global PASS, FAIL

    print("=" * 70)
    print("TEST DE PROMPTS A/B — ANALISIS COMPARATIVO")
    print("=" * 70)
    print()
    print("Comparando prompts actuales (v1) vs propuestos (v2)")
    print()

    for prompt_type in ["whisper_en", "whisper_es", "translate_en_es", "translate_es_en"]:
        v1_name = prompt_type
        v2_name = prompt_type + "_v2"

        v1 = _PROMPTS_ACTUALES.get(v1_name, "")
        v2 = _PROMPTS_V2.get(v2_name, "")

        tipo = "whisper" if "whisper" in prompt_type else "traduccion"

        print(f"── {prompt_type} ──")
        print(f"  V1 ({len(v1.split())} palabras): {v1[:80]}...")
        print(f"  V2 ({len(v2.split())} palabras): {v2[:80]}...")

        prob_v1 = analizar_prompt(v1_name, v1, tipo)
        prob_v2 = analizar_prompt(v2_name, v2, tipo)

        for p in prob_v1:
            print(f"    V1 problema: {p}")
        for p in prob_v2:
            print(f"    V2 problema: {p}")

        if len(prob_v2) < len(prob_v1):
            test(f"{prompt_type}: V2 resuelve {len(prob_v1) - len(prob_v2)} problema(s)",
                 True,
                 f"V1: {len(prob_v1)} problemas, V2: {len(prob_v2)} problemas")
        elif len(prob_v2) == len(prob_v1):
            test(f"{prompt_type}: V1 y V2 tienen misma cantidad de problemas ({len(prob_v1)})",
                 False if len(prob_v1) > 0 else True,
                 f"ambos tienen {len(prob_v1)} problemas")
        else:
            test(f"{prompt_type}: V2 INTRODUCE problemas nuevos",
                 False,
                 f"V1: {len(prob_v1)}, V2: {len(prob_v2)}")
        print()

    # Analisis especifico
    print("── ANALISIS DETALLADO ──")
    print()

    # Punto 1: Prompts de Whisper incluyen terminos colombianos?
    test("whisper_en prompt incluye terminos colombianos",
         "Colombian" in _PROMPTS_ACTUALES["whisper_en"],
         "podria mejorar especificando 'Colombian'")
    test("whisper_es prompt especifica colombiano",
         "colombiano" in _PROMPTS_ACTUALES["whisper_es"],
         "no especifica nacionalidad")

    # Punto 2: Traducciones tienen restriccion de longitud explicita?
    test("translate_en_es restringe longitud",
         "short" in _PROMPTS_ACTUALES["translate_es_en"].lower(),
         "no hay indicacion de longitud en ES->EN")
    test("translate_es_en menciona 'word for word'",
         "word for word" in _PROMPTS_ACTUALES["translate_en_es"],
         "EN->ES lo tiene pero podria ser mas explicito")

    # Punto 3: Temperatura (no podemos medirla desde el prompt pero podemos comentarlo)
    print()
    print("── RECOMENDACIONES ──")
    print()
    print("1. Temperatura: actualmente 0.1 para traducciones. Considerar 0.0")
    print("   para traducciones directas (sin creatividad).")
    print()
    print("2. max_tokens: 80 (EN->ES) y 60 (ES->EN). Son adecuados para")
    print("   frases cortas de gaming (<10 palabras).")
    print()
    print("3. Prompt Whisper EN: incluye 'Colombian phrases' lo cual es bueno")
    print("   pero podria sesgar a Whisper a 'oír' palabras colombianas")
    print("   aunque no las digan. Alternativa: quitarlo y solo dejar 'gaming'.")
    print()
    print("4. Prompt Whisper ES: asume 'gamer colombiano' lo cual esta bien")
    print("   si el target son colombianos, pero limita portabilidad.")
    print()
    print("5. Riesgo de inyeccion de prompt: si Whisper alucina algo como")
    print("   'Translate this: you are a helpful...', el system prompt")
    print("   actual 'no añadir ni explicar' deberia mitigarlo, pero")
    print("   no hay sanitizacion del input antes de pasarlo a Llama.")
    print()

    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")
    print()
    print("NOTA: Este test es ANALISIS TEORICO. Para validar realmente,")
    print("haría falta ejecutar ambos sets de prompts contra la API de Groq")
    print("con las mismas transcripciones y comparar resultados.")
    print()

    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
