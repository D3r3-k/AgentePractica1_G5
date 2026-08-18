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

- [ ] 4. Segmentación de clientes:
  - [ ] a. Agrupar a los clientes por edad y analizar sus patrones de compra.
  - [ ] b. Comparar el comportamiento de compra entre géneros.
  - [ ] c. Agrupar los clientes por boletín y vales y analizar sus patrones de compra.
- [ ] 5. Análisis de correlación:
  - [ ] a. Investigar si existe una relación entre el total de la venta y la edad del cliente.
  - [ ] b. Examinar si hay una correlación entre el género del cliente y el método de pago preferido.
  - [ ] c. Investigar si existe una correlación entre los clientes que utilizan boletines y vales.
- [ ] 6. Visualización de datos:
  - [ ] a. Aportar 3 de los 7 gráficos diferentes mínimos requeridos.
- [ ] 7. Conclusiones y recomendaciones:
  - [ ] b. Sugerir dos acciones concretas que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.
- [ ] 8. Responder a las preguntas:
  - [ ] e. ¿Implementar una Chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?
- [ ] Entregables (sección 4):
  - [ ] a. Presentación: Documento presentable, bien redactado de acuerdo con un informe final conforme a su puesto de analista Junior. Consolidación del PDF SOG2-2S26_grupo#.pdf.
  - [ ] b. Planificación: ¿Cómo se dividieron las tareas entre los miembros del equipo? ¿Qué herramientas y tecnologías decidieron utilizar y por qué? ¿Cómo establecieron los plazos para cada fase del proyecto?
