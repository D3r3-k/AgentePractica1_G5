"""Pruebas de humo del agente conversacional y su conexión con el MCPServer."""

from __future__ import annotations

import asyncio
import os
import sys

from .agent import MODEL_NAME, herramientas_analisis, root_agent


HERRAMIENTAS_ESPERADAS = {
    "obtener_estadisticas_basicas",
    "obtener_ventas_por_mes",
    "obtener_distribucion_metodos_pago",
    "obtener_distribucion_navegadores",
    "obtener_uso_boletines_vales",
    "obtener_tendencias",
    "obtener_segmentacion_edad",
    "obtener_segmentacion_genero",
    "obtener_segmentacion_boletin_vale",
    "obtener_correlacion_venta_edad",
    "obtener_correlacion_genero_pago",
    "obtener_correlacion_boletin_vale",
}


def _verificar_modelo() -> list[str]:
    """Confirma que la API acepte el modelo configurado.

    El listado de modelos incluye algunos que la API rechaza para claves
    nuevas, así que se valida con una llamada real y mínima.
    """
    from google import genai

    try:
        cliente = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        cliente.models.generate_content(model=MODEL_NAME, contents="ping")
    except KeyError:
        return ["No se pudo probar el modelo porque falta GOOGLE_API_KEY."]
    except Exception as exc:
        return [f"El modelo '{MODEL_NAME}' no respondió: {exc}"]

    print(f"El modelo '{MODEL_NAME}' respondió correctamente.")
    return []


def _verificar_configuracion() -> list[str]:
    fallos = []
    if not os.getenv("GOOGLE_API_KEY"):
        fallos.append("Falta GOOGLE_API_KEY en el archivo .env.")
    if not os.getenv("DB_HOST"):
        fallos.append("Falta DB_HOST en el archivo .env.")
    return fallos


async def _verificar_herramientas() -> list[str]:
    fallos = []
    herramientas = await herramientas_analisis.get_tools()
    nombres = {herramienta.name for herramienta in herramientas}

    faltantes = HERRAMIENTAS_ESPERADAS - nombres
    if faltantes:
        fallos.append(f"El MCPServer no expuso: {sorted(faltantes)}")

    print(f"Herramientas expuestas por el MCPServer: {len(nombres)}")
    for nombre in sorted(nombres):
        marca = "ok" if nombre in HERRAMIENTAS_ESPERADAS else "extra"
        print(f"  [{marca}] {nombre}")

    await herramientas_analisis.close()
    return fallos


async def _main() -> int:
    print(f"Agente: {root_agent.name}")
    print(f"Modelo: {MODEL_NAME}\n")

    fallos = _verificar_configuracion()
    if not fallos:
        fallos += _verificar_modelo()
    fallos += await _verificar_herramientas()

    if fallos:
        print("\nFallos encontrados:")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("\nTodas las verificaciones pasaron.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
