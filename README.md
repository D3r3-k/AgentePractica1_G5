<div align="center">

# Práctica 1 — Análisis de Ventas Online 2021 - Grupo 5

**Sistemas Organizacionales y Gerenciales 2**

Facultad de Ingeniería · Ingeniería en Ciencias y Sistemas

Universidad de San Carlos de Guatemala · Segundo Semestre 2026

Entregable: `SOG2-2S26_grupo5.pdf`

</div>

---
	
## Integrantes

|   #   | Nombre                          |   Carné   | Bloque asignado                           |
| :---: | ------------------------------- | :-------: | ----------------------------------------- |
|   1   | Derek Francisco Orellana Ibáñez | 202001151 | Datos y Base de Datos                     |
|   2   | Juan Esteban Chacón Trampe      | 202300431 | MCPServer                                 |
|   3   | Daniel Andree Hernandez Flores  | 202300512 | Agente conversacional (Google ADK)        |
|   4   | Fátima Florisel Cerezo Paredes  | 202300434 | Análisis exploratorio y de tendencias     |
|   5   | Valery Pamela Alarcon Ramos     | 202300794 | Segmentación, correlación e informe final |


El detalle de tareas por integrante está en [`docs/01-planificacion.md`](docs/01-planificacion.md).

---

## Índice

- [Planificacion](docs/01-planificacion.md)
- [Proceso de Análisis](docs/02-proceso-analisis.md)
- [Metodología](docs/03-metodologia.md)
- [Conclusiones](docs/04-conclusiones.md)
- [Recomendaciones](docs/05-recomendaciones.md)
- [Respuestas](docs/06-respuestas.md)
- [Diagrama de BD](docs/07-diagrama-bd.md)
- [Segmentación y correlación](docs/11-segmentacion-correlacion.md)
- [Análisis exploratorio y de tendencias](docs/12-exploratorio-tendencias.md)
- [MCPServer](mcp_server/README.md)
- [Agente conversacional](agente_adk/README.md)

---

## Informe final

El entregable es `informe/SOG2-2S26_grupo5.pdf`, redactado y maquetado en Word a
partir de la documentación de [`docs/`](docs/), las doce gráficas de
[`graficas/`](graficas/) y la salida de los scripts de análisis, que se conserva en
`informe/salidas-consola/`.

| Archivo | Contenido |
| :--- | :--- |
| `SOG2-2S26_grupo5.pdf` | El entregable, exportado desde Word |
| `informe final.docx` | El documento editable del que sale el PDF |
| `PENDIENTES.md` | Control de lo que falta por integrante |
| `salidas-consola/` | Salida de los scripts, reproducida en el capítulo «Resultados detallados» |

Toda cifra del informe procede de una consulta ejecutada contra PostgreSQL. Ninguna
se transcribió a mano y ninguna gráfica se editó con un programa de diseño: se
regeneran ejecutando los scripts de análisis.

---

## Análisis

```bash
python analisis/exploratorio.py    # puntos 2 y 3 · gráficas 01 a 05
python analisis/segmentacion.py    # puntos 4 y 5 · gráficas 06 a 09
python analisis/distribuciones.py  # gráficas 10 a 12
```

Ambos scripts importan `mcp_server/queries.py`, de modo que el informe, el MCPServer y
el agente conversacional devuelven por construcción las mismas cifras.

---


## Configuración

> [!NOTE] 
> **Windows**

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
copy .env.example .env
# Llenar .env con las credenciales
python db/limpieza.py
python db/carga.py
python -m mcp_server.server
```

> [!NOTE] 
> **Linux**

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Llenar .env con las credenciales
python3 db/limpieza.py
python3 db/carga.py
python3 -m mcp_server.server
```

> [!NOTE] 
> **Mac**

```bash
git clone https://github.com/D3r3-k/AgentePractica1_G5.git
cd AgentePractica1_G5
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Llenar .env con las credenciales
python3 db/limpieza.py
python3 db/carga.py
python3 -m mcp_server.server
```

## MCPServer

El servidor MCP expone 12 herramientas de consulta para los puntos 2 al 6. Su documentación, contrato de respuestas, variables de entorno y pruebas se encuentra en [`mcp_server/README.md`](mcp_server/README.md).

## Agente conversacional

El agente Google ADK consume las 12 herramientas del MCPServer por `stdio` y responde en lenguaje natural los puntos 2 al 6. Su documentación e instrucciones de ejecución están en [`agente_adk/README.md`](agente_adk/README.md).

El agente vive en un entorno virtual aparte (`.venv-agent`) porque `google-adk` requiere `mcp<2` y el MCPServer usa `mcp` 2.x:

```bash
python3 -m venv .venv-agent
.venv-agent/bin/pip install -r agente_adk/requirements.txt
.venv-agent/bin/python -m agente_adk.test_agente   # prueba de humo
.venv-agent/bin/adk web                            # interfaz de chat
```

En Windows se sustituye `.venv-agent/bin/` por `.venv-agent\Scripts\`.
