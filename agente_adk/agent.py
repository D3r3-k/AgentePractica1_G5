"""Agente conversacional Google ADK conectado al MCPServer de la Práctica 1."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from .prompt import INSTRUCCION_SISTEMA


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv("MODEL_NAME") or "gemini-3.5-flash-lite"

# Variables que el proceso del MCPServer necesita para llegar a PostgreSQL.
_VARIABLES_MCP = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_SCHEMA",
    "DB_SSLMODE",
    "DB_CONNECT_TIMEOUT",
)


def _interprete_mcp() -> str:
    """Devuelve el intérprete que ejecuta el MCPServer.

    El servidor usa `mcp` 2.x y el ADK usa `mcp` 1.x, por lo que cada uno vive
    en su propio entorno virtual. `MCP_PYTHON` permite sobrescribir la ruta.
    """
    configurado = os.getenv("MCP_PYTHON")
    if configurado:
        return configurado

    candidatos = (
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
    )
    for candidato in candidatos:
        if candidato.exists():
            return str(candidato)

    return sys.executable


def _entorno_mcp() -> dict[str, str]:
    """Copia al subproceso solo las variables que el MCPServer necesita."""
    entorno = {
        nombre: os.environ[nombre]
        for nombre in _VARIABLES_MCP
        if os.environ.get(nombre)
    }
    entorno["MCP_TRANSPORT"] = "stdio"
    entorno["PYTHONUNBUFFERED"] = "1"
    if os.environ.get("PATH"):
        entorno["PATH"] = os.environ["PATH"]
    return entorno


herramientas_analisis = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_interprete_mcp(),
            args=["-m", "mcp_server.server"],
            cwd=str(PROJECT_ROOT),
            env=_entorno_mcp(),
        ),
        timeout=60.0,
    ),
)


root_agent = LlmAgent(
    name="analista_ventas_online",
    model=MODEL_NAME,
    description=(
        "Analista de datos que responde preguntas sobre las ventas online de "
        "2021 consultando el MCPServer del grupo."
    ),
    instruction=INSTRUCCION_SISTEMA,
    tools=[herramientas_analisis],
)
