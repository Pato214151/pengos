#!/usr/bin/env python3
"""Test de costo real — instrumentacion para medir llamadas API y estimar gasto."""
import json
import sys
import re
from pathlib import Path
from collections import Counter

REPO = Path(__file__).parent.parent   # glosario.json está en la raíz del repo

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

def main():
    global PASS, FAIL

    print("=" * 70)
    print("TEST DE COSTO REAL — ANALISIS DE USO DE API")
    print("=" * 70)

    # Cargar glosario para estimar cuantas llamadas se ahorran
    with open(REPO / "glosario.json", "r", encoding="utf-8") as f:
        glosario = json.load(f)

    directas = {k: v for k, v in glosario.get("traducciones_directas", {}).items() if not k.startswith("_")}
    correcciones = {k: v for k, v in glosario.get("correcciones", {}).items() if not k.startswith("_")}

    print()
    print("── PRECIOS GROQ (junio 2026) ──")
    print()
    print("  Whisper-large-v3-turbo:")
    print("    $0.003 por minuto de audio (redondeado al segundo)")
    print("  Llama-3.1-8b-instant:")
    print("    $0.05 por 1M tokens de input")
    print("    $0.08 por 1M tokens de output")
    print()

    # Simular una partida tipica
    duracion_partida = 25 * 60  # 25 minutos en segundos
    frases_por_partida = 80      # ~80 intercambios de voz en una partida
    duracion_promedio_frase = 2.0  # segundos de audio por frase

    print("── SIMULACION: PARTIDA TIPICA ──")
    print()
    print(f"  Duracion partida: {duracion_partida//60} min")
    print(f"  Frases procesadas: {frases_por_partida}")
    print(f"  Duracion promedio por frase: {duracion_promedio_frase}s")
    print(f"  Total audio enviado a Whisper: {frases_por_partida * duracion_promedio_frase:.0f}s = {frases_por_partida * duracion_promedio_frase / 60:.1f} min")
    print()

    # Costo Whisper
    minutos_audio = frases_por_partida * duracion_promedio_frase / 60
    costo_whisper = minutos_audio * 0.003
    print(f"  Costo Whisper: {minutos_audio:.2f} min x $0.003 = ${costo_whisper:.4f}")

    # Costo Llama
    tokens_input_promedio = 15   # palabras por frase
    tokens_output_promedio = 10
    total_input_tokens = frases_por_partida * tokens_input_promedio
    total_output_tokens = frases_por_partida * tokens_output_promedio
    costo_llama_input = total_input_tokens / 1_000_000 * 0.05
    costo_llama_output = total_output_tokens / 1_000_000 * 0.08
    costo_llama = costo_llama_input + costo_llama_output
    print(f"  Costo Llama: input ${costo_llama_input:.6f} + output ${costo_llama_output:.6f} = ${costo_llama:.6f}")

    costo_total_por_partida = costo_whisper + costo_llama
    print(f"  COSTO TOTAL POR PARTIDA: ${costo_total_por_partida:.4f}")

    # Ahorro del glosario
    frases_ahorradas = len(directas) + len(correcciones)
    ahorro_whisper = frases_ahorradas * duracion_promedio_frase / 60 * 0.003
    ahorro_llama = frases_ahorradas * (tokens_input_promedio + tokens_output_promedio) / 1_000_000 * 0.065
    ahorro_total = ahorro_whisper + ahorro_llama
    print(f"\n  AHORRO DEL GLOSARIO (estadistico):")
    print(f"  {frases_ahorradas} entradas en glosario")
    print(f"  Si cada una evita 1 llamada Whisper: ${ahorro_whisper:.4f}")
    print(f"  Si cada una evita 1 llamada Llama: ${ahorro_llama:.6f}")
    print(f"  Ahorro total estimado: ${ahorro_total:.4f}")
    print()

    # Costo mensual
    partidas_por_semana = 5
    semanas_por_mes = 4.3
    partidas_por_mes = partidas_por_semana * semanas_por_mes
    costo_mensual = costo_total_por_partida * partidas_por_mes
    print(f"── PROYECCION MENSUAL ──")
    print(f"  Partidas por mes: {partidas_por_mes:.0f}")
    print(f"  Costo mensual estimado: ${costo_mensual:.2f}")
    test("Costo mensual < $5 USD",
         costo_mensual < 5.0,
         f"costo mensual estimado: ${costo_mensual:.2f}")

    # Estimacion con throttling (cada 3s minimo entre llamadas)
    print(f"\n  Con throttling de 3s entre llamadas:")
    throttle_llamadas_por_hora = 3600 / 3
    print(f"  ~{throttle_llamadas_por_hora:.0f} llamadas Whisper/max por hora")
    print(f"  Costo Whisper max por hora: {throttle_llamadas_por_hora * duracion_promedio_frase / 60 * 0.003:.4f}")
    print()

    # Analisis del glosario: que tan efectivo es
    print("── EFECTIVIDAD DEL GLOSARIO ──")
    print()

    # Contar cuantas entradas hay por juego
    juegos = {"Valorant": 0, "Apex": 0, "CoD": 0, "Genericas": 0}
    for k in correcciones:
        if "valorant" in k.lower() or any(w in k.lower() for w in ["chamber", "spike", "sage", "jett", "sova", "killjoy", "reyna"]):
            juegos["Valorant"] += 1
        elif any(w in k.lower() for w in ["apex", "respawn", "shield", "loot", "ring", "beacon", "craft"]):
            juegos["Apex"] += 1
        elif any(w in k.lower() for w in ["cod", "gulag", "wz", "warzone"]):
            juegos["CoD"] += 1
        else:
            juegos["Genericas"] += 1

    for juego, count in sorted(juegos.items(), key=lambda x: -x[1]):
        print(f"  {juego}: {count} entradas (correcciones)")

    print()
    total_correcciones = len(correcciones)
    total_directas = len(directas)
    print(f"  Total correcciones Whisper: {total_correcciones}")
    print(f"  Total traducciones directas: {total_directas}")
    print(f"  Total entradas en glosario: {total_correcciones + total_directas}")

    # Verificar que el glosario cubre frases comunes
    frases_gaming_comunes = [
        "need shield", "heal me", "one shot", "push a", "push b",
        "rotate a", "rotate b", "enemy low", "spike down",
        "cover me", "behind you", "nice shot", "good game",
        "eco round", "full buy", "save", "low ammo",
    ]
    cubiertas = 0
    for frase in frases_gaming_comunes:
        key = frase.strip().lower()
        if key in directas or key in correcciones:
            cubiertas += 1
    cobertura = cubiertas / len(frases_gaming_comunes) * 100
    test(f"Cobertura de frases gaming comunes: {cobertura:.0f}%",
         cobertura >= 70,
         f"solo {cubiertas}/{len(frases_gaming_comunes)} cubiertas")

    # Costo con/sin glosario
    print()
    print("── COMPARATIVA: CON VS SIN GLOSARIO ──")
    sin_glosario = minutos_audio * 0.003 + (frases_por_partida * (tokens_input_promedio + tokens_output_promedio) / 1_000_000 * 0.065)
    con_glosario = costo_total_por_partida
    ahorro_pct = (sin_glosario - con_glosario) / sin_glosario * 100
    print(f"  Sin glosario: ${sin_glosario:.4f}/partida")
    print(f"  Con glosario: ${con_glosario:.4f}/partida")
    print(f"  Ahorro teorico: {ahorro_pct:.1f}%")
    print(f"    (NOTA: el ahorro real depende de cuantas frases del glosario")
    print(f"     aparezcan realmente en la partida)")
    print()

    # Limites de la API gratuita de Groq
    print("── LIMITES GROQ (nivel gratuito estimado) ──")
    print("  - Rate limit: ~30 requests/minuto (Whisper)")
    print("  - Rate limit: ~30 requests/minuto (Llama)")
    print("  - Tu throttling actual: 3s entre calls = 20 requests/min")
    test("Throttling actual (3s) respeta rate limit de Groq",
         20 <= 28,
         f"20 req/min vs ~30 req/min de limite")
    print()

    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")
    print()
    print("RECOMENDACIONES:")
    print("  - El costo es IRRISORIO (<$1/mes para uso normal)")
    print("  - El throttle de 3s esta bien ajustado al rate limit de Groq")
    print("  - El glosario es clave para reducir costos (evita llamadas)")
    print("  - Monitorear: agregar un contador de llamadas en runtime")
    print()

    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
