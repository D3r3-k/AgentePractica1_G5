"""Valida que el agente responda los puntos 2 al 6 usando el MCPServer.

Genera la evidencia del requerimiento técnico 3.3.c: cada pregunta debe
provocar al menos una llamada a la herramienta esperada y una respuesta con
datos reales de la base.

Uso:
    .venv-agent/bin/python -m agente_adk.validacion
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

from .agent import MODEL_NAME, herramientas_analisis, root_agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SALIDA = PROJECT_ROOT / "docs" / "08-validacion-agente.md"

# La capa gratuita de Gemini limita las solicitudes por día y por modelo
# (cuota `GenerateRequestsPerDayPerProjectPerModel-FreeTier`). Cada pregunta
# consume al menos dos: la llamada a la herramienta y la redacción de la
# respuesta. La pausa evita además el límite por minuto.
PAUSA_SEGUNDOS = float(os.getenv("VALIDACION_PAUSA", "6"))
REINTENTOS = 3

# (punto, pregunta, herramienta que debe invocarse)
CASOS: tuple[tuple[str, str, str], ...] = (
    ("2.b", "¿Cuál es la media, mediana y moda de las variables numéricas?",
     "obtener_estadisticas_basicas"),
    ("2.c", "¿Cómo se distribuyeron las ventas por mes en 2021?",
     "obtener_ventas_por_mes"),
    ("2.c", "¿Cuántas ventas hubo por cada método de pago?",
     "obtener_distribucion_metodos_pago"),
    ("2.c", "¿Cómo se reparten las ventas entre los navegadores?",
     "obtener_distribucion_navegadores"),
    ("2.c", "¿Cómo se distribuyen las ventas según el uso de boletín y vale?",
     "obtener_uso_boletines_vales"),
    ("3.a", "¿Qué meses tuvieron mayores y menores ventas en 2021?",
     "obtener_tendencias"),
    ("3.b", "¿Cuál fue el navegador más preferido y cuál el menos popular?",
     "obtener_distribucion_navegadores"),
    ("3.c", "¿Cuántas ventas se pagaron contra entrega o en efectivo?",
     "obtener_distribucion_metodos_pago"),
    ("3.d", "¿En qué meses se usaron más boletines y vales?",
     "obtener_uso_boletines_vales"),
    ("4.a", "¿Cómo compran los clientes según su rango de edad?",
     "obtener_segmentacion_edad"),
    ("4.b", "¿Hay diferencias en el comportamiento de compra entre géneros?",
     "obtener_segmentacion_genero"),
    ("4.c", "¿Cómo compran los clientes que reciben boletín y los que usan vale?",
     "obtener_segmentacion_boletin_vale"),
    ("5.a", "¿Existe relación entre la edad del cliente y el total de la venta?",
     "obtener_correlacion_venta_edad"),
    ("5.b", "¿El género del cliente influye en el método de pago preferido?",
     "obtener_correlacion_genero_pago"),
    ("5.c", "¿Existe correlación entre los clientes que usan boletines y vales?",
     "obtener_correlacion_boletin_vale"),
    ("6", "Dame los datos que necesito para graficar las ventas por mes.",
     "obtener_ventas_por_mes"),
)


async def _preguntar(runner: InMemoryRunner, pregunta: str) -> tuple[list[str], str]:
    """Envía una pregunta en una sesión nueva y devuelve herramientas y texto."""
    sesion = await runner.session_service.create_session(
        app_name="practica1", user_id="validador"
    )
    herramientas: list[str] = []
    respuesta: list[str] = []

    async for evento in runner.run_async(
        user_id="validador",
        session_id=sesion.id,
        new_message=types.Content(role="user", parts=[types.Part(text=pregunta)]),
    ):
        partes = (evento.content.parts if evento.content else None) or []
        for parte in partes:
            llamada = getattr(parte, "function_call", None)
            if llamada is not None:
                herramientas.append(llamada.name)
            texto = getattr(parte, "text", None)
            if texto:
                respuesta.append(texto)

    return herramientas, "".join(respuesta).strip()


async def _main() -> int:
    runner = InMemoryRunner(agent=root_agent, app_name="practica1")
    filas: list[str] = []
    fallidos = 0

    print(f"Validando {len(CASOS)} preguntas con el modelo {MODEL_NAME}.\n")

    for indice, (punto, pregunta, esperada) in enumerate(CASOS):
        if indice:
            await asyncio.sleep(PAUSA_SEGUNDOS)

        herramientas: list[str] = []
        respuesta = ""
        for intento in range(1, REINTENTOS + 1):
            try:
                herramientas, respuesta = await _preguntar(runner, pregunta)
                break
            except Exception as exc:
                if "RESOURCE_EXHAUSTED" in str(exc) or "quota" in str(exc).lower():
                    espera = PAUSA_SEGUNDOS * 2 * intento
                    print(f"         cuota agotada, reintento en {espera:.0f}s")
                    await asyncio.sleep(espera)
                    continue
                herramientas, respuesta = [], f"Error: {exc}"
                break

        uso_correcto = esperada in herramientas
        hay_respuesta = len(respuesta) > 80
        exitoso = uso_correcto and hay_respuesta
        fallidos += 0 if exitoso else 1

        marca = "ok" if exitoso else "FALLO"
        print(f"[{marca}] {punto:>4}  {pregunta}")
        print(f"         herramientas: {herramientas or 'ninguna'}")

        filas.append(
            f"| {punto} | {pregunta} | `{esperada}` | "
            f"{', '.join(f'`{h}`' for h in herramientas) or 'ninguna'} | "
            f"{'Sí' if exitoso else 'No'} |"
        )

    await herramientas_analisis.close()

    encabezado = (
        "[ ← Regresar ](../README.md)\n\n"
        "# Validación del agente conversacional\n\n"
        "Evidencia del requerimiento técnico 3.3.c: el chat de IA entrega los\n"
        "resultados de los puntos 2 al 6 según se soliciten.\n\n"
        f"- Modelo: `{MODEL_NAME}`\n"
        f"- Preguntas evaluadas: {len(CASOS)}\n"
        f"- Preguntas correctas: {len(CASOS) - fallidos}\n\n"
        "Cada caso se ejecuta en una sesión nueva del agente. Se considera\n"
        "correcto cuando el agente invoca la herramienta esperada del MCPServer\n"
        "y devuelve una respuesta con contenido.\n\n"
        "| Punto | Pregunta | Herramienta esperada | Herramientas invocadas | Correcto |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    SALIDA.write_text(encabezado + "\n".join(filas) + "\n", encoding="utf-8")

    print(f"\nEvidencia escrita en {SALIDA.relative_to(PROJECT_ROOT)}")
    if fallidos:
        print(f"Preguntas sin validar: {fallidos}")
        return 1
    print("Las 16 preguntas se respondieron con la herramienta esperada.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
