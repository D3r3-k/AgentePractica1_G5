"""Pruebas de humo del MCPServer contra la base de datos configurada."""

from __future__ import annotations

import json
import unittest
from typing import Callable

from .server import (
    mcp,
    obtener_correlacion_boletin_vale,
    obtener_correlacion_genero_pago,
    obtener_correlacion_venta_edad,
    obtener_distribucion_metodos_pago,
    obtener_distribucion_navegadores,
    obtener_estadisticas_basicas,
    obtener_segmentacion_boletin_vale,
    obtener_segmentacion_edad,
    obtener_segmentacion_genero,
    obtener_tendencias,
    obtener_uso_boletines_vales,
    obtener_ventas_por_mes,
)


TOOLS: tuple[Callable[[], dict], ...] = (
    obtener_estadisticas_basicas,
    obtener_ventas_por_mes,
    obtener_distribucion_metodos_pago,
    obtener_distribucion_navegadores,
    obtener_uso_boletines_vales,
    obtener_tendencias,
    obtener_segmentacion_edad,
    obtener_segmentacion_genero,
    obtener_segmentacion_boletin_vale,
    obtener_correlacion_venta_edad,
    obtener_correlacion_genero_pago,
    obtener_correlacion_boletin_vale,
)


class MCPServerSmokeTest(unittest.TestCase):
    def test_hay_12_herramientas_registradas(self) -> None:
        self.assertEqual(len(mcp._tool_manager.list_tools()), 12)

    def test_todas_las_herramientas_devuelven_el_contrato(self) -> None:
        campos_requeridos = {"ok", "herramienta", "datos", "error"}
        for tool in TOOLS:
            with self.subTest(tool=tool.__name__):
                response = tool()
                self.assertTrue(campos_requeridos.issubset(response))
                self.assertTrue(response["ok"], response["error"])
                json.dumps(response, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)

