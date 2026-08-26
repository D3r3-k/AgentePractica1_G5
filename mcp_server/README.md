# MCPServer — Práctica 1

Servidor MCP de solo lectura para exponer al agente conversacional los resultados del análisis de ventas online de 2021.

## Estado

El servidor y sus 12 herramientas ya fueron probados contra la base PostgreSQL cargada. La validación dentro del agente Google ADK queda pendiente de la integración del integrante 3.

## Arquitectura

```text
mcp_server/
├── __init__.py       # Declara el paquete Python
├── database.py       # Conexión y consultas de lectura a PostgreSQL
├── queries.py        # Consultas de análisis de los puntos 2 al 6
├── server.py         # Registro y ejecución de las herramientas MCP
└── test_server.py    # Pruebas de humo contra el servidor y la base
```

El servidor utiliza el SDK oficial de MCP para Python, `psycopg2` para PostgreSQL y variables de entorno para las credenciales. Las consultas no insertan, actualizan ni eliminan información.

## Requisitos

- Python 3.10 o superior.
- Acceso a la base PostgreSQL en la nube.
- Archivo `.env` en la raíz del proyecto.

## Instalación

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno

El archivo `.env` debe contener como mínimo:

```env
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_SCHEMA=geren2
DB_SSLMODE=require
DB_CONNECT_TIMEOUT=10
MCP_TRANSPORT=stdio
```

Nunca se debe subir `.env` al repositorio.

## Preparación de la base de datos

Si la base aún no está cargada:

```bash
.venv/bin/python db/limpieza.py
.venv/bin/python db/carga.py
```

En Windows:

```powershell
.venv\Scripts\python.exe db\limpieza.py
.venv\Scripts\python.exe db\carga.py
```

`db/carga.py` no sobrescribe datos existentes a menos que se ejecute explícitamente con `--reemplazar`.

## Ejecución del servidor

Para pruebas locales se utiliza `stdio`, que es el transporte predeterminado:

```bash
.venv/bin/python -m mcp_server.server
```

El proceso queda esperando solicitudes del cliente MCP y no muestra un menú en la consola. Esto es normal en `stdio`.

Para ejecutar el servidor como HTTP, configurar:

```env
MCP_TRANSPORT=streamable-http
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
```

Después iniciar con el mismo comando. El endpoint MCP queda disponible en la ruta estándar del transporte HTTP.

## Herramientas disponibles

| Herramienta | Resultado |
|---|---|
| `obtener_estadisticas_basicas` | Media, mediana y moda de variables numéricas |
| `obtener_ventas_por_mes` | Cantidad, total y promedio por mes; recibe `anio` |
| `obtener_distribucion_metodos_pago` | Ventas por método de pago |
| `obtener_distribucion_navegadores` | Ventas por navegador o canal registrado |
| `obtener_uso_boletines_vales` | Combinaciones de boletín y vale |
| `obtener_tendencias` | Meses con mayores y menores ventas; recibe `anio` |
| `obtener_segmentacion_edad` | Patrones por rango de edad; acepta límites opcionales |
| `obtener_segmentacion_genero` | Comparación entre géneros |
| `obtener_segmentacion_boletin_vale` | Patrones de compra por boletín y vale |
| `obtener_correlacion_venta_edad` | Correlación de Pearson entre edad y venta total |
| `obtener_correlacion_genero_pago` | Asociación género–método de pago mediante V de Cramér |
| `obtener_correlacion_boletin_vale` | Asociación boletín–vale mediante V de Cramér |

Todas las respuestas siguen este contrato:

```json
{
  "ok": true,
  "herramienta": "obtener_ventas_por_mes",
  "datos": [],
  "error": null
}
```

Si ocurre un error de conexión o de consulta, `ok` será `false` y no se mostrarán credenciales ni detalles internos de PostgreSQL.

## Pruebas

Con el `.env` configurado y la base disponible:

```bash
.venv/bin/python -m mcp_server.test_server
```

La prueba verifica que las 12 herramientas estén registradas, que respondan con el contrato esperado y que sus resultados sean serializables como JSON.

## Integración con Google ADK

El integrante 3 debe iniciar este servidor como proceso MCP usando `stdio` y registrar el comando:

```text
.venv/bin/python -m mcp_server.server
```

La validación de preguntas desde el agente ADK queda pendiente. Debe comprobarse que el agente pueda solicitar, como mínimo, ventas por mes, método de pago, tendencias, segmentación y correlaciones.

## Interpretación pendiente

El esquema utiliza `MetodoPago = 0` como `Efectivo` y `Navegador = 0` como `Tienda Física`. Para el punto 3.c, el equipo documentó la aclaración del auxiliar: efectivo y contra entrega se consideran con valor 0; las tarjetas no se consideran contra entrega.

