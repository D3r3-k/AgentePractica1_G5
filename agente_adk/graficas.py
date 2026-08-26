"""Herramientas que muestran las gráficas del punto 6 como artifacts del chat.

Las imágenes ya fueron generadas por los scripts de `analisis/` y viven en
`graficas/`. Estas herramientas no las recalculan: leen el PNG y lo guardan
como artifact de la sesión para que la interfaz de `adk web` lo muestre
directamente en la conversación, como exige el punto 6 de la práctica.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from google.adk.tools import ToolContext
from google.genai import types


DIRECTORIO_GRAFICAS = Path(__file__).resolve().parents[1] / "graficas"

# Catálogo de las nueve visualizaciones del informe. La clave es el nombre que
# el modelo pasa a `mostrar_grafica`; `puntos` indica qué incisos de la
# práctica cubre cada una.
CATALOGO_GRAFICAS: dict[str, dict[str, str]] = {
    "ventas-por-mes": {
        "archivo": "01-ventas-por-mes.png",
        "titulo": "Evolución mensual de las ventas (2021)",
        "tipo": "líneas",
        "puntos": "2.c, 3.a",
    },
    "metodo-pago": {
        "archivo": "02-metodo-pago.png",
        "titulo": "Ventas por método de pago",
        "tipo": "barras",
        "puntos": "2.c, 3.c",
    },
    "navegador": {
        "archivo": "03-navegador.png",
        "titulo": "Ventas por navegador / canal de compra",
        "tipo": "barras",
        "puntos": "2.c, 3.b",
    },
    "boletin-vale": {
        "archivo": "04-boletin-vale.png",
        "titulo": "Distribución de ventas por boletín y vale",
        "tipo": "barras",
        "puntos": "2.c",
    },
    "boletin-vale-mensual": {
        "archivo": "05-boletin-vale-mensual.png",
        "titulo": "Uso de boletines y vales por mes (2021)",
        "tipo": "líneas",
        "puntos": "3.d",
    },
    "segmentacion-edad": {
        "archivo": "06-segmentacion-edad.png",
        "titulo": "Ticket promedio por rango de edad del cliente",
        "tipo": "barras",
        "puntos": "4.a",
    },
    "genero-metodo-pago": {
        "archivo": "07-genero-metodo-pago.png",
        "titulo": "Reparto del método de pago dentro de cada género",
        "tipo": "barras apiladas al 100 %",
        "puntos": "4.b, 5.b",
    },
    "dispersion-edad-venta": {
        "archivo": "08-dispersion-edad-venta.png",
        "titulo": "Relación entre la edad del cliente y el total de la venta",
        "tipo": "dispersión",
        "puntos": "5.a",
    },
    "boletin-vale-ticket": {
        "archivo": "09-boletin-vale-ticket.png",
        "titulo": "Ticket promedio según uso de boletín y vale",
        "tipo": "mapa de calor",
        "puntos": "4.c, 5.c",
    },
}


def listar_graficas() -> dict[str, Any]:
    """Lista las gráficas disponibles del análisis con su nombre y título.

    Úsala cuando el usuario pregunte qué gráficas existen o cuando necesites
    confirmar el nombre exacto antes de llamar a `mostrar_grafica`.
    """
    return {
        "ok": True,
        "herramienta": "listar_graficas",
        "datos": [
            {"nombre": nombre, **info}
            for nombre, info in CATALOGO_GRAFICAS.items()
        ],
        "error": None,
    }


async def mostrar_grafica(nombre: str, tool_context: ToolContext) -> dict[str, Any]:
    """Muestra una gráfica del análisis directamente en el chat.

    Args:
        nombre: Identificador de la gráfica. Valores válidos: ventas-por-mes,
            metodo-pago, navegador, boletin-vale, boletin-vale-mensual,
            segmentacion-edad, genero-metodo-pago, dispersion-edad-venta,
            boletin-vale-ticket.
    """
    info = CATALOGO_GRAFICAS.get(nombre.strip().lower())
    if info is None:
        return {
            "ok": False,
            "herramienta": "mostrar_grafica",
            "datos": [],
            "error": (
                f"No existe la gráfica '{nombre}'. Nombres válidos: "
                f"{', '.join(sorted(CATALOGO_GRAFICAS))}."
            ),
        }

    ruta = DIRECTORIO_GRAFICAS / info["archivo"]
    if not ruta.exists():
        return {
            "ok": False,
            "herramienta": "mostrar_grafica",
            "datos": [],
            "error": (
                f"El archivo {info['archivo']} no está en graficas/. "
                "Ejecuta los scripts de analisis/ para regenerarlo."
            ),
        }

    version = await tool_context.save_artifact(
        info["archivo"],
        types.Part.from_bytes(data=ruta.read_bytes(), mime_type="image/png"),
    )
    return {
        "ok": True,
        "herramienta": "mostrar_grafica",
        "datos": [{**info, "version": version}],
        "error": None,
    }
