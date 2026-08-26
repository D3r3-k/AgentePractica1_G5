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
    - [6. Ticket promedio por rango de edad — gráfico de barras verticales](#6-ticket-promedio-por-rango-de-edad--gráfico-de-barras-verticales)
    - [7. Método de pago por género — barras horizontales apiladas al 100 %](#7-método-de-pago-por-género--barras-horizontales-apiladas-al-100-)
    - [8. Edad frente a total de la venta — gráfico de dispersión](#8-edad-frente-a-total-de-la-venta--gráfico-de-dispersión)
    - [9. Boletín y vale frente al ticket — mapa de calor](#9-boletín-y-vale-frente-al-ticket--mapa-de-calor)
    - [10. Distribución del total de la venta — histograma](#10-distribución-del-total-de-la-venta--histograma)
    - [11. Total de la venta por rango de edad — diagrama de caja](#11-total-de-la-venta-por-rango-de-edad--diagrama-de-caja)
    - [12. Composición del 63.9 % presencial — gráfico de cascada](#12-composición-del-639--presencial--gráfico-de-cascada)
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

El bloque de segmentación y correlación sigue el mismo criterio en
[`analisis/segmentacion.py`](../analisis/segmentacion.py), que produce las
visualizaciones 6 a 9 y comparte paleta, formato de etiquetas y pie de fuente con el
script anterior, de modo que las doce gráficas se lean como un solo conjunto. Sus
consultas propias son el desglose enriquecido por rango de edad y por género —el
MCPServer entrega el ticket, pero no la penetración de boletín, vale y canal dentro
de cada segmento—, el par (edad, venta_total) sin agregar que alimenta el diagrama
de dispersión y la correlación de Spearman, que `corr()` de PostgreSQL no calcula.

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

### 6. Ticket promedio por rango de edad — gráfico de barras verticales

**Pregunta:** ¿gastan distinto los clientes según su edad? (punto 4.a)

Se graficó el **ticket promedio** y no la facturación total del tramo. Es una
distinción que cambia por completo la pregunta que responde el gráfico: la
facturación total seguiría el tamaño de cada segmento y mostraría, trivialmente,
que los tramos con más clientes venden más. El ticket promedio normaliza por
tamaño y permite comparar comportamiento, que es lo que pide el punto.

Aquí el eje vertical **sí arranca en cero**, al contrario que en la evolución
mensual. La diferencia de criterio es deliberada: este gráfico compara magnitudes
entre categorías independientes, y recortar la base convertiría una brecha real de
Q20.21 en una montaña visual que sugeriría un hallazgo inexistente. Que las cinco
barras se vean casi iguales **es** el hallazgo.

Se añadió una línea horizontal punteada con el promedio general (Q206.24) como
referencia: sin ella, el lector no tendría contra qué juzgar si un tramo está alto o
bajo. Las cifras se rotularon **dentro** de cada barra y no encima, porque a la
altura del extremo superior de las barras pasa justamente esa línea de referencia y
las etiquetas se encimarían con ella. Se destacaron en verde el tramo de mayor
ticket y en rojo el de menor, siguiendo la misma convención de color del resto del
informe.

### 7. Método de pago por género — barras horizontales apiladas al 100 %

**Pregunta:** ¿pagan distinto hombres y mujeres? (puntos 4.b y 5.b)

Los dos géneros tienen distinto número de compras (3,372 y 3,128), de modo que
comparar cantidades absolutas induciría a error: el grupo más grande mostraría
barras más largas en todos los métodos sin que eso signifique preferencia. Al
normalizar cada género al 100 % de sus propias compras, ambos grupos se vuelven
directamente comparables.

Se eligieron barras **apiladas** y no agrupadas porque aquí las categorías sí son
excluyentes —cada venta tiene un único método de pago— y su suma tiene significado:
el 100 % de las compras del género. Es exactamente el caso contrario al de boletín y
vale, donde una misma venta puede registrar ambos y por eso allí se usaron barras
agrupadas.

La orientación horizontal permite leer las dos franjas una encima de la otra, que es
la comparación que interesa. El resultado es un gráfico visualmente monótono, y esa
monotonía es el mensaje: la mayor brecha entre ambos géneros es de 2.2 puntos
porcentuales. Un gráfico que muestra una no-diferencia debe verse como una
no-diferencia.

### 8. Edad frente a total de la venta — gráfico de dispersión

**Pregunta:** ¿existe relación entre la edad del cliente y lo que gasta? (punto 5.a)

Es el único gráfico del informe donde se representan las 6,500 observaciones
individuales sin agregar. La dispersión es la forma canónica para dos variables
continuas y la única que permite ver la **estructura** de la relación en lugar de su
resumen: un coeficiente de −0.0252 es un número que hay que creer, mientras que una
nube sin forma es una evidencia que se verifica de un vistazo.

Con 6,500 puntos en un rango de 62 edades el solapamiento es inevitable, así que se
aplicó transparencia (alfa 0.28) y se redujo el tamaño del marcador: la densidad de
la banda inferior pasa a codificar cuántas ventas se concentran en montos bajos, lo
que aporta información en vez de estorbar. Se añadió la recta de regresión —cuya
pendiente de −Q0.48 por año se traduce en una línea visualmente plana— y una línea
punteada con la venta promedio.

Se decidió **no recortar los valores atípicos** pese a que las ventas por encima de
Q1,500 estiran el eje y comprimen la nube principal. Eliminarlas habría producido un
gráfico más bonito y menos honesto: esas ventas existen, y su dispersión a lo largo
de todas las edades refuerza precisamente la conclusión de que la edad no predice el
gasto.

El recuadro con el coeficiente, el r² y la lectura («sin relación aprovechable») se
incluyó dentro del área del gráfico para que la imagen sea autosuficiente al
extraerla del informe.

### 9. Boletín y vale frente al ticket — mapa de calor

**Pregunta:** ¿cuál de los dos instrumentos comerciales mueve el gasto? (puntos 4.c y 5.c)

El cruce de dos variables binarias produce exactamente cuatro celdas, y la pregunta
no es cuánto vale cada una por separado sino **en qué dirección se produce la
separación**. Un mapa de calor codifica el ticket promedio en intensidad de color y
permite responder eso de inmediato: las dos celdas superiores son oscuras y las dos
inferiores claras, es decir, la variación ocurre entre filas —boletín— y no entre
columnas —vale—.

Se descartaron barras agrupadas para las cuatro combinaciones. Habrían mostrado los
mismos cuatro valores con mayor precisión de lectura, pero como una lista de cuatro
categorías sueltas; el hecho de que se trata de una matriz de 2×2 y de que una
dimensión domina sobre la otra se habría perdido. Es el caso en que la estructura
del dato importa más que la precisión de la comparación, y por eso se aceptó el
intercambio.

Para compensar la conocida imprecisión del color como canal cuantitativo, cada celda
lleva rotulado su ticket exacto y su número de compras, y se incluyó la barra de
color con escala en quetzales. El color del texto se calcula según la intensidad del
fondo para mantener el contraste legible en las cuatro celdas. Las líneas blancas de
separación se agregaron para que las celdas se lean como categorías discretas y no
como un gradiente continuo.

### 10. Distribución del total de la venta — histograma

**Pregunta:** ¿cómo se reparten las ventas a lo largo de la escala de montos?
(punto 2.b)

Las medidas de tendencia central del punto 2.b se reportaban únicamente como tabla, y
una tabla no permite ver la **forma** de una distribución. El histograma es la única
representación que muestra dónde se acumulan los casos, y aquí ese reparto es el
hallazgo: la media de Q206.24 supera a la mediana de Q137.35 en un 50 %, señal de una
asimetría hacia la derecha que ninguna de las tres medidas comunica por sí sola.

Se eligió una amplitud de clase de Q50 tras comparar alternativas. Intervalos más
anchos borraban el escalón entre la clase modal (Q50-100, con 1,442 ventas) y sus
vecinas; más estrechos fragmentaban la cola en barras de altura irrelevante y añadían
ruido sin información.

La decisión de diseño con más consecuencias fue **truncar el eje en Q800 y agrupar la
cola en una clase abierta**. El máximo observado es de Q3,169, de modo que un eje
completo dedicaría más de tres cuartas partes del ancho a barras casi invisibles y
comprimiría contra el margen izquierdo la zona donde se concentra el 97.5 % de los
casos. La clase agrupada se rotuló «800+», se dibujó con trama diagonal para que no se
confunda con una clase regular de Q50 y lleva anotado su conteo exacto de 161 ventas.
Es un recorte que se declara en el propio gráfico, no una omisión silenciosa.

El color codifica la posición respecto de la media: las clases que quedan por debajo
van en tono claro, las que quedan por encima en tono oscuro, y la clase que contiene
la media se marca en gris por ser la única ambigua. Así el 66.4 % de ventas que no
alcanza el promedio se lee como una superficie y no como un dato suelto. Media y
mediana se trazaron como líneas verticales rotuladas, y la distancia entre ambas se
anotó explícitamente, porque esa separación es justamente lo que el gráfico
demuestra.

### 11. Total de la venta por rango de edad — diagrama de caja

**Pregunta:** ¿la edad separa a los clientes por su gasto, más allá del promedio?
(puntos 4.a y 5.a)

La visualización 6 ya compara el ticket promedio entre rangos de edad, pero un
promedio admite una objeción razonable: puede ocultar distribuciones muy distintas.
Dos grupos con la misma media pueden tener dispersiones opuestas. El diagrama de caja
es la respuesta directa a esa objeción, porque muestra simultáneamente mediana,
cuartiles y recorrido de cada segmento.

Se escogió frente a un gráfico de violín o a histogramas superpuestos por una razón de
lectura: con cinco categorías, las cajas alineadas permiten comparar posición y
amplitud de un vistazo, mientras que cinco densidades superpuestas exigirían al lector
distinguir curvas que aquí serían casi idénticas. Y la coincidencia es precisamente el
mensaje.

Igual que en el histograma, el eje vertical se recortó —en Q700— porque los valores
atípicos llegan a Q3,169 y con el eje completo las cinco cajas quedarían aplastadas
contra la base, anulando la comparación que da sentido al gráfico. Por el mismo motivo
se omitieron los puntos atípicos individuales: el objeto de esta visualización es el
cuerpo central de cada distribución, no sus extremos, que ya quedan cubiertos por el
histograma anterior.

Cada caja lleva rotulados sus tres cuartiles y, bajo el eje, el tamaño de su muestra,
dato necesario para juzgar la estabilidad del tramo 56+ (346 clientes). Una línea
horizontal con la mediana general sirve de referencia común, y el recuadro superior
enuncia la conclusión que la imagen sostiene: las cinco distribuciones se solapan y
solo Q21.55 separan a la mediana más alta de la más baja.

### 12. Composición del 63.9 % presencial — gráfico de cascada

**Pregunta:** ¿de dónde sale la cifra de ventas que exigen presencia física?
(punto 3.c)

Este hallazgo no proviene de una columna sino de un cruce entre dos: canal de origen y
método de pago. Presentarlo como un total aislado obligaba al lector a aceptar el
63.9 % por confianza. La cascada existe justamente para eso: hace visible la
**aritmética** de un agregado, mostrando cómo cada componente se suma hasta el
subtotal.

Se descartó un gráfico circular, que habría mostrado las tres porciones pero no la
operación que las combina, y unas barras apiladas simples, que habrían dado la suma
sin distinguir el subtotal intermedio de sus sumandos. La cascada conserva ambas
cosas: las dos primeras barras flotan sobre la base acumulada, la tercera reinicia en
cero para señalar que es un subtotal, y la cuarta completa hasta el total del año.

El color separa las funciones en lugar de decorar: azul oscuro para el canal
presencial, rojo para el componente inferido —las 633 ventas en línea pagadas en
efectivo, que es el dato que exige un supuesto—, verde para el subtotal y azul claro
para el remanente puramente digital. Las líneas punteadas de conexión entre barras
marcan la continuidad del acumulado, y una línea de referencia con el total de 6,500
ventas cierra la escala.

Cada barra lleva su valor absoluto y su porcentaje, y el recuadro enuncia el resultado
en lenguaje llano. La visualización tiene además un valor de trazabilidad: al mostrar
la cifra descompuesta, deja a la vista que 633 de las 4,156 transacciones dependen de
una inferencia y no de un campo registrado, tal como se advierte en el punto 3.c.

## Decisiones de diseño transversales

Se aplicaron los mismos criterios a las doce visualizaciones para que el
informe se lea como un conjunto coherente:

- **Paleta constante.** Un azul institucional para la serie principal, verde para
  los valores destacados en positivo y rojo para los mínimos. El color se usa
  siempre para codificar significado, nunca como adorno.
- **Todo valor rotulado sobre el dato.** Sin excepción, cada barra y cada punto
  de las doce visualizaciones muestra su cifra exacta junto al elemento que la
  representa, y en las distribuciones se añade el porcentaje sobre el total. El
  criterio es que ninguna conclusión dependa de que el lector estime una altura
  o una longitud contra el eje: el gráfico debe entregar el dato, no insinuarlo.
- **Ejes siempre identificados.** Los doce gráficos rotulan ambos ejes con la
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

Se evaluaron y descartaron las alternativas siguientes:

- **Gráfico circular para el método de pago.** La comparación de ángulos es menos
  precisa que la de longitudes; se prefirieron barras.
- **Barras apiladas para boletín y vale.** Las dos categorías no son excluyentes,
  por lo que el total apilado carecería de interpretación.
- **Gráfico de violín para el gasto por rango de edad.** Habría mostrado la densidad
  completa de cada segmento, pero con cinco distribuciones casi idénticas obligaría a
  distinguir curvas superpuestas; el diagrama de caja comunica la misma coincidencia
  con una lectura más directa.
- **Barras apiladas simples para el 63.9 % presencial.** Entregan la suma pero no
  distinguen el subtotal intermedio de sus componentes, que es justamente lo que la
  cascada hace visible.

Un caso merece mención aparte porque la decisión cambió durante el proyecto. El
**histograma de montos de venta** se descartó en la primera ronda, con el argumento de
que las medidas de tendencia central ya cubrían el punto 2.b. Al redactar el informe
quedó claro que ese argumento era insuficiente: la media y la mediana señalan que
existe asimetría, pero no permiten ver su magnitud ni dónde se acumulan las ventas, y
sin esa imagen el lector no tiene forma de juzgar si el ticket promedio describe bien
al negocio. El histograma se incorporó entonces como visualización 10 y es hoy el
único gráfico que muestra la forma de la variable principal del conjunto de datos.
