[ ← Regresar ](../README.md)

# Metodología

## Índice
- [Metodología](#metodología)
  - [Índice](#índice)
  - [Criterio general de selección](#criterio-general-de-selección)
  - [Origen de los datos graficados](#origen-de-los-datos-graficados)
  - [Selección de cada visualización](#selección-de-cada-visualización)
    - [1. Evolución mensual de las ventas — gráfico de líneas](#1-evolución-mensual-de-las-ventas--gráfico-de-líneas)
    - [2. Ventas por método de pago — gráfico de barras verticales](#2-ventas-por-método-de-pago--gráfico-de-barras-verticales)
    - [3. Ventas por navegador / canal — gráfico de barras horizontales](#3-ventas-por-navegador--canal--gráfico-de-barras-horizontales)
    - [4. Distribución de ventas por boletín y vale — barras agrupadas](#4-distribución-de-ventas-por-boletín-y-vale--barras-agrupadas)
    - [5. Uso de boletines y vales por mes — barras agrupadas](#5-uso-de-boletines-y-vales-por-mes--barras-agrupadas)
  - [Decisiones de diseño transversales](#decisiones-de-diseño-transversales)
  - [Visualizaciones descartadas](#visualizaciones-descartadas)

## Criterio general de selección

La elección de cada gráfico no partió del catálogo de tipos disponibles, sino de
la pregunta de negocio que debía responder. Antes de escribir código se
clasificó cada hallazgo del análisis exploratorio y de tendencias según su
naturaleza estadística, y esa clasificación determinó la forma visual:

| Naturaleza del hallazgo | Forma visual apropiada | Razón |
| --- | --- | --- |
| Variable continua en el tiempo | Línea | La continuidad del trazo comunica que las observaciones están ordenadas y son comparables entre sí. |
| Comparación entre categorías excluyentes | Barras | La longitud es el atributo visual que el ojo compara con mayor precisión. |
| Categorías con etiquetas largas | Barras horizontales | Evita rotar el texto del eje, que reduce la legibilidad. |
| Dos series comparables sobre el mismo eje | Barras agrupadas | Permite comparar tanto entre categorías como entre series sin superponer información. |

El principio rector fue que cada gráfico respondiera **una sola pregunta** de
forma inequívoca. Cuando una visualización intentaba responder dos, se dividió
en dos gráficos distintos.

## Origen de los datos graficados

Todas las visualizaciones se construyeron a partir de consultas SQL ejecutadas
directamente contra la base de datos PostgreSQL en la nube, no sobre el archivo
`.csv` original. Esta decisión responde al punto 2.a del enunciado («obtener los
datos de la base de datos») y garantiza que las cifras del informe, las que
devuelve el MCPServer y las que muestra el agente conversacional provengan de
una misma fuente.

La agregación se delegó a PostgreSQL (`GROUP BY`, `SUM`, `COUNT`, `AVG`) en
lugar de resolverla en Python: el motor procesa la agregación sobre los índices
existentes y solo transporta el resultado, que son unas pocas decenas de filas.

El script [`analisis/exploratorio.py`](../analisis/exploratorio.py) reutiliza las
funciones del módulo [`mcp_server/queries.py`](../mcp_server/queries.py), de modo
que el informe y el agente conversacional comparten exactamente la misma lógica
de consulta. Este bloque añadió dos consultas propias, que son las que el
MCPServer no expone: el desglose mensual de boletines y vales (punto 3.d) y el
cruce entre método de pago y canal de origen, necesario para separar el efectivo
cobrado en caja del cobrado al momento de la entrega (punto 3.c).

## Selección de cada visualización

### 1. Evolución mensual de las ventas — gráfico de líneas

**Pregunta:** ¿cómo se comportaron las ventas a lo largo de 2021 y en qué meses
alcanzaron su máximo y su mínimo? (puntos 2.c y 3.a)

Se eligió un gráfico de líneas porque el mes es una variable ordenada y continua:
enero precede a febrero, y esa secuencia es parte del significado del dato. Un
gráfico de barras habría representado los mismos valores, pero presentando los
meses como categorías independientes, lo que oculta la forma de la tendencia.

Los doce puntos llevan su valor exacto anotado, y los dos meses extremos se
resaltan además con color y con la palabra «Máximo» o «Mínimo». Diciembre y
noviembre son precisamente la respuesta al punto 3.a, y el gráfico debía
señalarlos sin exigir que el lector recorriera los doce puntos comparándolos.

La posición de cada etiqueta se calcula según la forma de la curva: en los
valles se escribe debajo del punto, en los picos encima, y en los tramos
ascendentes o descendentes se recuesta hacia el lado ya recorrido por la línea.
Así ninguna cifra se encima con el trazo ni con las etiquetas vecinas.

El eje vertical no arranca en cero. Es una decisión deliberada: los totales
mensuales se mueven en un rango estrecho y, forzando el origen en cero, la línea
quedaría prácticamente plana y la variación real resultaría invisible. Como el
gráfico describe una evolución y no compara magnitudes absolutas entre
categorías, el recorte del eje es una convención aceptada para series de tiempo;
además, al estar rotulados los doce valores, la lectura no depende en ningún
momento de estimar la altura contra el eje.

### 2. Ventas por método de pago — gráfico de barras verticales

**Pregunta:** ¿cómo se reparten las ventas entre efectivo, crédito y débito?
(puntos 2.c y 3.c)

Con solo tres categorías excluyentes y sin orden intrínseco entre ellas, las
barras verticales son la forma más directa de comparación. Se ordenaron de mayor
a menor frecuencia para que el ranking se lea sin esfuerzo, y se destacó la
categoría dominante con un color más intenso.

Se descartó un gráfico circular. Aunque el reparto suma el 100 % y un pastel
parecería natural, comparar ángulos es notablemente menos preciso que comparar
longitudes, y la diferencia entre débito (22.6 %) y efectivo (18.6 %) se
distingue peor en un círculo que en dos barras contiguas.

Cada barra se etiquetó con el conteo absoluto y el porcentaje: el porcentaje
comunica el peso relativo y el absoluto permite dimensionar la muestra.

### 3. Ventas por navegador / canal — gráfico de barras horizontales

**Pregunta:** ¿cuál es el canal más preferido y cuál el menos popular?
(puntos 2.c y 3.b)

Se mantuvieron las barras por tratarse de una comparación entre categorías, pero
se giraron a horizontal por una razón práctica: las etiquetas («Tienda Física»,
«Navegador 1» … «Navegador 4») son largas y en orientación vertical obligarían a
rotar el texto en diagonal. En horizontal, cada nombre se lee de corrido junto a
su barra.

La orientación además aporta una ventaja interpretativa: al ordenar de mayor a
menor de arriba hacia abajo, el gráfico se lee como un ranking, que es
exactamente lo que pide el punto 3.b.

Se coloreó «Tienda Física» de forma distinta al resto porque no es un navegador
sino el canal presencial, y agrupar ambas cosas bajo un mismo color sugeriría una
comparación entre iguales que no lo es. La distinción visual permite responder
dos preguntas en un solo gráfico sin confundirlas: el canal más usado en términos
absolutos es la tienda física (3,523 ventas, 54.2 %), mientras que entre los
navegadores propiamente dichos el preferido es el Navegador 1 (1,273 ventas) y el
menos popular el Navegador 4 (197 ventas).

Se graficó la **cantidad** de ventas y no el monto acumulado porque la pregunta
es de preferencia de canal, y la preferencia se expresa en número de
transacciones, no en dinero.

### 4. Distribución de ventas por boletín y vale — barras agrupadas

**Pregunta:** ¿qué proporción de las ventas involucró boletín y qué proporción
involucró vale? (punto 2.c)

El punto 2.c enumera cinco distribuciones que deben visualizarse, y boletín y
vale son dos de ellas. Como ambas son variables binarias del mismo tipo —cada
una divide las ventas en «sí la usó» y «no la usó»— se resolvieron en un solo
gráfico de barras agrupadas en lugar de dos gráficos separados: compartir el eje
vertical permite comparar directamente la penetración de un instrumento frente
al otro, que es el hallazgo relevante.

Se optó por representar ambas categorías (sí y no) y no únicamente los casos
positivos, porque una distribución solo se comprende cuando se ve contra su
complemento: 2,921 ventas con boletín solo significan algo al lado de las 3,579
sin él.

La lectura resultante es contundente: el boletín alcanza al 44.9 % de las ventas
mientras que el vale apenas llega al 19.3 %, es decir, el boletín tiene más del
doble de penetración que el vale.

### 5. Uso de boletines y vales por mes — barras agrupadas

**Pregunta:** ¿en qué meses se usaron más boletines y vales? (punto 3.d)

Este hallazgo involucra dos series (boletines y vales) sobre un mismo eje
temporal de doce meses. Se optó por barras agrupadas en lugar de barras apiladas
porque boletín y vale **no son categorías excluyentes**: una misma venta puede
registrar ambos, de modo que apilarlas sumaría casos duplicados y produciría una
altura sin significado. Agrupadas, cada barra conserva su propia línea base y
ambas magnitudes se comparan contra el eje y entre sí.

Tampoco se usó un gráfico de líneas, pese al eje temporal, porque aquí el
interés no está en la forma de la tendencia sino en identificar meses puntuales
de mayor uso; las barras individualizan cada mes y facilitan esa lectura.

La diferencia de escala entre ambas series se conserva a propósito: que los
boletines dupliquen consistentemente a los vales es en sí mismo un hallazgo sobre
la penetración de cada instrumento comercial.

## Decisiones de diseño transversales

Se aplicaron los mismos criterios a las cinco visualizaciones para que el
informe se lea como un conjunto coherente:

- **Paleta constante.** Un azul institucional para la serie principal, verde para
  los valores destacados en positivo y rojo para los mínimos. El color se usa
  siempre para codificar significado, nunca como adorno.
- **Todo valor rotulado sobre el dato.** Sin excepción, cada barra y cada punto
  de las cinco visualizaciones muestra su cifra exacta junto al elemento que la
  representa, y en las distribuciones se añade el porcentaje sobre el total. El
  criterio es que ninguna conclusión dependa de que el lector estime una altura
  o una longitud contra el eje: el gráfico debe entregar el dato, no insinuarlo.
- **Ejes siempre identificados.** Los cinco gráficos rotulan ambos ejes con la
  magnitud y su unidad («Total de ventas (quetzales)», «Cantidad de ventas»,
  «Mes»), y las series de las barras agrupadas se distinguen con leyenda.
- **Eliminación de elementos no informativos.** Se retiraron los bordes superior
  y derecho, y las rejillas se dejaron punteadas y tenues, de modo que el dato
  domine visualmente sobre la estructura del gráfico.
- **Exportación a 150 ppp** con recorte ajustado, resolución suficiente para que
  el texto se lea con nitidez al incorporar las imágenes al PDF final.
- **Reproducibilidad.** Las gráficas no se editaron a mano: se regeneran por
  completo ejecutando `python analisis/exploratorio.py`, de forma que cualquier
  corrección en los datos se refleja en las imágenes sin trabajo manual.

## Visualizaciones descartadas

Se evaluaron y descartaron tres alternativas, por las razones siguientes:

- **Gráfico circular para el método de pago.** La comparación de ángulos es menos
  precisa que la de longitudes; se prefirieron barras.
- **Barras apiladas para boletín y vale.** Las dos categorías no son excluyentes,
  por lo que el total apilado carecería de interpretación.
- **Histograma de montos de venta.** Aunque describe la distribución de la
  variable, el punto 2.b ya queda cubierto con las medidas de tendencia central,
  y la distribución por cliente corresponde al bloque de segmentación.
