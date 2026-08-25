[ ← Regresar ](../README.md)

# Planificacion

## Integrante 1 — Datos y Base de Datos

- [x] 1. Preparación de datos:
  - [x] a. Extraer los datos del archivo .csv.
  - [x] b. Verificar si hay valores faltantes o duplicados y decidir cómo manejarlos.
  - [x] c. Asegurarse de que los tipos de datos sean correctos para cada columna.
  - [x] d. Cargar los datos a una base de datos SQL en la nube.
- [x] 3.3 Requerimientos técnicos:
  - [x] a. Base de datos relacional implementada en la nube.
- [ ] 7. Conclusiones y recomendaciones:
  - [ ] a. Conclusión clave #1 (mín. 20 líneas).
  - [ ] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [ ] 8. Responder a las preguntas:
  - [ ] a. ¿Cómo podrían los insights obtenidos ayudar a diferenciarse de la competencia?
- [x] Entregables (sección 4):
  - [x] a. Diagrama: Diagrama de la base de datos.
  - [x] b. Proceso de análisis: Describa el enfoque paso a paso que siguieron para limpiar y preparar los datos.

## Integrante 2 — MCPServer

- [x] 3.3 Requerimientos técnicos:
  - [x] a. Crear el MCPServer y exponer las herramientas de análisis.
  - [x] b. Validar la integración del MCPServer con el agente conversacional de Google ADK (las 12 herramientas responden al agente por `stdio`).
- [ ] 7. Conclusiones y recomendaciones:
  - [x] a. Conclusión clave #2 (mín. 20 líneas).
  - [x] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [ ] 8. Responder a las preguntas:
  - [x] b. ¿Qué decisiones estratégicas podrían tomarse basándose en este análisis para aumentar las ventas y la satisfacción del cliente?
- [ ] Entregables (sección 4):
  - [x] a. Código: Código utilizado para su implementación.
  - [x] b. README y pruebas del MCPServer.

## Integrante 3 — Agente conversacional (Google ADK)

- [x] 3.3 Requerimientos técnicos:
  - [x] a. Google ADK para crear el agente de IA conversacional (`agente_adk/agent.py`).
  - [x] b. Usar cualquier modelo de IA. Se usa `gemini-3.5-flash-lite`, validado con una llamada real.
  - [x] c. Los puntos del 2 al 6, el chat de IA debe ser capaz de entregar los resultados según se soliciten (16/16 preguntas). Evidencia en [`08-validacion-agente.md`](08-validacion-agente.md).
- [x] 7. Conclusiones y recomendaciones:
  - [x] a. Conclusión clave #3 (mín. 20 líneas).
  - [x] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [x] 8. Responder a las preguntas:
  - [x] c. ¿Cómo podría este análisis de datos ayudar a la empresa a ahorrar costos o mejorar la eficiencia operativa?
- [ ] Entregables (sección 4):
  - [x] a. Código: agente ADK, pruebas y validación automatizada.
  - [x] b. Bitácora de implementación 

## Integrante 4 — Análisis exploratorio y de tendencias

> [!NOTE]
> **Aclaración del auxiliar sobre el punto 3.c:**
>
> Tomar el valor 0 tanto para Efectivo como contra entrega, los pagos con tarjeta ya sea débito o crédito no se consideran como pagos contra entrega

- [ ] 3.3 Requerimientos técnicos:
  - [ ] a. Cualquier lenguaje de análisis de datos como Python o R.
- [ ] 2. Análisis exploratorio:
  - [ ] a. Obtener los datos de la base de datos.
  - [ ] b. Calcular estadísticas básicas (media, mediana, moda) para las variables numéricas.
  - [ ] c. Crear visualizaciones para mostrar la distribución de ventas por mes, método de pago, navegador, Boletín y Vale.
- [ ] 3. Análisis de tendencias:
  - [ ] a. Determinar los meses con mayores y menores ventas.
  - [ ] b. Identificar el navegador más preferido y el menos popular.
  - [ ] c. Identificar total de ventas fueron pagadas contra entrega o con pago en efectivo.
  - [ ] d. Identificar los meses donde se usaron más boletines y vales.
- [ ] 6. Visualización de datos:
  - [ ] a. Aportar 4 de los 7 gráficos diferentes mínimos requeridos.
- [ ] 7. Conclusiones y recomendaciones:
  - [ ] a. Conclusión clave #4 (mín. 20 líneas).
  - [ ] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [ ] 8. Responder a las preguntas:
  - [ ] d. ¿Qué datos adicionales recomendarían para obtener insights aún más valiosos en el futuro?
- [ ] Entregables (sección 4):
  - [ ] a. Metodología: Explique cómo seleccionaron las visualizaciones más apropiadas para sus hallazgos.

## Integrante 5 — Segmentación, correlación e informe final

- [x] 4. Segmentación de clientes:
  - [x] a. Agrupar a los clientes por edad y analizar sus patrones de compra.
  - [x] b. Comparar el comportamiento de compra entre géneros.
  - [x] c. Agrupar los clientes por boletín y vales y analizar sus patrones de compra.
- [x] 5. Análisis de correlación:
  - [x] a. Investigar si existe una relación entre el total de la venta y la edad del cliente.
  - [x] b. Examinar si hay una correlación entre el género del cliente y el método de pago preferido.
  - [x] c. Investigar si existe una correlación entre los clientes que utilizan boletines y vales.
- [x] 6. Visualización de datos:
  - [x] a. Aportar 3 de los 7 gráficos diferentes mínimos requeridos. Se aportaron 4: barras verticales, barras apiladas al 100 %, dispersión y mapa de calor.
- [x] 7. Conclusiones y recomendaciones:
  - [x] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [x] 8. Responder a las preguntas:
  - [x] e. ¿Implementar una Chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?
- [x] Entregables (sección 4):
  - [x] a. Presentación: Documento presentable, bien redactado de acuerdo con un informe final conforme a su puesto de analista Junior. Consolidación del PDF SOG2-2S26_grupo5.pdf.
  - [x] b. Planificación: ¿Cómo se dividieron las tareas entre los miembros del equipo? ¿Qué herramientas y tecnologías decidieron utilizar y por qué? ¿Cómo establecieron los plazos para cada fase del proyecto?

Resultados del bloque en [`11-segmentacion-correlacion.md`](11-segmentacion-correlacion.md);
código en [`analisis/segmentacion.py`](../analisis/segmentacion.py).

---

# Entregable «Planificación»

## ¿Cómo se dividieron las tareas entre los miembros del equipo?

El criterio de división no fue repartir los ocho puntos del alcance en partes
iguales, sino **cortar el proyecto por sus dependencias técnicas**. El enunciado
describe una cadena: sin datos limpios no hay base de datos, sin base de datos no
hay consultas, sin consultas no hay servidor MCP, sin servidor no hay agente
conversacional. Repartir por puntos habría dejado a varias personas bloqueadas
esperando el trabajo de otra.

Se definieron entonces cinco bloques, cada uno con una frontera clara y un
entregable propio:

| # | Integrante | Carné | Bloque | Puntos del alcance |
| :---: | :--- | :---: | :--- | :--- |
| 1 | Derek Francisco Orellana Ibáñez | 202001151 | Datos y base de datos | 1, diagrama, proceso de análisis |
| 2 | Juan Esteban Chacón Trampe | 202300431 | MCPServer | 3.3, código y pruebas |
| 3 | Daniel Andree Hernandez Flores | 202300512 | Agente conversacional (Google ADK) | 3.3, validación 2 al 6 |
| 4 | Fátima Florisel Cerezo Paredes | 202300434 | Análisis exploratorio y de tendencias | 2, 3, metodología, 4 gráficas |
| 5 | Valery Pamela Alarcon Ramos | 202300794 | Segmentación, correlación e informe final | 4, 5, 4 gráficas, consolidación del PDF |

Tres decisiones sobre este reparto merecen explicación:

**La interfaz entre bloques se acordó antes de escribir código.** El integrante 2
definió el contrato de respuesta del MCPServer —`{ok, herramienta, datos, error}`—
al inicio, lo que permitió que el integrante 3 avanzara en el agente y la integrante
5 en el análisis sin esperar a que las doce herramientas estuvieran terminadas. El
módulo `mcp_server/queries.py` quedó como fuente única de consultas: los scripts de
análisis lo importan en lugar de reescribir el SQL, de modo que el informe, el
servidor y el agente devuelven por construcción las mismas cifras.

**El punto 6 se repartió entre dos personas.** El enunciado pide un mínimo de siete
gráficos. Se asignaron cuatro a la integrante 4 (distribuciones y tendencias) y tres
como mínimo a la integrante 5 (segmentación y correlación); esta última aportó
cuatro, con lo que el proyecto cierra con **nueve visualizaciones**. Como ambas
trabajaban sobre el mismo entregable visual, se fijaron por adelantado la paleta, el
formato de etiquetas y el pie de fuente, y esos criterios quedaron documentados en
[`03-metodologia.md`](03-metodologia.md).

**La integrante 5 no redacta conclusión propia.** El punto 7.a pide exactamente
cuatro conclusiones clave y el equipo es de cinco personas. Se acordó que quien
consolida el PDF asumiera a cambio la coherencia del documento completo:
verificación de que las cifras citadas en las cuatro conclusiones coinciden con las
que devuelve la base de datos, unificación de estilo y armado final. Las dos acciones
concretas del punto 7.b sí las aporta cada integrante, incluida ella, porque el
enunciado las pide **por estudiante**.

## ¿Qué herramientas y tecnologías decidieron utilizar y por qué?

| Herramienta | Uso en el proyecto | Por qué se eligió |
| :--- | :--- | :--- |
| **PostgreSQL** (nube) | Base de datos relacional | El enunciado exige base relacional en la nube y penaliza con −20 % cada incumplimiento. Se prefirió a MySQL por `percentile_cont`, `mode()` y `corr()`, que resuelven en el motor la mediana, la moda y la correlación de Pearson del punto 5.a. |
| **Python 3.10+** | Limpieza, carga, análisis y gráficas | Cumple el requisito de lenguaje de análisis y es el único ecosistema donde conviven `psycopg2`, `matplotlib` y el SDK de MCP sin puentes entre lenguajes. |
| **pandas** | Limpieza y normalización del CSV | Resuelve en pocas líneas la normalización de nombres, la coerción de tipos y la detección de nulos y duplicados del punto 1.b y 1.c. |
| **psycopg2** | Conexión a PostgreSQL | Controlador estándar. Se usó `psycopg2.sql` para componer identificadores de forma segura y `RealDictCursor` para recibir filas como diccionarios. |
| **matplotlib** | Las nueve visualizaciones | Da control fino sobre la posición de cada etiqueta, que era necesario para cumplir el criterio de rotular todos los valores sin superposiciones. Se descartó Seaborn: aporta estética por defecto pero menos control, y aquí el diseño estaba definido de antemano. |
| **MCP (Model Context Protocol)** | Servidor de doce herramientas | Requisito explícito del enunciado. Se eligió transporte `stdio` porque el agente levanta el servidor como subproceso y no hace falta exponer un puerto. |
| **Google ADK + Gemini Flash-Lite** | Agente conversacional | Requisito del enunciado; el propio documento recomienda las versiones Flash o Flash-Lite por velocidad y uso gratuito dentro de sus límites. |
| **Git y GitHub** | Control de versiones | Plataforma indicada en la sección 5. Se trabajó con ramas por integrante (`feat/<carné>/<tema>`) sobre `develop`, con revisión por *pull request* antes de integrar. |
| **Markdown → HTML → PDF** | Informe final | La documentación vive versionada en Markdown junto al código; el PDF se genera desde una plantilla HTML propia con Chromium en modo headless. Evita el paso manual por procesador de texto y permite regenerar el entregable con un comando cuando cambia una cifra. |

Dos decisiones técnicas se tomaron por restricción y conviene dejarlas registradas.
La primera es que el agente vive en un entorno virtual separado (`.venv-agent`),
porque `google-adk` requiere `mcp<2` mientras que el MCPServer usa `mcp` 2.x; aislar
los entornos fue más barato que degradar el servidor. La segunda es que el análisis
estadístico se resolvió **sin SciPy**: los contrastes que necesitaba el punto 5
—significancia de Pearson sobre muestra grande y chi-cuadrado con uno y dos grados de
libertad— tienen forma cerrada y se implementaron con `math`, evitando sumar una
dependencia pesada al proyecto por tres fórmulas.

## ¿Cómo establecieron los plazos para cada fase del proyecto?

Los plazos se derivaron de la cadena de dependencias, no del calendario. Cada fase se
programó para terminar cuando la siguiente la necesitaba, y se fijó un punto de
control al final de cada una: hasta que el bloque anterior no estuviera integrado en
`develop` y verificado, el siguiente no arrancaba. El tiempo estimado por el enunciado
es de 20 horas, que se distribuyeron en cinco fases sobre una semana.

| Fase | Días | Responsable | Condición de cierre |
| :--- | :--- | :--- | :--- |
| 0. Arranque y estructura | 13 y 16 ago | Integrante 1 | Repositorio, `.env.example`, estructura de carpetas y planificación acordada |
| 1. Datos y base de datos | 16 ago | Integrante 1 | CSV limpio cargado en PostgreSQL y diagrama entregado |
| 2. MCPServer | 17 ago | Integrante 2 | Las 12 herramientas responden con el contrato acordado |
| 3. Agente y análisis exploratorio | 17 ago | Integrantes 3 y 4 | Agente responde los puntos 2 al 6; 5 gráficas generadas |
| 4. Segmentación y correlación | 18 y 19 ago | Integrante 5 | Puntos 4 y 5 resueltos; 4 gráficas generadas |
| 5. Consolidación del informe | 19 ago | Integrante 5 | PDF `SOG2-2S26_grupo5.pdf` armado y revisado |

Las fases 2, 3 y 4 pudieron solaparse parcialmente gracias al contrato de respuesta
acordado de antemano: mientras el integrante 2 terminaba las últimas herramientas, el
3 ya integraba el agente contra las primeras y la 5 trabajaba directamente sobre
`queries.py`.

**Un desfase real y cómo se manejó.** Durante la fase 3 se detectó un error en la
limpieza de datos que alteraba el total de ventas por mes. Corregirlo obligó a
recargar la base y a regenerar las gráficas ya producidas (*commits* `7d00259` y
`fab64c6`). El costo fue bajo porque las gráficas se generan por script y ninguna se
había editado a mano: bastó volver a ejecutar el análisis. Esa fue justamente la razón
por la que se decidió desde el inicio no retocar imágenes manualmente, y el incidente
confirmó la decisión.

**Reserva final.** Se dejó deliberadamente la consolidación del PDF como última fase
y con holgura, porque es la única que depende de que **todos** los bloques estén
cerrados. Los pendientes que la integrante 5 detectó al consolidar están registrados
en [`PENDIENTES.md`](../PENDIENTES.md) con su responsable, de modo que el cierre no
dependa de la memoria de nadie.
