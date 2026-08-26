# Pendientes para cerrar la entrega

Estado al **26 de agosto de 2026**, verificado contra `informe final.docx` y contra la
base de datos.

El informe está completo salvo por lo que se lista aquí. Los encabezados de las
secciones pendientes ya están puestos en el documento, de modo que incorporarlas es
solo pegar el texto debajo de cada uno.

---

## 🔴 Bloquea la nota

### 1. Faltan los tres aportes del integrante 1

Es lo único que impide cumplir los puntos 7.a, 7.b y 8 del enunciado.

| Sección | Estado en el Word | Referencia de extensión |
| :--- | :--- | :--- |
| Conclusión Clave 1 (punto 7.a) | ❌ vacía | Las otras tres: 3,477 · 3,929 · 4,033 caracteres |
| Dos acciones concretas Clave #1 (punto 7.b) | ❌ vacía | Las otras cuatro: 1,972 · 2,699 · 2,795 · 2,916 |
| Pregunta 8.a — ¿Cómo diferenciarse de la competencia? | ❌ vacía | Las otras cuatro: 1,227 · 2,997 · 3,628 · 4,206 |

**Responsable:** integrante 1 — Derek (202001151).

El punto 7.a exige **cuatro conclusiones clave de mínimo 20 líneas cada una**, y el
7.b **dos acciones concretas por estudiante**. Con cuatro de cinco bloques entregados,
ninguno de los dos requisitos se cumple todavía.

## 🟡 Afectan la presentación

### 2. Tres archivos enlazados en el README que no existen

[`README.md`](../README.md) menciona `docs/08-validacion-agente.md`,
`docs/09-aportes-integrante3.md` y `docs/10-implementacion-agente.md`. Ninguno existe
en ninguna rama del repositorio.

Además [`docs/01-planificacion.md`](../docs/01-planificacion.md) cita el primero como
evidencia de que el agente responde las 16 preguntas del alcance, que es justamente lo
que la rúbrica pide comprobar.

**Responsable:** integrante 3 — Daniel (202300512). O se suben los tres documentos, o
se quitan las menciones del README.

### 3. El README del MCPServer quedó desactualizado

[`mcp_server/README.md`](../mcp_server/README.md) dice en su sección «Estado» que *«la
validación dentro del agente Google ADK queda pendiente de la integración del
integrante 3»*, repite lo mismo en «Integración con Google ADK» y cierra con una
sección «Interpretación pendiente». Las tres cosas ya se resolvieron. Leído por el
catedrático, sugiere trabajo incompleto que sí se completó.

**Responsable:** integrantes 2 y 3.

### 4. El diagrama de la base de datos declara un tipo que no coincide

En [`docs/assets/07-diagrama-bd.svg`](../docs/assets/07-diagrama-bd.svg), los campos
`boletin` y `vale` aparecen como `BOOLEAN`, pero
[`db/schema.sql`](../db/schema.sql) los declara `SMALLINT NOT NULL CHECK (… IN (0, 1))`.
El diagrama está impreso en el capítulo 4 del informe.

**Responsable:** integrante 1 — Derek (202001151), que es quien generó el diagrama.

---

## ✅ Cerrado

| Bloque | Responsable | Evidencia |
| :--- | :--- | :--- |
| Punto 1 — Preparación de datos | Derek (202001151) | `db/limpieza.py`, `db/carga.py`, `db/schema.sql` |
| Punto 2 — Análisis exploratorio | Fátima (análisis) · Valery (redacción) | `docs/12-exploratorio-tendencias.md` |
| Punto 3 — Análisis de tendencias | Fátima (análisis) · Valery (redacción) | `docs/12-exploratorio-tendencias.md` |
| Punto 4 — Segmentación de clientes | Valery (202300794) | `docs/11-segmentacion-correlacion.md` |
| Punto 5 — Análisis de correlación | Valery (202300794) | `docs/11-segmentacion-correlacion.md` |
| Punto 6 — Visualización: 12 gráficas de 10 tipos | Fátima (5) · Valery (4) · Derek (3) | `graficas/01` a `graficas/12` |
| Punto 7.a — Conclusión clave 2 | Juan Esteban (202300431) | `docs/04-conclusiones.md` |
| Punto 7.a — Conclusiones clave 3 y 4 | Daniel y Fátima | `docs/04-conclusiones.md` |
| Punto 7.b — Acciones de los integrantes 2, 3, 4 y 5 | Juan Esteban, Daniel, Fátima, Valery | `docs/05-recomendaciones.md` |
| Punto 8.b | Juan Esteban (202300431) | `docs/06-respuestas.md` |
| Punto 8.c | Daniel (202300512) | `docs/06-respuestas.md` |
| Punto 8.d | Fátima (202300434) | `docs/06-respuestas.md` |
| Punto 8.e | Valery (202300794) | `docs/06-respuestas.md` |
| 3.3 — Base de datos relacional en la nube | Derek (202001151) | PostgreSQL, conexión verificada |
| 3.3 — Lenguaje de análisis de datos | Fátima, Valery y Derek | Python 3.12 |
| 3.3 — MCPServer con 12 herramientas | Juan Esteban (202300431) | `mcp_server/` |
| 3.3 — Agente Google ADK | Daniel (202300512) | `agente_adk/` |
| Entregable — Proceso de análisis | Derek (202001151) | `docs/02-proceso-analisis.md` |
| Entregable — Metodología (12 visualizaciones) | Fátima y Valery | `docs/03-metodologia.md` |
| Entregable — Diagrama de BD | Derek (202001151) | `docs/07-diagrama-bd.md` |
| Entregable — Planificación | Valery (202300794) | `docs/01-planificacion.md` |
| Entregable — Código | Todo el equipo | Capítulo 10 del informe |
| Entregable — Presentación | Valery (202300794) | `informe/SOG2-2S26_grupo5.pdf` |
| Corrección de cifras de las acciones Clave #3 y de la respuesta 8.c | Daniel (202300512) · aplicada por Valery | Verificado contra PostgreSQL el 26/08 |

---

## Pasos finales, en este orden

El orden importa: si se borra la página en blanco o se actualiza el índice antes de
pegar los textos, la paginación se vuelve a desfasar y hay que repetirlo.

1. **Integrante 1** entrega su conclusión, sus dos acciones y su respuesta 8.a.
2. **Integrante 5** pega ese aporte en `informe final.docx`.
3. Actualizar el índice: clic derecho sobre él → Actualizar campos → Actualizar toda
   la tabla.
4. Revisar que ninguna gráfica quede partida entre dos páginas.
5. Borrar la página en blanco del final.
6. Exportar como **`SOG2-2S26_grupo5.pdf`** y entregar en UEDI.

> **Nota.** El documento editable ya está en `informe/informe final.docx`, junto al
> PDF. El PDF de esa carpeta corresponde a la exportación del 25/08 y habrá que
> reemplazarlo por la versión final tras incorporar el aporte pendiente.
