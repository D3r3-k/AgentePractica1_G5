[ ← Regresar ](../README.md)

# respuestas

## Pregunta 8.c: ¿Cómo podría este análisis de datos ayudar a la empresa a ahorrar costos o mejorar la eficiencia operativa?

El análisis nos permite ahorrar dinero por dos lados distintos, y vale la pena verlos por separado porque impactan diferentes presupuestos:

1. Cortar de raíz los gastos de marketing que no sirven.
A veces el mayor ahorro viene de dejar de hacer lo que no funciona. Con una correlación de -0.019 entre edad y compra, y un 0.024 entre género y forma de pago, queda claro que meterle presupuesto a segmentar campañas por edad o género es tirar el dinero a la basura. Igualmente, regalar vales a clientes no suscritos nos hace perder un 7.8% en el ticket promedio; o sea, le estamos pagando al cliente para que nos compre menos. Frenar esto es un ahorro inmediato y no nos cuesta ni un centavo.

2. Ajustar la parte técnica y operativa a la realidad.
No tiene sentido tratar a todos los canales por igual. El Navegador 4 solo representa 197 ventas (el 3% del total), mientras que el Navegador 1 se lleva el 42.8% de todo el volumen digital. Gastar el mismo tiempo y dinero en mantenimiento o pruebas de compatibilidad para un navegador que casi nadie usa es un desperdicio. Si concentramos el trabajo del equipo de sistemas en el canal principal y reducimos la atención al marginal, liberamos recursos sin que el usuario note la diferencia. 

## Pregunta 8.d: ¿Qué datos adicionales recomendarían para obtener insights aún más valiosos en el futuro?

Trabajar con estas doce columnas dejó claro dónde están los techos del análisis. Cada límite que encontramos apunta a un dato que no se está capturando, y esta es la lista ordenada por lo que más cambiaría las decisiones si existiera.

**1. Qué se vendió.** Es la ausencia más grande y la más incómoda. El dataset dice cuánto se pagó, cuándo y por dónde, pero no dice qué compró la gente. Sin producto ni categoría no se puede calcular rotación, ni armar recomendaciones, ni saber si diciembre vende más por volumen o porque se venden cosas más caras. Un identificador de producto y su categoría convertirían este análisis en uno de surtido, que es donde de verdad se toman las decisiones de compra e inventario.

**2. Costo y margen por transacción.** Todo el análisis está construido sobre ingresos, y eso obliga a asumir que vender más siempre es mejor. No lo es. Sin costo no hay forma de saber si el descuento del vale se paga solo, si la tienda física es más rentable que el reparto o si el canal que más factura es también el que menos deja. Es el dato que separa un reporte de ventas de uno de rentabilidad.

**3. Estado final del pedido.** Detectamos 633 ventas en línea pagadas en efectivo, que se cobran cuando el producto llega a la puerta. No sabemos cuántas de esas efectivamente llegaron. Un campo de estado —entregado, rechazado, reagendado, devuelto— revelaría si esa modalidad es un canal sano o una fuga silenciosa. Hoy estamos midiendo ventas que quizá nunca se concretaron.

**4. Marca de tiempo completa y documentación de la columna Tiempo.** Solo tenemos la fecha, sin hora. Saber a qué hora compra la gente permitiría dimensionar turnos en la tienda y programar los envíos del boletín cuando alguien los va a abrir. A esto se suma un problema de metadatos: la columna `Tiempo` trae valores alrededor de 767 sin ninguna unidad declarada. Pueden ser segundos de sesión, minutos hasta la entrega o cualquier otra cosa, y como no está documentada tuvimos que dejarla fuera del análisis. Un diccionario de datos habría recuperado una variable completa.

**5. Origen del tráfico y campañas activas.** Noviembre es el mes más flojo del año, con 493 ventas, y no tenemos manera de saber por qué. Registrar de dónde llegó cada visita y qué campaña estaba corriendo en cada fecha convertiría hallazgos descriptivos en explicaciones. Ahora mismo podemos decir qué pasó, pero no por qué, y esa distinción es la que separa un análisis que informa de uno que sirve para actuar.

**6. Dispositivo y sucursal.** Los canales están etiquetados como «Navegador 1» a «Navegador 4» sin decir cuáles son ni si la diferencia es de navegador, de dispositivo o de aplicación. Saber si el Navegador 4 tiene 197 ventas porque casi nadie lo usa o porque algo se rompe en su proceso de pago son dos diagnósticos opuestos con soluciones opuestas. Del lado físico pasa igual: si la empresa abre más sucursales, sin un identificador de tienda todas las ventas presenciales seguirán apareciendo como un solo bloque indistinguible.

**7. Fecha de suscripción al boletín.** Los suscriptores gastan más, pero con los datos actuales no se puede saber si empezaron a gastar más después de suscribirse o si ya gastaban más desde antes. Guardar la fecha en que cada cliente se suscribió permitiría comparar su comportamiento previo y posterior, y resolver con datos ya existentes una pregunta que hoy exige montar un experimento.

Vale la pena señalar que los primeros tres puntos no requieren tecnología nueva: son campos que el sistema transaccional casi con seguridad ya maneja y que simplemente no se están arrastrando hasta el conjunto de datos analítico. El costo de agregarlos es bajo comparado con lo que se gana.

## Pregunta 8.e: ¿Implementar un chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?

Sí, y de forma sustancial, pero el efecto no es el que suele venderse. No se trata de que la inteligencia artificial descubra hallazgos que el equipo no vio, sino de que elimina la espera entre una pregunta de negocio y su respuesta numérica. Vale la pena separar lo que este proyecto demuestra que el agente sí hace de lo que no puede hacer, porque de esa distinción depende que la inversión valga la pena.

**Lo que cambia de verdad: la velocidad y quién puede preguntar.**
Hoy, cuando alguien de comercial quiere saber cuánto vendió noviembre o qué tramo etario deja más margen, la pregunta entra a una cola: alguien la traduce a SQL, la ejecuta, la formatea y la devuelve. Ese ciclo se mide en horas o días, y su costo real no es el tiempo del analista sino las preguntas que nunca se hacen porque no valen el trámite. Con el agente implementado, las dieciséis preguntas del alcance de esta práctica se responden en lenguaje natural y en segundos, sin que quien pregunta sepa SQL. El analista deja de ser el intermediario de consultas rutinarias y queda libre para el trabajo que sí requiere criterio.

**Por qué esta implementación es confiable y un chatbot genérico no lo sería.**
Aquí está la decisión de arquitectura que más importa. El agente no recibe la base de datos ni el archivo CSV para que los interprete: recibe doce herramientas del MCPServer, cada una respaldada por una consulta SQL fija y revisada. Cuando alguien pregunta por la correlación entre edad y venta, el modelo no calcula nada; invoca `obtener_correlacion_venta_edad`, y el `corr()` de PostgreSQL devuelve −0.0252. El papel del modelo se limita a entender la pregunta, elegir la herramienta y redactar la respuesta.

La diferencia es enorme en términos de riesgo. Un modelo al que se le pega un CSV en el chat puede equivocarse al sumar y presentar el error con total seguridad. Aquí eso no puede ocurrir, porque los números no los produce el modelo. Además la conexión es de solo lectura y las credenciales viven en variables de entorno, de modo que el agente no puede alterar ni exponer la base. Es la diferencia entre una herramienta de consulta y un generador de texto plausible.

**Los tres límites que la empresa debe asumir antes de decidir.**

*Primero, el agente solo sabe lo que sus herramientas exponen.* Responde las doce consultas registradas y nada más. El hallazgo más valioso de nuestro bloque —que el vale resta 6.9% de ticket a los no suscritos y suma 3.8% a los suscritos, una vez controlado el efecto del boletín— no salió de ninguna de las doce herramientas: exigió sospechar de un promedio agregado, reconocer una paradoja de Simpson y escribir una consulta nueva. El agente entrega respuestas; no formula las preguntas correctas.

*Segundo, entregar el dato no es entregar el análisis.* El agente puede devolver r = −0.0252 con toda exactitud y aun así quien lo lea puede concluir «hay relación negativa, enfoquémonos en clientes jóvenes». El número correcto y la decisión equivocada conviven sin problema. Un dato como ese necesita ir acompañado de que explica el 0.064% de la variación y de que significativo no equivale a importante, y ese acompañamiento es criterio profesional, no recuperación de información.

*Tercero, un dato inmediato invita a decidir rápido.* La fricción de la cola de consultas cumplía involuntariamente una función de filtro. Al desaparecer, conviene que las decisiones de peso sigan pasando por revisión humana, sobre todo cuando el conjunto de datos tiene los vacíos documentados en la pregunta 8.d: sin producto, sin costo y sin estado del pedido, hay preguntas que el agente contestará con seguridad aparente sin que la respuesta signifique lo que el usuario cree.

**Recomendación.** Implementarlo, con un alcance definido: como capa de autoservicio para consulta operativa y seguimiento de indicadores, no como sustituto del análisis. El costo es marginal —un modelo Flash-Lite gratuito dentro de sus límites de uso y un servidor que ya está escrito— y el retorno es directo en tiempo liberado. La condición es que el equipo mantenga las herramientas al día conforme el negocio incorpore nuevas preguntas, porque un agente conectado a doce consultas que envejecen se vuelve, con el tiempo, una fuente autorizada de respuestas incompletas.
