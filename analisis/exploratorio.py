"""Análisis exploratorio y de tendencias de las ventas 2021 (puntos 2 y 3).

Imprime en consola las estadísticas solicitadas y guarda en `graficas/` las
cinco visualizaciones que aporta este bloque al mínimo de siete del punto 6.

Uso:
    python analisis/exploratorio.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from psycopg2 import sql

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from mcp_server import queries
from mcp_server.database import fetch_all, qualified_table


ANIO = 2021
GRAFICAS_DIR = PROJECT_ROOT / "graficas"

COLOR_PRINCIPAL = "#1f4e79"
COLOR_SECUNDARIO = "#c0504d"
COLOR_ACENTO = "#4f81bd"
COLOR_APOYO = "#9bbb59"

TOTAL_TRANSACCIONES = 6500
FUENTE = (
    "Fuente: elaboración propia con base en los datos de ventas online 2021 "
    f"cargados en PostgreSQL (N = {TOTAL_TRANSACCIONES:,} transacciones)."
)


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
# 2. Análisis exploratorio
# ---------------------------------------------------------------------------


def estadisticas_basicas() -> list[dict[str, Any]]:
    """2.b — Media, mediana y moda de las variables numéricas."""
    filas = queries.get_basic_statistics()

    _encabezado("2.b  ESTADÍSTICAS BÁSICAS DE LAS VARIABLES NUMÉRICAS")
    print(f"{'Variable':<16}{'Media':>16}{'Mediana':>16}{'Moda':>16}")
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['variable']:<16}"
            f"{fila['media']:>16,.2f}"
            f"{fila['mediana']:>16,.2f}"
            f"{fila['moda']:>16,.2f}"
        )
    return filas


def ventas_por_mes() -> list[dict[str, Any]]:
    """2.c / 3.a — Distribución de las ventas a lo largo del año."""
    filas = queries.get_monthly_sales(ANIO)

    _encabezado(f"2.c  DISTRIBUCIÓN DE VENTAS POR MES ({ANIO})")
    print(f"{'Mes':<14}{'Ventas':>10}{'Total':>18}{'Promedio':>16}")
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['mes_nombre'].capitalize():<14}"
            f"{fila['cantidad_ventas']:>10,}"
            f"{_moneda(fila['total_ventas']):>18}"
            f"{_moneda(fila['promedio_venta']):>16}"
        )
    return filas


def distribucion_metodo_pago() -> list[dict[str, Any]]:
    """2.c — Distribución de las ventas por método de pago."""
    filas = queries.get_payment_distribution()
    total = sum(fila["cantidad_ventas"] for fila in filas)

    _encabezado("2.c  DISTRIBUCIÓN DE VENTAS POR MÉTODO DE PAGO")
    print(f"{'Método':<20}{'Ventas':>10}{'%':>9}{'Total':>18}{'Promedio':>16}")
    print("-" * 78)
    for fila in filas:
        porcentaje = fila["cantidad_ventas"] / total * 100
        print(
            f"{fila['metodo_pago']:<20}"
            f"{fila['cantidad_ventas']:>10,}"
            f"{porcentaje:>8.1f}%"
            f"{_moneda(fila['total_ventas']):>18}"
            f"{_moneda(fila['promedio_venta']):>16}"
        )
    return filas


def distribucion_navegador() -> list[dict[str, Any]]:
    """2.c / 3.b — Distribución de las ventas por canal de compra."""
    filas = queries.get_browser_distribution()
    total = sum(fila["cantidad_ventas"] for fila in filas)

    _encabezado("2.c  DISTRIBUCIÓN DE VENTAS POR NAVEGADOR / CANAL")
    print(f"{'Canal':<20}{'Ventas':>10}{'%':>9}{'Total':>18}{'Promedio':>16}")
    print("-" * 78)
    for fila in filas:
        porcentaje = fila["cantidad_ventas"] / total * 100
        print(
            f"{fila['navegador']:<20}"
            f"{fila['cantidad_ventas']:>10,}"
            f"{porcentaje:>8.1f}%"
            f"{_moneda(fila['total_ventas']):>18}"
            f"{_moneda(fila['promedio_venta']):>16}"
        )
    return filas


def uso_boletin_vale() -> list[dict[str, Any]]:
    """2.c — Distribución de las ventas según boletín y vale."""
    filas = queries.get_newsletter_voucher_usage()
    total = sum(fila["cantidad_ventas"] for fila in filas)

    _encabezado("2.c  DISTRIBUCIÓN DE VENTAS POR BOLETÍN Y VALE")
    print(f"{'Boletín':<10}{'Vale':<10}{'Ventas':>10}{'%':>9}{'Promedio':>18}")
    print("-" * 78)
    for fila in filas:
        porcentaje = fila["cantidad_ventas"] / total * 100
        print(
            f"{fila['boletin_nombre']:<10}"
            f"{fila['vale_nombre']:<10}"
            f"{fila['cantidad_ventas']:>10,}"
            f"{porcentaje:>8.1f}%"
            f"{_moneda(fila['promedio_venta']):>18}"
        )
    return filas


# ---------------------------------------------------------------------------
# 3. Análisis de tendencias
# ---------------------------------------------------------------------------


def meses_extremos() -> dict[str, Any]:
    """3.a — Meses con mayores y menores ventas."""
    datos = queries.get_trends(ANIO)

    _encabezado(f"3.a  MESES CON MAYORES Y MENORES VENTAS ({ANIO})")
    for etiqueta, clave in (
        ("MAYORES ventas", "meses_mayores_ventas"),
        ("MENORES ventas", "meses_menores_ventas"),
    ):
        for fila in datos[clave]:
            print(
                f"{etiqueta:<18}{fila['mes_nombre'].capitalize():<12}"
                f"{fila['cantidad_ventas']:>6,} ventas   "
                f"{_moneda(fila['total_ventas'])}"
            )
    return datos


def navegador_preferido(filas: list[dict[str, Any]]) -> None:
    """3.b — Canal más preferido y menos popular."""
    ordenadas = sorted(filas, key=lambda fila: fila["cantidad_ventas"], reverse=True)
    total = sum(fila["cantidad_ventas"] for fila in ordenadas)
    solo_online = [fila for fila in ordenadas if fila["navegador"] != "Tienda Física"]

    _encabezado("3.b  NAVEGADOR MÁS PREFERIDO Y MENOS POPULAR")
    mas = ordenadas[0]
    menos = ordenadas[-1]
    print(
        f"Canal más usado en general : {mas['navegador']} "
        f"({mas['cantidad_ventas']:,} ventas, "
        f"{mas['cantidad_ventas'] / total * 100:.1f}%)"
    )
    if solo_online:
        preferido = solo_online[0]
        print(
            f"Navegador más preferido    : {preferido['navegador']} "
            f"({preferido['cantidad_ventas']:,} ventas, "
            f"{preferido['cantidad_ventas'] / total * 100:.1f}%)"
        )
    print(
        f"Navegador menos popular    : {menos['navegador']} "
        f"({menos['cantidad_ventas']:,} ventas, "
        f"{menos['cantidad_ventas'] / total * 100:.1f}%)"
    )


def ventas_en_efectivo(filas: list[dict[str, Any]]) -> None:
    """3.c — Ventas pagadas contra entrega o en efectivo.

    Criterio oficial aclarado por el auxiliar del curso: se toma MetodoPago = 0
    tanto para efectivo como para contra entrega; los pagos con tarjeta de
    crédito o débito no se consideran contra entrega. La respuesta al punto es,
    entonces, el total de ventas con MetodoPago = 0.

    Como detalle complementario se desglosa dónde se cobró ese efectivo,
    cruzando el método de pago con el canal: el efectivo registrado en la
    tienda física corresponde a cobro en caja, mientras que el originado en un
    navegador solo pudo cobrarse al momento de la entrega.
    """
    efectivo = next(
        (fila for fila in filas if fila["metodo_pago"].lower() == "efectivo"), None
    )
    total_ventas = sum(fila["cantidad_ventas"] for fila in filas)
    total_monto = sum(fila["total_ventas"] for fila in filas)

    _encabezado("3.c  VENTAS PAGADAS CONTRA ENTREGA O EN EFECTIVO")
    if efectivo is None:
        print("No se encontraron ventas registradas con pago en efectivo.")
        return

    consulta = sql.SQL(
        """
        SELECT
            (v.id_navegador = 0) AS en_tienda,
            COUNT(v.id_venta)::int AS cantidad_ventas,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas
        FROM {} v
        WHERE v.id_metodo_pago = 0
        GROUP BY 1
        ORDER BY 1
        """
    ).format(qualified_table("venta"))
    desglose = {fila["en_tienda"]: fila for fila in fetch_all(consulta)}
    contra_entrega = desglose.get(False)
    en_caja = desglose.get(True)

    print(
        "RESPUESTA (criterio del auxiliar: MetodoPago = 0 cuenta como efectivo "
        "y como contra entrega)"
    )
    print(
        f"  Ventas contra entrega o en efectivo : "
        f"{efectivo['cantidad_ventas']:,} de {total_ventas:,} "
        f"({efectivo['cantidad_ventas'] / total_ventas * 100:.1f}%)"
    )
    print(
        f"  Monto acumulado                     : "
        f"{_moneda(efectivo['total_ventas'])} de {_moneda(total_monto)} "
        f"({efectivo['total_ventas'] / total_monto * 100:.1f}%)"
    )
    print()
    print("DETALLE COMPLEMENTARIO — dónde se cobró ese efectivo")
    if contra_entrega:
        print(
            f"  Originado en navegador (cobro en la entrega) : "
            f"{contra_entrega['cantidad_ventas']:,} ventas "
            f"({contra_entrega['cantidad_ventas'] / efectivo['cantidad_ventas'] * 100:.1f}%"
            f" del efectivo)   {_moneda(contra_entrega['total_ventas'])}"
        )
    if en_caja:
        print(
            f"  Originado en tienda física (cobro en caja)   : "
            f"{en_caja['cantidad_ventas']:,} ventas "
            f"({en_caja['cantidad_ventas'] / efectivo['cantidad_ventas'] * 100:.1f}%"
            f" del efectivo)   {_moneda(en_caja['total_ventas'])}"
        )


def uso_mensual_boletin_vale() -> list[dict[str, Any]]:
    """3.d — Meses con mayor uso de boletines y vales.

    Consulta propia de este bloque: el MCPServer expone el uso agregado de
    boletines y vales, pero no su desglose mensual.
    """
    consulta = sql.SQL(
        """
        SELECT
            EXTRACT(MONTH FROM v.fecha_compra)::int AS mes,
            COUNT(v.id_venta)::int AS cantidad_ventas,
            COALESCE(SUM(v.boletin), 0)::int AS boletines,
            COALESCE(SUM(v.vale), 0)::int AS vales
        FROM {} v
        WHERE v.fecha_compra >= %s AND v.fecha_compra < %s
        GROUP BY 1
        ORDER BY 1
        """
    ).format(qualified_table("venta"))
    filas = fetch_all(consulta, (date(ANIO, 1, 1), date(ANIO + 1, 1, 1)))
    for fila in filas:
        fila["mes_nombre"] = queries.MONTH_NAMES[fila["mes"] - 1]

    _encabezado(f"3.d  USO DE BOLETINES Y VALES POR MES ({ANIO})")
    print(f"{'Mes':<14}{'Ventas':>10}{'Boletines':>12}{'%':>8}{'Vales':>10}{'%':>8}")
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['mes_nombre'].capitalize():<14}"
            f"{fila['cantidad_ventas']:>10,}"
            f"{fila['boletines']:>12,}"
            f"{fila['boletines'] / fila['cantidad_ventas'] * 100:>7.1f}%"
            f"{fila['vales']:>10,}"
            f"{fila['vales'] / fila['cantidad_ventas'] * 100:>7.1f}%"
        )

    mas_boletines = max(filas, key=lambda fila: fila["boletines"])
    mas_vales = max(filas, key=lambda fila: fila["vales"])
    print()
    print(
        f"Mes con más boletines : {mas_boletines['mes_nombre'].capitalize()} "
        f"({mas_boletines['boletines']:,})"
    )
    print(
        f"Mes con más vales     : {mas_vales['mes_nombre'].capitalize()} "
        f"({mas_vales['vales']:,})"
    )
    return filas


# ---------------------------------------------------------------------------
# 6. Visualización de datos 
# ---------------------------------------------------------------------------


def _guardar(fig: plt.Figure, nombre: str) -> None:
    GRAFICAS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = GRAFICAS_DIR / nombre
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


def grafica_ventas_por_mes(filas: list[dict[str, Any]]) -> None:
    """Gráfico de líneas: evolución mensual de las ventas."""
    meses = [fila["mes_nombre"].capitalize()[:3] for fila in filas]
    totales = [fila["total_ventas"] for fila in filas]

    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.plot(meses, totales, marker="o", color=COLOR_PRINCIPAL, linewidth=2)

    maximo = max(totales)
    minimo = min(totales)
    ultimo = len(totales) - 1

    for indice, valor in enumerate(totales):
        anterior = totales[indice - 1] if indice > 0 else valor
        siguiente = totales[indice + 1] if indice < ultimo else valor
        debajo = valor <= anterior and valor <= siguiente

        if debajo or (valor >= anterior and valor >= siguiente):
            alineacion, desplazamiento_x = "center", 0
        elif valor > anterior:
            alineacion, desplazamiento_x = "right", -6
        else:
            alineacion, desplazamiento_x = "left", 6

        if indice == 0:
            alineacion, desplazamiento_x = "left", 4
        elif indice == ultimo:
            alineacion, desplazamiento_x = "right", -4

        if valor == minimo:
            ax.scatter(indice, valor, color=COLOR_SECUNDARIO, s=140, zorder=5)
            etiqueta = f"Q{valor:,.0f}\nMínimo"
            color_etiqueta = COLOR_SECUNDARIO
        elif valor == maximo:
            ax.scatter(indice, valor, color=COLOR_APOYO, s=140, zorder=5)
            etiqueta = f"Máximo\nQ{valor:,.0f}"
            color_etiqueta = COLOR_PRINCIPAL
        else:
            etiqueta = f"Q{valor:,.0f}"
            color_etiqueta = "#333333"

        ax.annotate(
            etiqueta,
            (indice, valor),
            textcoords="offset points",
            xytext=(desplazamiento_x, -14 if debajo else 14),
            ha=alineacion,
            va="top" if debajo else "bottom",
            fontsize=8,
            color=color_etiqueta,
        )

    rango = maximo - minimo
    ax.set_ylim(minimo - rango * 0.32, maximo + rango * 0.28)
    ax.set_title(f"Evolución mensual de las ventas ({ANIO})", fontsize=13, pad=14)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Total de ventas (quetzales)")
    ax.yaxis.set_major_formatter(lambda valor, _: f"Q{valor:,.0f}")
    _limpiar_ejes(ax)
    _guardar(fig, "01-ventas-por-mes.png")


def grafica_metodo_pago(filas: list[dict[str, Any]]) -> None:
    """Gráfico de barras: ventas por método de pago."""
    ordenadas = sorted(filas, key=lambda fila: fila["cantidad_ventas"], reverse=True)
    metodos = [fila["metodo_pago"] for fila in ordenadas]
    cantidades = [fila["cantidad_ventas"] for fila in ordenadas]
    total = sum(cantidades)

    fig, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(metodos, cantidades, color=COLOR_ACENTO, width=0.6)
    barras[0].set_color(COLOR_PRINCIPAL)

    for barra, cantidad in zip(barras, cantidades):
        ax.annotate(
            f"{cantidad:,}\n({cantidad / total * 100:.1f}%)",
            (barra.get_x() + barra.get_width() / 2, cantidad),
            textcoords="offset points",
            xytext=(0, 5),
            ha="center",
            fontsize=9,
        )

    ax.set_title("Ventas por método de pago", fontsize=13, pad=14)
    ax.set_xlabel("Método de pago")
    ax.set_ylabel("Cantidad de ventas")
    ax.set_ylim(0, max(cantidades) * 1.18)
    _limpiar_ejes(ax)
    _guardar(fig, "02-metodo-pago.png")


def grafica_navegador(filas: list[dict[str, Any]]) -> None:
    """Gráfico de barras horizontales: ventas por canal de compra."""
    ordenadas = sorted(filas, key=lambda fila: fila["cantidad_ventas"])
    canales = [fila["navegador"] for fila in ordenadas]
    cantidades = [fila["cantidad_ventas"] for fila in ordenadas]
    total = sum(cantidades)
    colores = [
        COLOR_PRINCIPAL if canal == "Tienda Física" else COLOR_ACENTO
        for canal in canales
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.barh(canales, cantidades, color=colores, height=0.6)

    for barra, cantidad in zip(barras, cantidades):
        ax.annotate(
            f"{cantidad:,} ({cantidad / total * 100:.1f}%)",
            (cantidad, barra.get_y() + barra.get_height() / 2),
            textcoords="offset points",
            xytext=(6, 0),
            va="center",
            fontsize=9,
        )

    ax.set_title("Ventas por navegador / canal de compra", fontsize=13, pad=14)
    ax.set_xlabel("Cantidad de ventas")
    ax.set_ylabel("Canal de compra")
    ax.set_xlim(0, max(cantidades) * 1.18)
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    ax.set_axisbelow(True)
    _limpiar_ejes(ax, rejilla_y=False)
    _guardar(fig, "03-navegador.png")


def grafica_boletin_vale(filas: list[dict[str, Any]]) -> None:
    """Gráfico de barras agrupadas: distribución de ventas por boletín y vale.

    Recibe la tabla cruzada de las cuatro combinaciones y la reduce a la
    distribución de cada instrumento por separado, que es lo que pide el
    punto 2.c.
    """
    con_boletin = sum(f["cantidad_ventas"] for f in filas if f["boletin"] == 1)
    sin_boletin = sum(f["cantidad_ventas"] for f in filas if f["boletin"] == 0)
    con_vale = sum(f["cantidad_ventas"] for f in filas if f["vale"] == 1)
    sin_vale = sum(f["cantidad_ventas"] for f in filas if f["vale"] == 0)
    total = con_boletin + sin_boletin

    categorias = ["Boletín", "Vale"]
    recibieron = [con_boletin, con_vale]
    no_recibieron = [sin_boletin, sin_vale]
    posiciones = list(range(len(categorias)))
    ancho = 0.35

    fig, ax = plt.subplots(figsize=(8, 5.5))
    barras_si = ax.bar(
        [posicion - ancho / 2 for posicion in posiciones],
        recibieron,
        width=ancho,
        label="Sí",
        color=COLOR_PRINCIPAL,
    )
    barras_no = ax.bar(
        [posicion + ancho / 2 for posicion in posiciones],
        no_recibieron,
        width=ancho,
        label="No",
        color=COLOR_ACENTO,
    )

    for grupo in (barras_si, barras_no):
        ax.bar_label(
            grupo,
            labels=[
                f"{int(barra.get_height()):,}\n({barra.get_height() / total * 100:.1f}%)"
                for barra in grupo
            ],
            padding=3,
            fontsize=9,
        )

    ax.set_title("Distribución de ventas por boletín y vale", fontsize=13, pad=14)
    ax.set_xlabel("Instrumento comercial")
    ax.set_ylabel("Cantidad de ventas")
    ax.set_xticks(posiciones)
    ax.set_xticklabels(categorias)
    ax.set_ylim(0, max(no_recibieron) * 1.20)
    ax.legend(title="¿Lo utilizó?", frameon=False)
    _limpiar_ejes(ax)
    _guardar(fig, "04-boletin-vale.png")


def grafica_boletin_vale_mensual(filas: list[dict[str, Any]]) -> None:
    """Gráfico de barras agrupadas: uso mensual de boletines y vales."""
    meses = [fila["mes_nombre"].capitalize()[:3] for fila in filas]
    boletines = [fila["boletines"] for fila in filas]
    vales = [fila["vales"] for fila in filas]
    posiciones = list(range(len(meses)))
    ancho = 0.4

    fig, ax = plt.subplots(figsize=(12, 5.5))
    barras_boletines = ax.bar(
        [posicion - ancho / 2 for posicion in posiciones],
        boletines,
        width=ancho,
        label="Boletines",
        color=COLOR_PRINCIPAL,
    )
    barras_vales = ax.bar(
        [posicion + ancho / 2 for posicion in posiciones],
        vales,
        width=ancho,
        label="Vales",
        color=COLOR_APOYO,
    )

    for grupo in (barras_boletines, barras_vales):
        ax.bar_label(grupo, fmt="%d", padding=3, fontsize=8)

    ax.set_title(f"Uso de boletines y vales por mes ({ANIO})", fontsize=13, pad=14)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cantidad de ventas con boletín / vale")
    ax.set_xticks(posiciones)
    ax.set_xticklabels(meses)
    ax.set_ylim(0, max(boletines) * 1.22)
    ax.legend(frameon=False, ncols=2, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    _limpiar_ejes(ax)
    _guardar(fig, "05-boletin-vale-mensual.png")


# ---------------------------------------------------------------------------


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Análisis exploratorio y de tendencias · ventas {ANIO}")

    estadisticas_basicas()
    mensuales = ventas_por_mes()
    metodos = distribucion_metodo_pago()
    navegadores = distribucion_navegador()
    boletin_vale = uso_boletin_vale()

    meses_extremos()
    navegador_preferido(navegadores)
    ventas_en_efectivo(metodos)
    mensual_boletin_vale = uso_mensual_boletin_vale()

    _encabezado("6.  GENERACIÓN DE GRÁFICAS")
    grafica_ventas_por_mes(mensuales)
    grafica_metodo_pago(metodos)
    grafica_navegador(navegadores)
    grafica_boletin_vale(boletin_vale)
    grafica_boletin_vale_mensual(mensual_boletin_vale)


if __name__ == "__main__":
    main()
