#!/usr/bin/env python3
"""Test de falsos positivos — edge cases extremos del filtro + glosario."""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("GROQ_API_KEY", "test-key-for-tests")
# El test vive en tests/; agregar la raíz del repo al path para importar los módulos.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from filters import es_transcripcion_valida
from glosario import (
    _glosario_key,
    cargar_glosario,
    corregir_transcripcion,
    traduccion_directa,
)

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
    cargar_glosario()

    print("=" * 70)
    print("TEST: FALSOS POSITIVOS — COMBINACIONES PELIGROSAS")
    print("=" * 70)

    casos = [
        # (texto, debe_pasar, descripcion)
        # Frases con puntuacion rara
        ("wait...",                      True,  "puntos suspensivos al final"),
        ("wait...!",                     True,  "puntos + exclamacion"),
        ("!!!!",                         False, "solo signos de exclamacion"),
        ("¿¿¿",                          False, "solo signos raros"),
        ("wat??",                        True,  "signos de pregunta"),
        ("???",                          False, "solo signos de pregunta"),
        ("...wait",                      True,  "puntos al inicio"),
        ("he's one shot!",               True,  "frase normal con signo"),
        ("he's one shot?!",              True,  "frase con doble signo"),

        # Numeros y mezclas
        ("12345",                        False, "solo numeros"),
        ("push 1",                       True,  "numero + palabra"),
        ("1 left a",                     True,  "numero + frase"),
        ("1v3",                          False, "notacion gaming aislada (<4 chars)"),
        ("1v1 me bro",                   True,  "frase gaming tipica"),
        ("lol",                          False, "jerga aislada (<4 chars sin glosario)"),
        ("lmao",                         True,  "jerga"),

        # Limites de length
        ("a",                            False, "1 char sin glosario"),
        ("ok",                           False, "2 chars sin glosario"),
        ("go",                           True,  "2 chars EN glosario directa"),
        ("no",                           True,  "2 chars EN glosario directa"),
        ("yes",                          True,  "3 chars EN glosario directa"),
        ("ez",                           True,  "2 chars EN glosario directa"),
        ("hi",                           False, "2 chars SIN glosario"),
        ("push",                         True,  "4 chars SIN glosario pero tiene sentido"),
        ("rush",                         True,  "palabra real corta"),
        ("clutch",                       True,  "palabra real"),

        # Hallucination patterns falsos positivos (NO deberian fallar)
        ("thanks bro",                   True,  "'thanks' pero no es 'thanks for watching'"),
        ("thanks man",                   True,  "similar pero no es patron"),
        ("subscribe to win",             True,  "'subscribe to' pero no es patron exacto"),
        ("caption this",                 True,  "'caption' sin 'by'"),
        ("caption",                      True,  "palabra caption sola"),
        ("music to my ears",             True,  "'music' en contexto"),
        ("musica en el lobby",           True,  "'musica' dentro de frase"),

        # Unicode tricky
        ("café",                   True,  "unicode combinado (acento como combining)"),
        ("​push left",              True,  "zero-width space antes"),
        ("push​left",               True,  "zero-width space dentro"),
        ("push left​",              True,  "zero-width space despues"),

        # Whitespace raro
        ("push\tleft",                   True,  "tabulador entre palabras"),
        ("  push  left  ",               True,  "multiples espacios"),
        ("\npush\nleft\n",               True,  "newlines"),

        # Mayusculas/minusculas
        ("PUSH LEFT",                    True,  "todo mayusculas"),
        ("Push Left",                    True,  "capitalizado"),
        ("PUSH A",                       True,  "todo mayus en glosario"),
        ("HeAl Me",                      True,  "mayusculas mezcladas"),

        # Silencio tipo Whisper
        (".",                            False, "punto solo"),
        ("-",                            False, "guion solo"),
        ("...",                          False, "puntos suspensivos solos"),
        (". . .",                        False, "puntos con espacios"),
        ("— — —",                        False, "guiones largos"),
        ("*",                            False, "asterisco solo"),
        ("♪♪♪",                          False, "notas musicales seguidas"),
        ("♫ ♫ ♫",                        False, "notas musicales separadas"),
        ("[ ♪ música ♪ ]",              True,  "musica entre brackets (tiene texto valido)"),

        # Caracteres cirilicos mezclados con latin
        ("push левый",                   False, "mezcla latin + cirilico"),
        ("привет team",                  False, "cirilico + latin"),
        ("rush Б",                       False, "latin + cirilico"),

        # Hangul + latin
        ("push 왼쪽",                     False, "latin + hangul"),

        # Frases en espanol en el canal EN
        ("necesito cura",                True,  "espanol en canal EN (es valido)"),
        ("cubreme",                      True,  "espanol corto"),
        ("vamos B",                      True,  "espanol gaming"),
        ("detras tuyo",                  True,  "espanol frase comun"),
    ]

    for texto, debe_pasar, desc in casos:
        resultado = es_transcripcion_valida(texto)
        if debe_pasar:
            test(f"DEBE PASAR: {desc} ({repr(texto[:40])})",
                 resultado is True,
                 "el filtro lo BLOQUEO pero deberia pasar")
        else:
            test(f"DEBE BLOQUEAR: {desc} ({repr(texto[:40])})",
                 resultado is False,
                 "el filtro lo DEJO PASAR pero deberia bloquear")

    print("\n" + "=" * 70)
    print("TEST: COBERTURA DEL GLOSARIO")
    print("=" * 70)

    frases_comunes = [
        ("need shield",    "frase comun en Valorant"),
        ("pushing a",      "variante de push a"),
        ("rotate b",       "variante de rotate to b"),
        ("rotating b",     "variante con -ing"),
        ("dropping",       "comun en Apex"),
    ]
    for frase, desc in frases_comunes:
        tiene_trad = traduccion_directa(frase) is not None
        tiene_corr = corregir_transcripcion(frase) != frase
        test(
            f"GLOSARIO: {desc} ({repr(frase)}) {'TIENE' if tiene_trad or tiene_corr else 'FALTA'} cobertura",
            tiene_trad or tiene_corr,
            "ni en correcciones ni en traducciones_directas",
        )

    print("\n" + "=" * 70)
    print("TEST: GLOSARIO KEY — CASOS TRICKY")
    print("=" * 70)

    casos_key = [
        ("",                ""),
        ("!!!",             ""),
        ("...",             ""),
        ("a.",              "a"),
        ("a...",            "a"),
        ("¡hola!",          "¡hola"),
        ("¿que?",           "¿que"),
        ("wait...",         "wait"),
        ("stop.",           "stop"),
        ("hello-world",     "hello-world"),
        ("doble  espacio",  "doble  espacio"),
        ("  trim  ",        "trim"),
        ("...muchos puntos inicio", "muchos puntos inicio"),
    ]
    for entrada, esperado in casos_key:
        resultado = _glosario_key(entrada)
        test(f"key({repr(entrada)}) -> {repr(esperado)}",
             resultado == esperado,
             f"obtuvo {repr(resultado)}")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")
    print("=" * 70)
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
