[ ← Regresar ](../README.md)

# Agente conversacional — Práctica 1

Agente de IA construido con **Google ADK** que responde preguntas sobre las
ventas online de 2021 consultando el [MCPServer](../mcp_server/README.md) del
grupo. Cubre los puntos 2 al 6 del alcance de la práctica.

## Arquitectura

```text
Usuario  ──►  adk web / adk run
                   │
                   ▼
            root_agent (LlmAgent, Gemini Flash)      .venv-agent  · mcp 1.x
                   │
                   │  McpToolset · transporte stdio
                   ▼
            mcp_server.server (12 herramientas)      .venv        · mcp 2.x
                   │
                   ▼
            PostgreSQL en la nube (esquema geren2)
```

```text
agente_adk/
├── __init__.py        # Expone el paquete al runtime de ADK
├── agent.py           # Define root_agent y la conexión al MCPServer
├── graficas.py        # Herramientas que muestran los PNG del punto 6 en el chat
├── prompt.py          # Instrucción del sistema y diccionario de códigos
├── requirements.txt   # Dependencias del entorno del agente
└── test_agente.py     # Prueba de humo de la configuración y las herramientas
```

## Por qué hay dos entornos virtuales

El MCPServer del integrante 2 usa el SDK `mcp` **2.x**, mientras que
`google-adk` declara `mcp>=1.24,<2` para su cliente MCP. Instalar ambos en el
mismo entorno rompe la importación de `McpToolset`
(`ModuleNotFoundError: No module named 'mcp.shared.session'`).

La solución es aislar cada componente:

| Entorno       | Contenido                       | Rol                        |
| ------------- | ------------------------------- | -------------------------- |
| `.venv`       | `requirements.txt` · `mcp` 2.x  | Ejecuta el MCPServer       |
| `.venv-agent` | `google-adk[mcp]` · `mcp` 1.x   | Ejecuta el agente ADK      |

El agente levanta el MCPServer como subproceso por `stdio` usando el intérprete
de `.venv`, así que ambos SDK nunca se cargan en el mismo proceso. La ruta se
detecta automáticamente y se puede forzar con la variable `MCP_PYTHON`.

## Requisitos

- Python 3.10 o superior.
- Base PostgreSQL cargada (pasos del integrante 1).
- Entorno `.venv` con el MCPServer instalado (ver [`mcp_server/README.md`](../mcp_server/README.md)).
- Una `GOOGLE_API_KEY` de [Google AI Studio](https://aistudio.google.com/apikey).

## Instalación

Desde la raíz del repositorio, con `.venv` ya creado:

```bash
python3 -m venv .venv-agent
source .venv-agent/bin/activate
pip install -r agente_adk/requirements.txt
```

En Windows:

```powershell
python -m venv .venv-agent
.venv-agent\Scripts\activate
pip install -r agente_adk\requirements.txt
```

## Variables de entorno

En el `.env` de la raíz, además de las credenciales de base de datos:

```env
GOOGLE_API_KEY=
GOOGLE_GENAI_USE_VERTEXAI=FALSE
MODEL_NAME=gemini-3.6-flash
```

`MODEL_NAME` no se obtiene de ningún panel: es el identificador del modelo, un
texto que se escribe directamente. Se usa una versión **Flash** por la
recomendación del enunciado, ya que están optimizadas para alta velocidad y
tienen cuota gratuita.

Para ver qué modelos habilita una clave:

```bash
.venv-agent/bin/python -c "
import os
from dotenv import load_dotenv; load_dotenv('.env')
from google import genai
for m in genai.Client(api_key=os.environ['GOOGLE_API_KEY']).models.list():
    if 'generateContent' in (getattr(m, 'supported_actions', None) or []):
        print(m.name.replace('models/', ''))
"
```

El listado no es garantía: `gemini-2.5-flash` aparece pero la API lo rechaza
para claves nuevas con un `404` que indica migrar a `gemini-3.6-flash`. Por eso
`test_agente.py` valida el modelo con una llamada real antes de dar por buena la
configuración.

`MCP_PYTHON` solo se define si la detección automática del intérprete de `.venv`
falla.

## Ejecución

Interfaz web de ADK, desde la raíz del repositorio:

```bash
.venv-agent/bin/adk web
```

Abrir la URL que imprime la consola y elegir `agente_adk` en el selector de
agentes.

Modo terminal:

```bash
.venv-agent/bin/adk run agente_adk
```

En Windows se sustituye `.venv-agent/bin/` por `.venv-agent\Scripts\`.

## Pruebas

```bash
.venv-agent/bin/python -m agente_adk.test_agente
```

La prueba levanta el MCPServer por `stdio`, confirma que las 12 herramientas
estén expuestas al agente, valida que el `.env` tenga las claves necesarias y
comprueba con una llamada real que la API acepte el modelo configurado.

Validación completa de los puntos 2 al 6, que genera la evidencia del
requerimiento 3.3.c en [`docs/08-validacion-agente.md`](../docs/08-validacion-agente.md):

```bash
.venv-agent/bin/python -m agente_adk.validacion
```

Cada pregunta corre en una sesión nueva y se considera correcta si el agente
invoca la herramienta esperada del MCPServer. El script pausa 15 segundos entre
preguntas porque la capa gratuita de Gemini permite 20 solicitudes por minuto;
`VALIDACION_PAUSA` ajusta ese valor.

## Preguntas de validación

Estas preguntas cubren los puntos 2 al 6 y sirven como evidencia de la
integración exigida en el requerimiento técnico 3.3.b:

| Punto | Pregunta | Herramienta esperada |
| --- | --- | --- |
| 2.b | ¿Cuál es la media, mediana y moda de las variables numéricas? | `obtener_estadisticas_basicas` |
| 2.c | ¿Cómo se distribuyeron las ventas por mes? | `obtener_ventas_por_mes` |
| 2.c | ¿Cuántas ventas hubo por método de pago? | `obtener_distribucion_metodos_pago` |
| 3.a | ¿Qué meses tuvieron mayores y menores ventas? | `obtener_tendencias` |
| 3.b | ¿Cuál fue el navegador más y menos usado? | `obtener_distribucion_navegadores` |
| 3.c | ¿Cuántas ventas se pagaron contra entrega o en efectivo? | `obtener_distribucion_metodos_pago` |
| 3.d | ¿En qué meses se usaron más boletines y vales? | `obtener_uso_boletines_vales` |
| 4.a | ¿Cómo compran los clientes según su rango de edad? | `obtener_segmentacion_edad` |
| 4.b | ¿Hay diferencias de compra entre géneros? | `obtener_segmentacion_genero` |
| 4.c | ¿Cómo compran los clientes con boletín y con vale? | `obtener_segmentacion_boletin_vale` |
| 5.a | ¿Existe relación entre la edad y el total de la venta? | `obtener_correlacion_venta_edad` |
| 5.b | ¿El género influye en el método de pago preferido? | `obtener_correlacion_genero_pago` |
| 5.c | ¿Los clientes con boletín también usan vales? | `obtener_correlacion_boletin_vale` |
| 6 | Dame los datos para graficar las ventas por mes | `obtener_ventas_por_mes` |
| 6 | Muéstrame la gráfica de la evolución mensual de las ventas | `mostrar_grafica` |
| 6 | ¿Qué gráficas del análisis puedes mostrarme? | `listar_graficas` |

## Punto 6: gráficas dentro del chat

Además de las 12 herramientas del MCPServer, el agente registra dos
herramientas locales definidas en `graficas.py`:

- `listar_graficas`: catálogo de las nueve visualizaciones del informe.
- `mostrar_grafica(nombre)`: lee el PNG correspondiente de `graficas/` y lo
  guarda como **artifact** de la sesión con `tool_context.save_artifact`, de
  modo que la interfaz de `adk web` muestra la imagen directamente en la
  conversación, como exige el enunciado.

El agente no recalcula las gráficas: sirve las imágenes ya generadas por los
scripts de `analisis/`. Si falta algún PNG en `graficas/`, la herramienta lo
reporta y basta con volver a ejecutar esos scripts.
