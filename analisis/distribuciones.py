"""Distribuciones y composición del canal (puntos 2.b, 4.a, 5.a y 3.c).

Imprime en consola las cifras que sostienen cada gráfica y guarda en
`graficas/` las tres visualizaciones que cierran el mínimo de siete del punto 6.
Los tres tipos de gráfico son nuevos respecto de las nueve ya existentes:
histograma, diagrama de caja y gráfico de cascada.

Reutiliza `mcp_server/database.py` igual que `analisis/exploratorio.py` y
`analisis/segmentacion.py`, de modo que el informe, el MCPServer y el agente
conversacional devuelven las mismas cifras por construcción.

Uso:
    python analisis/distribuciones.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from psycopg2 import sql

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from mcp_server.database import fetch_all, fetch_one, qualified_table


ANIO = 2021
GRAFICAS_DIR = PROJECT_ROOT / "graficas"

# Misma paleta que `analisis/exploratorio.py` y `analisis/segmentacion.py`: las
# doce gráficas del informe deben leerse como un único conjunto.
COLOR_PRINCIPAL = "#1f4e79"
COLOR_SECUNDARIO = "#c0504d"
COLOR_ACENTO = "#4f81bd"
COLOR_APOYO = "#9bbb59"
COLOR_NEUTRO = "#8c8c8c"

TOTAL_TRANSACCIONES = 6500
FUENTE = (
    "Fuente: elaboración propia con base en los datos de ventas online 2021 "
    f"cargados en PostgreSQL (N = {TOTAL_TRANSACCIONES:,} transacciones)."
)

# Corte del eje del histograma. El percentil 99 está en Q1,048.91 y el máximo en
# Q3,169: sin corte, el 2.5 % de la cola estira el eje cuatro veces y aplasta la
# distribución que el gráfico debe mostrar.
ANCHO_CLASE = 50
TOPE_HISTOGRAMA = 800

# Corte del eje del diagrama de caja, por la misma razón.
TOPE_CAJA = 700

RANGOS_EDAD = ("18-25", "26-35", "36-45", "46-55", "56+")


# ---------------------------------------------------------------------------
# Utilidades de presentación
# ---------------------------------------------------------------------------


def _encabezado(titulo: str) -> None:
    print()
    print("=" * 78)
    print(titulo)
    print("=" * 78)


def _moneda(valor: float) -> str:
    return f"Q{valor:,.2f}"


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------


def _rango_edad_sql() -> sql.SQL:
    """Misma clasificación por edad que `queries.get_age_segments`."""
    return sql.SQL(
        """
        CASE
            WHEN c.edad < 18 THEN '<18'
            WHEN c.edad BETWEEN 18 AND 25 THEN '18-25'
            WHEN c.edad BETWEEN 26 AND 35 THEN '26-35'
            WHEN c.edad BETWEEN 36 AND 45 THEN '36-45'
            WHEN c.edad BETWEEN 46 AND 55 THEN '46-55'
            ELSE '56+'
        END
        """
    )


def resumen_venta_total() -> dict[str, Any]:
    """2.b — Posición y dispersión de `venta_total`.

    La media, la mediana y la moda ya se reportan en el análisis exploratorio;
    aquí se añaden los cuartiles y los percentiles altos, que son los que
    explican por qué la media y la mediana se separan tanto.
    """
    consulta = sql.SQL(
        """
        SELECT
            MIN(venta_total)::double precision AS minimo,
            percentile_cont(0.25) WITHIN GROUP (ORDER BY venta_total)
                ::double precision AS q1,
            percentile_cont(0.50) WITHIN GROUP (ORDER BY venta_total)
                ::double precision AS mediana,
            AVG(venta_total)::double precision AS media,
            percentile_cont(0.75) WITHIN GROUP (ORDER BY venta_total)
                ::double precision AS q3,
            percentile_cont(0.90) WITHIN GROUP (ORDER BY venta_total)
                ::double precision AS p90,
            percentile_cont(0.99) WITHIN GROUP (ORDER BY venta_total)
                ::double precision AS p99,
            MAX(venta_total)::double precision AS maximo,
            COUNT(*)::int AS ventas
        FROM {}
        """
    ).format(qualified_table("venta"))
    resumen = fetch_one(consulta)

    bajo_media = fetch_one(
        sql.SQL(
            """
            SELECT COUNT(*)::int AS ventas
            FROM {} v
            WHERE v.venta_total < (SELECT AVG(venta_total) FROM {})
            """
        ).format(qualified_table("venta"), qualified_table("venta"))
    )["ventas"]

    resumen["bajo_media"] = bajo_media
    resumen["bajo_media_porcentaje"] = bajo_media / resumen["ventas"] * 100
    resumen["exceso_media_porcentaje"] = (
        resumen["media"] / resumen["mediana"] - 1
    ) * 100

    _encabezado("2.b  DISTRIBUCIÓN DEL TOTAL DE LA VENTA")
    print(f"{'Estadístico':<28}{'Valor':>16}")
    print("-" * 78)
    for etiqueta, clave in (
        ("Mínimo", "minimo"),
        ("Primer cuartil (Q1)", "q1"),
        ("Mediana", "mediana"),
        ("Media", "media"),
        ("Tercer cuartil (Q3)", "q3"),
        ("Percentil 90", "p90"),
        ("Percentil 99", "p99"),
        ("Máximo", "maximo"),
    ):
        print(f"{etiqueta:<28}{_moneda(resumen[clave]):>16}")
    print("-" * 78)
    print(
        f"La media supera a la mediana en {resumen['exceso_media_porcentaje']:.1f}%; "
        f"{resumen['bajo_media']:,} ventas "
        f"({resumen['bajo_media_porcentaje']:.1f}%) quedan por debajo de la media."
    )
    return resumen


def ventas_totales() -> list[float]:
    """Serie sin agregar de `venta_total`, que alimenta el histograma."""
    consulta = sql.SQL(
        "SELECT venta_total::double precision AS venta_total FROM {}"
    ).format(qualified_table("venta"))
    return [fila["venta_total"] for fila in fetch_all(consulta)]


def ventas_por_rango_edad() -> dict[str, list[float]]:
    """4.a / 5.a — Serie sin agregar de `venta_total` por rango de edad."""
    consulta = sql.SQL(
        """
        SELECT {} AS rango_edad,
               v.venta_total::double precision AS venta_total
        FROM {} c
        JOIN {} v ON v.id_cliente = c.id_cliente
        """
    ).format(
        _rango_edad_sql(), qualified_table("cliente"), qualified_table("venta")
    )
    series: dict[str, list[float]] = {rango: [] for rango in RANGOS_EDAD}
    for fila in fetch_all(consulta):
        series.setdefault(fila["rango_edad"], []).append(fila["venta_total"])
    return {rango: series[rango] for rango in RANGOS_EDAD if series.get(rango)}


def cuartiles_por_rango_edad() -> list[dict[str, Any]]:
    """4.a — Cuartiles del ticket por rango de edad."""
    consulta = sql.SQL(
        """
        SELECT
            {} AS rango_edad,
            COUNT(*)::int AS ventas,
            percentile_cont(0.25) WITHIN GROUP (ORDER BY v.venta_total)
                ::double precision AS q1,
            percentile_cont(0.50) WITHIN GROUP (ORDER BY v.venta_total)
                ::double precision AS mediana,
            percentile_cont(0.75) WITHIN GROUP (ORDER BY v.venta_total)
                ::double precision AS q3,
            AVG(v.venta_total)::double precision AS media
        FROM {} c
        JOIN {} v ON v.id_cliente = c.id_cliente
        GROUP BY 1
        ORDER BY 1
        """
    ).format(
        _rango_edad_sql(), qualified_table("cliente"), qualified_table("venta")
    )
    filas = fetch_all(consulta)

    _encabezado("4.a / 5.a  CUARTILES DEL TICKET POR RANGO DE EDAD")
    print(
        f"{'Rango':<10}{'Ventas':>10}{'Q1':>14}{'Mediana':>14}"
        f"{'Q3':>14}{'Media':>14}"
    )
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['rango_edad']:<10}"
            f"{fila['ventas']:>10,}"
            f"{_moneda(fila['q1']):>14}"
            f"{_moneda(fila['mediana']):>14}"
            f"{_moneda(fila['q3']):>14}"
            f"{_moneda(fila['media']):>14}"
        )
    print("-" * 78)
    medianas = [fila["mediana"] for fila in filas]
    print(
        "Las cinco medianas se mueven entre "
        f"{_moneda(min(medianas))} y {_moneda(max(medianas))}: "
        f"{_moneda(max(medianas) - min(medianas))} de diferencia entre el rango "
        "que más gasta y el que menos."
    )
    return filas


def composicion_presencial() -> dict[str, Any]:
    """3.c — Ventas que exigen presencia física frente a las digitales puras.

    Se aplica el criterio del auxiliar: `MetodoPago = 0` cuenta como efectivo y
    como contra entrega; las tarjetas de crédito y débito no. Una venta en
    efectivo originada en un navegador no puede cobrarse en el mostrador, de
    modo que se liquida en la puerta del cliente: es reparto con cobro en mano.
    La partición es una inferencia razonada, no un campo de la base.
    """
    consulta = sql.SQL(
        """
        SELECT
            COUNT(*) FILTER (WHERE v.id_navegador = 0)::int AS tienda_fisica,
            COUNT(*) FILTER (
                WHERE v.id_navegador <> 0 AND v.id_metodo_pago = 0
            )::int AS contra_entrega,
            COUNT(*) FILTER (
                WHERE v.id_navegador <> 0 AND v.id_metodo_pago <> 0
            )::int AS digital_puro,
            COUNT(*)::int AS total
        FROM {} v
        """
    ).format(qualified_table("venta"))
    datos = fetch_one(consulta)
    datos["presencial"] = datos["tienda_fisica"] + datos["contra_entrega"]
    datos["en_linea"] = datos["contra_entrega"] + datos["digital_puro"]

    _encabezado("3.c  COMPOSICIÓN DE LAS VENTAS SEGÚN EXIJAN PRESENCIA FÍSICA")
    print(f"{'Componente':<48}{'Ventas':>12}{'% total':>12}")
    print("-" * 78)
    for etiqueta, clave in (
        ("Tienda física", "tienda_fisica"),
        ("En línea con pago en efectivo (contra entrega)", "contra_entrega"),
        ("Subtotal: requieren presencia física", "presencial"),
        ("En línea con pago con tarjeta", "digital_puro"),
        ("Total", "total"),
    ):
        porcentaje = datos[clave] / datos["total"] * 100
        print(f"{etiqueta:<48}{datos[clave]:>12,}{porcentaje:>11.1f}%")
    print("-" * 78)
    print(
        f"{datos['contra_entrega']:,} de las {datos['en_linea']:,} ventas en línea "
        f"({datos['contra_entrega'] / datos['en_linea'] * 100:.1f}%) se pagaron en "
        "efectivo al momento de la entrega."
    )
    return datos


# ---------------------------------------------------------------------------
# 6. Visualización de datos
# ---------------------------------------------------------------------------


def _guardar(fig: plt.Figure, nombre: str) -> None:
    GRAFICAS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = GRAFICAS_DIR / nombre
    # Recoloca los rótulos de los ejes dentro del lienzo antes de escribir el
    # pie de fuente; de lo contrario las etiquetas de dos y tres renglones
    # desbordan por abajo y se encabalgan con él.
    fig.tight_layout()
    fig.text(0.01, -0.02, FUENTE, fontsize=8, color="#555555", ha="left")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  guardada: {ruta.relative_to(PROJECT_ROOT)}")


def _limpiar_ejes(ax: plt.Axes, rejilla_y: bool = True) -> None:
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    if rejilla_y:
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.set_axisbelow(True)


def grafica_distribucion_venta(valores: list[float], resumen: dict[str, Any]) -> None:
    """Histograma: cómo se reparten las 6,500 ventas por su importe.

    El punto 2.b se resuelve hoy con una tabla de media, mediana y moda, sin
    ninguna gráfica. El histograma es el único tipo que muestra la forma de la
    distribución, y esa forma es la que explica la tabla: la asimetría a la
    derecha es la razón de que la media supere a la mediana en un 50 %.
    """
    n_clases = TOPE_HISTOGRAMA // ANCHO_CLASE
    conteos = [0] * (n_clases + 1)
    for valor in valores:
        indice = n_clases if valor >= TOPE_HISTOGRAMA else int(valor // ANCHO_CLASE)
        conteos[indice] += 1

    media = resumen["media"]
    mediana = resumen["mediana"]
    clase_media = int(media // ANCHO_CLASE)

    fig, ax = plt.subplots(figsize=(12.5, 6.5))

    posiciones = list(range(n_clases + 1))
    for indice, conteo in enumerate(conteos):
        if indice == n_clases:
            # La barra agregada de la cola no es una clase más: representa un
            # intervalo abierto y dieciséis veces más ancho que las demás. El
            # sombreado impide leerla como si fuera comparable con sus vecinas.
            color, trama = COLOR_PRINCIPAL, "//"
        elif indice < clase_media:
            color, trama = COLOR_ACENTO, None
        elif indice == clase_media:
            color, trama = COLOR_NEUTRO, None
        else:
            color, trama = COLOR_PRINCIPAL, None
        ax.bar(
            indice,
            conteo,
            width=0.92,
            color=color,
            hatch=trama,
            edgecolor="white",
            linewidth=0.6,
        )
        ax.text(
            indice,
            conteo + max(conteos) * 0.015,
            f"{conteo:,}",
            ha="center",
            va="bottom",
            fontsize=8,
            # El recuadro blanco no se ve sobre el fondo, pero interrumpe las
            # líneas de referencia que pasan por detrás de la cifra.
            bbox={
                "boxstyle": "square,pad=0.12",
                "facecolor": "white",
                "edgecolor": "none",
            },
        )

    # Las líneas de referencia se sitúan en coordenadas de clase para que caigan
    # sobre la barra que realmente las contiene.
    x_mediana = mediana / ANCHO_CLASE - 0.5
    x_media = media / ANCHO_CLASE - 0.5
    ax.axvline(
        x_mediana,
        color=COLOR_APOYO,
        linestyle="--",
        linewidth=2,
        label=f"Mediana {_moneda(mediana)} — la venta típica",
    )
    ax.axvline(
        x_media,
        color=COLOR_SECUNDARIO,
        linestyle="--",
        linewidth=2,
        label=(
            f"Media {_moneda(media)} — "
            f"{resumen['bajo_media_porcentaje']:.1f}% de las ventas no la alcanza"
        ),
    )

    # La distancia entre ambas líneas es el mensaje del gráfico, así que se
    # dibuja como una medida acotada y no se deja a la vista del lector.
    y_flecha = max(conteos) * 0.80
    ax.annotate(
        "",
        xy=(x_mediana, y_flecha),
        xytext=(x_media, y_flecha),
        arrowprops={"arrowstyle": "<->", "color": "#444444", "linewidth": 1.4},
    )
    # El rótulo va a la derecha de la línea de la media, no centrado sobre la
    # medida: el hueco entre ambas líneas es más angosto que el propio texto.
    ax.text(
        x_media + 0.18,
        y_flecha,
        f"La media queda {_moneda(media - mediana)} por encima\n"
        f"de la mediana: un {resumen['exceso_media_porcentaje']:.0f}% más",
        ha="left",
        va="center",
        fontsize=9.5,
        color="#444444",
    )

    etiquetas = [
        f"{indice * ANCHO_CLASE}–{(indice + 1) * ANCHO_CLASE}"
        for indice in range(n_clases)
    ] + [f"{TOPE_HISTOGRAMA}+"]
    ax.set_xticks(posiciones)
    ax.set_xticklabels(etiquetas, rotation=45, ha="right", fontsize=8.5)

    ax.set_title(
        "Distribución del total de la venta: dos tercios de las ventas no llegan al promedio",
        fontsize=13,
        pad=14,
    )
    ax.set_xlabel("Total de la venta (quetzales)")
    ax.set_ylabel("Cantidad de ventas")
    ax.set_ylim(0, max(conteos) * 1.12)

    # El color de las barras codifica el mismo hecho que la línea de la media,
    # así que la leyenda debe declararlo en lugar de dejarlo a la deducción.
    sobre_media = resumen["ventas"] - resumen["bajo_media"]
    manijas, etiquetas_leyenda = ax.get_legend_handles_labels()
    manijas += [
        Patch(facecolor=COLOR_ACENTO),
        Patch(facecolor=COLOR_NEUTRO),
        Patch(facecolor=COLOR_PRINCIPAL),
    ]
    etiquetas_leyenda += [
        f"Clases por debajo de la media ({resumen['bajo_media']:,} ventas)",
        "Clase que contiene la media",
        f"Clases por encima de la media ({sobre_media:,} ventas)",
    ]
    ax.legend(
        manijas,
        etiquetas_leyenda,
        frameon=False,
        loc="upper right",
        fontsize=9.5,
    )
    _limpiar_ejes(ax)
    # El ancho de clase, el porqué de la clase gris y el corte del eje quedan
    # documentados en `docs/03-metodologia.md`, no sobre la imagen.
    _guardar(fig, "10-distribucion-venta.png")


def grafica_caja_edad(
    series: dict[str, list[float]],
    cuartiles: list[dict[str, Any]],
    resumen: dict[str, Any],
) -> None:
    """Diagrama de caja: distribución del ticket por rango de edad.

    Las barras de la gráfica 06 comparan promedios, y a un promedio siempre se
    le puede objetar que esconde diferencias internas. El diagrama de caja
    responde a esa objeción por adelantado: muestra la distribución completa de
    cada rango, no un solo número, y las cinco se solapan casi por entero.
    """
    rangos = list(series.keys())
    datos = [series[rango] for rango in rangos]
    por_rango = {fila["rango_edad"]: fila for fila in cuartiles}

    fig, ax = plt.subplots(figsize=(11, 6.5))

    caja = ax.boxplot(
        datos,
        showfliers=False,
        widths=0.55,
        patch_artist=True,
        medianprops={"color": COLOR_SECUNDARIO, "linewidth": 2.2},
        whiskerprops={"color": COLOR_PRINCIPAL, "linewidth": 1.2},
        capprops={"color": COLOR_PRINCIPAL, "linewidth": 1.2},
        boxprops={"edgecolor": COLOR_PRINCIPAL, "linewidth": 1.2},
    )
    for cuerpo in caja["boxes"]:
        cuerpo.set_facecolor(COLOR_ACENTO)
        cuerpo.set_alpha(0.55)

    ax.axhline(
        resumen["mediana"],
        color=COLOR_APOYO,
        linestyle="--",
        linewidth=1.6,
        zorder=0,
        label=f"Mediana general {_moneda(resumen['mediana'])}",
    )

    for posicion, rango in enumerate(rangos, start=1):
        fila = por_rango[rango]
        # Los tres cuartiles rotulados a la derecha de cada caja: la lectura no
        # debe depender de estimar alturas contra el eje.
        for clave, alineacion in (("q3", "bottom"), ("mediana", "center"), ("q1", "top")):
            ax.text(
                posicion + 0.31,
                fila[clave],
                _moneda(fila[clave]),
                ha="left",
                va=alineacion,
                fontsize=8.5,
                color="#444444",
                # Interrumpe la línea de la mediana general, que cruza el
                # lienzo justo a la altura de las medianas por rango.
                bbox={
                    "boxstyle": "square,pad=0.12",
                    "facecolor": "white",
                    "edgecolor": "none",
                },
            )
        ax.text(
            posicion,
            -TOPE_CAJA * 0.075,
            f"n = {fila['ventas']:,}",
            ha="center",
            va="center",
            fontsize=9,
            color="#444444",
        )

    medianas = [por_rango[rango]["mediana"] for rango in rangos]
    ax.annotate(
        "Las cinco distribuciones se solapan:\n"
        f"{_moneda(max(medianas) - min(medianas))} separan a la mediana más alta "
        "de la más baja.\nLa edad no divide a los clientes por su gasto.",
        xy=(0.985, 0.96),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=10,
        bbox={
            "boxstyle": "round,pad=0.5",
            "facecolor": "#f2f2f2",
            "edgecolor": "#cccccc",
        },
    )

    ax.set_title(
        "Distribución del total de la venta por rango de edad del cliente",
        fontsize=13,
        pad=14,
    )
    ax.set_xlabel("Rango de edad del cliente (años)")
    ax.set_ylabel("Total de la venta (quetzales)")
    ax.set_xticks(range(1, len(rangos) + 1))
    ax.set_xticklabels(rangos)
    ax.set_ylim(-TOPE_CAJA * 0.12, TOPE_CAJA)
    ax.spines["left"].set_bounds(0, TOPE_CAJA)
    ax.set_yticks(range(0, TOPE_CAJA + 1, 100))
    ax.yaxis.set_major_formatter(lambda valor, _: f"Q{valor:,.0f}")
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    _limpiar_ejes(ax)
    # El recorte del eje en Q700, la omisión de los atípicos y el alcance de los
    # bigotes quedan documentados en `docs/03-metodologia.md`.
    _guardar(fig, "11-caja-edad.png")


def grafica_cascada_presencial(datos: dict[str, Any]) -> None:
    """Cascada: cómo se llega al 63.9 % de ventas que exigen presencia física.

    El hallazgo es el resultado de sumar dos grupos que viven en columnas
    distintas de la base, y ninguna gráfica del informe mostraba esa suma. La
    cascada es el único tipo que representa a la vez los sumandos, el subtotal
    y el resto, encadenados de modo que se vea de dónde sale la cifra.
    """
    total = datos["total"]
    presencial = datos["presencial"]

    # (etiqueta, base, altura, color)
    barras = [
        ("Tienda física", 0, datos["tienda_fisica"], COLOR_PRINCIPAL),
        (
            "En línea,\npago en efectivo\n(contra entrega)",
            datos["tienda_fisica"],
            datos["contra_entrega"],
            COLOR_SECUNDARIO,
        ),
        ("Requieren\npresencia física", 0, presencial, COLOR_APOYO),
        (
            "En línea,\npago con tarjeta",
            presencial,
            datos["digital_puro"],
            COLOR_ACENTO,
        ),
    ]

    fig, ax = plt.subplots(figsize=(11, 6.5))

    for posicion, (etiqueta, base, altura, color) in enumerate(barras):
        ax.bar(
            posicion,
            altura,
            bottom=base,
            width=0.62,
            color=color,
            edgecolor="white",
            linewidth=0.8,
        )
        ax.text(
            posicion,
            base + altura / 2,
            f"{altura:,}\n{altura / total * 100:.1f}%",
            ha="center",
            va="center",
            fontsize=11,
            color="white",
            fontweight="bold",
        )

    # Conectores entre el techo de cada barra y el arranque de la siguiente:
    # son los que convierten cuatro barras sueltas en una cascada.
    for posicion in range(len(barras) - 1):
        _, base, altura, _ = barras[posicion]
        ax.plot(
            [posicion + 0.31, posicion + 1 - 0.31],
            [base + altura, base + altura],
            color="#999999",
            linestyle=":",
            linewidth=1.2,
            zorder=0,
        )

    ax.axhline(
        total,
        color="#444444",
        linestyle="--",
        linewidth=1.3,
        zorder=0,
    )
    ax.text(
        len(barras) - 0.55,
        total + total * 0.018,
        f"Total {ANIO}: {total:,} ventas",
        ha="right",
        va="bottom",
        fontsize=9.5,
        color="#444444",
    )

    ax.annotate(
        f"{presencial:,} de {total:,} ventas ({presencial / total * 100:.1f}%)\n"
        "necesitan que una persona entregue el producto\n"
        "o reciba el dinero en mano.",
        # A la izquierda y por debajo de la línea del total: es el único hueco
        # que no cruza ni las barras ni el techo de las 6,500 ventas.
        xy=(0.015, 0.84),
        xycoords="axes fraction",
        ha="left",
        va="top",
        fontsize=10,
        bbox={
            "boxstyle": "round,pad=0.5",
            "facecolor": "#f2f2f2",
            "edgecolor": "#cccccc",
        },
    )

    ax.set_title(
        "De dónde sale el 63.9 % de ventas que exigen presencia física",
        fontsize=13,
        pad=14,
    )
    ax.set_xlabel("Componente de la venta")
    ax.set_ylabel("Cantidad de ventas")
    ax.set_xticks(range(len(barras)))
    ax.set_xticklabels([barra[0] for barra in barras], fontsize=9.5)
    ax.set_ylim(0, total * 1.12)
    ax.yaxis.set_major_formatter(lambda valor, _: f"{valor:,.0f}")
    _limpiar_ejes(ax)
    # El criterio del auxiliar sobre el pago contra entrega y el carácter
    # inferido de la partición quedan documentados en `docs/03-metodologia.md`.
    _guardar(fig, "12-cascada-presencial.png")


# ---------------------------------------------------------------------------


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Distribuciones y composición del canal · ventas {ANIO}")

    resumen = resumen_venta_total()
    cuartiles = cuartiles_por_rango_edad()
    composicion = composicion_presencial()

    _encabezado("6.  GENERACIÓN DE GRÁFICAS")
    grafica_distribucion_venta(ventas_totales(), resumen)
    grafica_caja_edad(ventas_por_rango_edad(), cuartiles, resumen)
    grafica_cascada_presencial(composicion)


if __name__ == "__main__":
    main()
