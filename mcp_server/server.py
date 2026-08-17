"""MCPServer que expone los resultados de análisis de la Práctica 1."""

from __future__ import annotations

import logging
import os
from typing import Any, Callable

from mcp.server import MCPServer

from . import queries
from .database import DatabaseError


LOGGER = logging.getLogger(__name__)

mcp = MCPServer(
    name="analisis-ventas-online",
    title="Análisis de ventas online - Práctica 1",
    description=(
        "Servidor MCP de solo lectura para consultar los análisis de ventas "
        "de la base de datos de la Práctica 1."
    ),
    instructions=(
        "Utiliza las herramientas para responder preguntas sobre estadísticas, "
        "tendencias, segmentación y correlaciones. No inventes resultados que no "
        "estén presentes en la respuesta de la herramienta."
    ),
    version="0.1.0",
    log_level="INFO",
)


def _success(tool_name: str, data: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "herramienta": tool_name,
        "datos": data,
        "error": None,
    }


def _failure(tool_name: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "herramienta": tool_name,
        "datos": [],
        "error": message,
    }


def _execute(
    tool_name: str,
    operation: Callable[[], Any],
) -> dict[str, Any]:
    """Ejecuta una consulta y devuelve un contrato uniforme al agente."""
    try:
        return _success(tool_name, operation())
    except ValueError as exc:
        return _failure(tool_name, str(exc))
    except DatabaseError as exc:
        LOGGER.error("Error de base de datos en %s: %s", tool_name, exc)
        return _failure(tool_name, str(exc))
    except Exception:
        LOGGER.exception("Error inesperado en la herramienta %s", tool_name)
        return _failure(tool_name, "Ocurrió un error interno al ejecutar el análisis.")


@mcp.tool(
    name="obtener_estadisticas_basicas",
    description="Obtiene media, mediana y moda de las variables numéricas.",
    structured_output=True,
)
def obtener_estadisticas_basicas() -> dict[str, Any]:
    return _execute("obtener_estadisticas_basicas", queries.get_basic_statistics)


@mcp.tool(
    name="obtener_ventas_por_mes",
    description="Obtiene cantidad, total y promedio de ventas agrupados por mes.",
    structured_output=True,
)
def obtener_ventas_por_mes(anio: int = 2021) -> dict[str, Any]:
    return _execute("obtener_ventas_por_mes", lambda: queries.get_monthly_sales(anio))


@mcp.tool(
    name="obtener_distribucion_metodos_pago",
    description="Obtiene la distribución de ventas por método de pago.",
    structured_output=True,
)
def obtener_distribucion_metodos_pago() -> dict[str, Any]:
    return _execute(
        "obtener_distribucion_metodos_pago",
        queries.get_payment_distribution,
    )


@mcp.tool(
    name="obtener_distribucion_navegadores",
    description="Obtiene la distribución de ventas por navegador o canal registrado.",
    structured_output=True,
)
def obtener_distribucion_navegadores() -> dict[str, Any]:
    return _execute(
        "obtener_distribucion_navegadores",
        queries.get_browser_distribution,
    )


@mcp.tool(
    name="obtener_uso_boletines_vales",
    description="Obtiene las ventas agrupadas por uso de boletines y vales.",
    structured_output=True,
)
def obtener_uso_boletines_vales() -> dict[str, Any]:
    return _execute(
        "obtener_uso_boletines_vales",
        queries.get_newsletter_voucher_usage,
    )


@mcp.tool(
    name="obtener_tendencias",
    description="Identifica los meses con mayores y menores ventas.",
    structured_output=True,
)
def obtener_tendencias(anio: int = 2021) -> dict[str, Any]:
    return _execute("obtener_tendencias", lambda: queries.get_trends(anio))


@mcp.tool(
    name="obtener_segmentacion_edad",
    description="Agrupa clientes y compras por rangos de edad.",
    structured_output=True,
)
def obtener_segmentacion_edad(
    edad_minima: int | None = None,
    edad_maxima: int | None = None,
) -> dict[str, Any]:
    return _execute(
        "obtener_segmentacion_edad",
        lambda: queries.get_age_segments(edad_minima, edad_maxima),
    )


@mcp.tool(
    name="obtener_segmentacion_genero",
    description="Compara clientes, compras y ventas entre géneros.",
    structured_output=True,
)
def obtener_segmentacion_genero() -> dict[str, Any]:
    return _execute("obtener_segmentacion_genero", queries.get_gender_segments)


@mcp.tool(
    name="obtener_segmentacion_boletin_vale",
    description="Compara el comportamiento de compra según boletines y vales.",
    structured_output=True,
)
def obtener_segmentacion_boletin_vale() -> dict[str, Any]:
    return _execute(
        "obtener_segmentacion_boletin_vale",
        queries.get_newsletter_voucher_segments,
    )


@mcp.tool(
    name="obtener_correlacion_venta_edad",
    description="Calcula la correlación de Pearson entre edad y venta total.",
    structured_output=True,
)
def obtener_correlacion_venta_edad() -> dict[str, Any]:
    return _execute(
        "obtener_correlacion_venta_edad",
        queries.get_sale_age_correlation,
    )


@mcp.tool(
    name="obtener_correlacion_genero_pago",
    description="Examina la asociación entre género y método de pago preferido.",
    structured_output=True,
)
def obtener_correlacion_genero_pago() -> dict[str, Any]:
    return _execute(
        "obtener_correlacion_genero_pago",
        queries.get_gender_payment_relationship,
    )


@mcp.tool(
    name="obtener_correlacion_boletin_vale",
    description="Examina la asociación entre el uso de boletines y vales.",
    structured_output=True,
)
def obtener_correlacion_boletin_vale() -> dict[str, Any]:
    return _execute(
        "obtener_correlacion_boletin_vale",
        queries.get_newsletter_voucher_relationship,
    )


def _run_server() -> None:
    transport = (os.getenv("MCP_TRANSPORT") or "stdio").strip().lower()
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise ValueError(
            "MCP_TRANSPORT debe ser 'stdio', 'sse' o 'streamable-http'."
        )

    if transport == "streamable-http":
        host = os.getenv("MCP_SERVER_HOST") or "127.0.0.1"
        try:
            port = int(os.getenv("MCP_SERVER_PORT", "8000"))
        except ValueError as exc:
            raise ValueError("MCP_SERVER_PORT debe ser un número entero.") from exc
        mcp.run(transport=transport, host=host, port=port)
        return

    mcp.run(transport=transport)


if __name__ == "__main__":
    _run_server()

