"""Segmentación de clientes y análisis de correlación (puntos 4 y 5).

Imprime en consola los resultados solicitados y guarda en `graficas/` las
cuatro visualizaciones que aporta este bloque al mínimo de siete del punto 6.

Reutiliza las consultas del MCPServer (`mcp_server/queries.py`) para que el
informe, el servidor MCP y el agente conversacional devuelvan exactamente las
mismas cifras. Las consultas propias de este bloque son las que el MCPServer no
expone: el desglose enriquecido por rango de edad y por género, el par
(edad, venta_total) sin agregar que alimenta el diagrama de dispersión, y la
correlación de Spearman.

Uso:
    python analisis/segmentacion.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from psycopg2 import sql

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from mcp_server import queries
from mcp_server.database import fetch_all, fetch_one, qualified_table


ANIO = 2021
GRAFICAS_DIR = PROJECT_ROOT / "graficas"

# Misma paleta que `analisis/exploratorio.py`: el informe debe leerse como un
# único conjunto de gráficas y no como dos bloques con criterios distintos.
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

# Umbral convencional para declarar significancia estadística.
ALFA = 0.05


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
# Utilidades estadísticas
#
# El proyecto no depende de SciPy: los tres contrastes que necesita este bloque
# (Pearson sobre muestra grande, chi-cuadrado con 1 y con 2 grados de libertad)
# tienen forma cerrada y se resuelven con `math`.
# ---------------------------------------------------------------------------


def _p_normal_dos_colas(z: float) -> float:
    """Probabilidad de dos colas de la distribución normal estándar."""
    return math.erfc(abs(z) / math.sqrt(2))


def _p_chi_cuadrado(chi_cuadrado: float, grados_libertad: int) -> float | None:
    """Valor p de una chi-cuadrado con 1 o 2 grados de libertad.

    Son los dos únicos casos que aparecen en este bloque (tablas 2x2 y 2x3) y
    ambos tienen solución analítica, de modo que no hace falta SciPy.
    """
    if chi_cuadrado <= 0:
        return 1.0
    if grados_libertad == 1:
        return math.erfc(math.sqrt(chi_cuadrado / 2))
    if grados_libertad == 2:
        return math.exp(-chi_cuadrado / 2)
    return None


def _significancia_pearson(r: float, n: int) -> dict[str, Any]:
    """Contrasta H0: r = 0 y estima cuánta varianza explica la relación."""
    if n <= 2 or abs(r) >= 1:
        return {"t": None, "p": None, "r2_porcentaje": None}
    t = r * math.sqrt(n - 2) / math.sqrt(1 - r**2)
    return {
        "t": t,
        # Con n = 6,500 la t de Student es indistinguible de la normal.
        "p": _p_normal_dos_colas(t),
        "r2_porcentaje": r**2 * 100,
    }


def _veredicto(p: float | None) -> str:
    if p is None:
        return "no evaluable"
    return (
        f"p = {p:.4g} → significativa (p < {ALFA})"
        if p < ALFA
        else f"p = {p:.4g} → NO significativa (p ≥ {ALFA})"
    )


# ---------------------------------------------------------------------------
# 4. Segmentación de clientes
# ---------------------------------------------------------------------------


def segmentacion_edad() -> list[dict[str, Any]]:
    """4.a — Agrupa a los clientes por edad y analiza sus patrones de compra.

    Consulta propia de este bloque. El MCPServer expone la segmentación por
    edad con el ticket promedio; aquí se añaden la mediana, el monto por
    compra, el número de compras y la penetración de boletín y vale, que son
    los patrones de compra que pide el enunciado.
    """
    consulta = sql.SQL(
        """
        SELECT
            CASE
                WHEN c.edad BETWEEN 18 AND 25 THEN '18-25'
                WHEN c.edad BETWEEN 26 AND 35 THEN '26-35'
                WHEN c.edad BETWEEN 36 AND 45 THEN '36-45'
                WHEN c.edad BETWEEN 46 AND 55 THEN '46-55'
                ELSE '56+'
            END AS rango_edad,
            COUNT(DISTINCT c.id_cliente)::int AS clientes,
            COUNT(v.id_venta)::int AS compras,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            AVG(v.venta_total)::double precision AS ticket_promedio,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY v.venta_total)::double precision
                AS ticket_mediana,
            AVG(v.num_compra)::double precision AS compras_promedio,
            AVG(v.monto_compra)::double precision AS monto_por_compra,
            AVG(v.boletin::double precision) * 100 AS pct_boletin,
            AVG(v.vale::double precision) * 100 AS pct_vale
        FROM {} c
        JOIN {} v ON v.id_cliente = c.id_cliente
        GROUP BY 1
        ORDER BY 1
        """
    ).format(qualified_table("cliente"), qualified_table("venta"))
    filas = fetch_all(consulta)

    total_clientes = sum(fila["clientes"] for fila in filas)
    total_monto = sum(fila["total_ventas"] for fila in filas)

    _encabezado("4.a  SEGMENTACIÓN DE CLIENTES POR RANGO DE EDAD")
    print(
        f"{'Rango':<9}{'Clientes':>10}{'%':>8}{'Ticket prom.':>15}"
        f"{'Mediana':>13}{'Boletín':>10}{'Vale':>9}"
    )
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['rango_edad']:<9}"
            f"{fila['clientes']:>10,}"
            f"{fila['clientes'] / total_clientes * 100:>7.1f}%"
            f"{_moneda(fila['ticket_promedio']):>15}"
            f"{_moneda(fila['ticket_mediana']):>13}"
            f"{fila['pct_boletin']:>9.1f}%"
            f"{fila['pct_vale']:>8.1f}%"
        )

    mayor = max(filas, key=lambda fila: fila["ticket_promedio"])
    menor = min(filas, key=lambda fila: fila["ticket_promedio"])
    brecha = mayor["ticket_promedio"] - menor["ticket_promedio"]
    print()
    print(
        f"Ticket más alto : {mayor['rango_edad']:<7} "
        f"{_moneda(mayor['ticket_promedio'])}"
    )
    print(
        f"Ticket más bajo : {menor['rango_edad']:<7} "
        f"{_moneda(menor['ticket_promedio'])}"
    )
    print(
        f"Brecha entre extremos: {_moneda(brecha)} "
        f"({brecha / menor['ticket_promedio'] * 100:.1f}% sobre el rango más bajo)"
    )
    print(
        f"Facturación total segmentada: {_moneda(total_monto)} "
        f"· {total_clientes:,} clientes"
    )
    return filas


def segmentacion_genero() -> dict[str, Any]:
    """4.b — Compara el comportamiento de compra entre géneros.

    Consulta propia: el MCPServer entrega el ticket por género; aquí se añade
    el reparto de método de pago, canal, boletín y vale, que es lo que permite
    hablar de «comportamiento de compra» y no solo de gasto.
    """
    consulta = sql.SQL(
        """
        SELECT
            g.nombre AS genero,
            COUNT(v.id_venta)::int AS compras,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            AVG(v.venta_total)::double precision AS ticket_promedio,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY v.venta_total)::double precision
                AS ticket_mediana,
            AVG(c.edad::double precision) AS edad_promedio,
            AVG(v.num_compra)::double precision AS compras_promedio,
            AVG(v.boletin::double precision) * 100 AS pct_boletin,
            AVG(v.vale::double precision) * 100 AS pct_vale,
            AVG((v.id_navegador = 0)::int::double precision) * 100 AS pct_tienda_fisica
        FROM {} v
        JOIN {} c ON c.id_cliente = v.id_cliente
        JOIN {} g ON g.id_genero = c.id_genero
        GROUP BY g.id_genero, g.nombre
        ORDER BY g.id_genero
        """
    ).format(
        qualified_table("venta"),
        qualified_table("cliente"),
        qualified_table("genero"),
    )
    filas = fetch_all(consulta)
    contingencia = queries.get_gender_payment_relationship()["tabla_contingencia"]

    _encabezado("4.b  COMPORTAMIENTO DE COMPRA POR GÉNERO")
    print(
        f"{'Género':<12}{'Compras':>9}{'Ticket prom.':>15}{'Mediana':>12}"
        f"{'Edad prom.':>12}{'Boletín':>10}{'Vale':>8}"
    )
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['genero']:<12}"
            f"{fila['compras']:>9,}"
            f"{_moneda(fila['ticket_promedio']):>15}"
            f"{_moneda(fila['ticket_mediana']):>12}"
            f"{fila['edad_promedio']:>11.1f}"
            f"{fila['pct_boletin']:>9.1f}%"
            f"{fila['pct_vale']:>7.1f}%"
        )

    # Reparto porcentual del método de pago dentro de cada género: es la forma
    # correcta de comparar dos grupos de distinto tamaño.
    generos = list(dict.fromkeys(fila["genero"] for fila in contingencia))
    metodos = list(dict.fromkeys(fila["metodo_pago"] for fila in contingencia))
    reparto: dict[str, dict[str, float]] = {}
    for genero in generos:
        del_genero = [f for f in contingencia if f["genero"] == genero]
        total = sum(f["cantidad_ventas"] for f in del_genero)
        reparto[genero] = {
            f["metodo_pago"]: f["cantidad_ventas"] / total * 100 for f in del_genero
        }

    print()
    print("Reparto del método de pago dentro de cada género (%)")
    print(f"{'Género':<12}" + "".join(f"{metodo:>18}" for metodo in metodos))
    print("-" * 78)
    for genero in generos:
        print(
            f"{genero:<12}"
            + "".join(f"{reparto[genero][metodo]:>17.1f}%" for metodo in metodos)
        )

    brecha_maxima = max(
        abs(reparto[generos[0]][metodo] - reparto[generos[1]][metodo])
        for metodo in metodos
    )
    diferencia_ticket = abs(
        filas[0]["ticket_promedio"] - filas[1]["ticket_promedio"]
    )
    print()
    print(
        f"Diferencia de ticket entre géneros : {_moneda(diferencia_ticket)} "
        f"({diferencia_ticket / min(f['ticket_promedio'] for f in filas) * 100:.1f}%)"
    )
    print(
        f"Mayor brecha en método de pago     : {brecha_maxima:.1f} puntos porcentuales"
    )
    return {"resumen": filas, "reparto_pago": reparto, "metodos": metodos}


def segmentacion_boletin_vale() -> list[dict[str, Any]]:
    """4.c — Agrupa los clientes por boletín y vale y analiza sus patrones."""
    filas = queries.get_newsletter_voucher_segments()
    total_compras = sum(fila["compras"] for fila in filas)
    total_monto = sum(fila["total_ventas"] for fila in filas)

    _encabezado("4.c  SEGMENTACIÓN POR BOLETÍN Y VALE")
    print(
        f"{'Boletín':<10}{'Vale':<8}{'Compras':>10}{'%':>8}"
        f"{'Ticket prom.':>15}{'Facturación':>16}{'% fact.':>10}"
    )
    print("-" * 78)
    for fila in filas:
        print(
            f"{fila['boletin']:<10}"
            f"{fila['vale']:<8}"
            f"{fila['compras']:>10,}"
            f"{fila['compras'] / total_compras * 100:>7.1f}%"
            f"{_moneda(fila['promedio_venta']):>15}"
            f"{_moneda(fila['total_ventas']):>16}"
            f"{fila['total_ventas'] / total_monto * 100:>9.1f}%"
        )

    def _agregado(clave: str, valor: str) -> tuple[int, float, float]:
        grupo = [fila for fila in filas if fila[clave] == valor]
        compras = sum(fila["compras"] for fila in grupo)
        monto = sum(fila["total_ventas"] for fila in grupo)
        return compras, monto, monto / compras if compras else 0.0

    print()
    print("Efecto de cada instrumento por separado")
    print(f"{'Grupo':<26}{'Compras':>10}{'Ticket prom.':>16}")
    print("-" * 78)
    for etiqueta, clave, valor in (
        ("Con boletín", "boletin", "Sí"),
        ("Sin boletín", "boletin", "No"),
        ("Con vale", "vale", "Sí"),
        ("Sin vale", "vale", "No"),
    ):
        compras, _, ticket = _agregado(clave, valor)
        print(f"{etiqueta:<26}{compras:>10,}{_moneda(ticket):>16}")

    _, _, con_boletin = _agregado("boletin", "Sí")
    _, _, sin_boletin = _agregado("boletin", "No")
    print()
    print(
        f"Diferencia por boletín : {_moneda(con_boletin - sin_boletin)} "
        f"({(con_boletin / sin_boletin - 1) * 100:+.1f}%)"
    )

    # El vale se evalúa dentro de cada grupo de boletín: comparar «con vale»
    # contra «sin vale» sobre el total mezclaría el efecto de los dos
    # instrumentos, porque los suscritos usan vale con mucha más frecuencia.
    print()
    print("Efecto del vale controlando por boletín (evita la paradoja de Simpson)")
    for boletin in ("No", "Sí"):
        con_vale = next(
            f for f in filas if f["boletin"] == boletin and f["vale"] == "Sí"
        )
        sin_vale = next(
            f for f in filas if f["boletin"] == boletin and f["vale"] == "No"
        )
        delta = con_vale["promedio_venta"] - sin_vale["promedio_venta"]
        print(
            f"  Boletín = {boletin:<3} → con vale {_moneda(con_vale['promedio_venta'])} "
            f"vs sin vale {_moneda(sin_vale['promedio_venta'])}   "
            f"{_moneda(delta)} ({delta / sin_vale['promedio_venta'] * 100:+.1f}%)"
        )
    return filas


# ---------------------------------------------------------------------------
# 5. Análisis de correlación
# ---------------------------------------------------------------------------


def correlacion_venta_edad() -> dict[str, Any]:
    """5.a — Relación entre el total de la venta y la edad del cliente."""
    resultado = queries.get_sale_age_correlation()
    r = resultado["correlacion_pearson"]
    n = resultado["tamano_muestra"]
    prueba = _significancia_pearson(r, n)

    # Spearman detecta relaciones monótonas no lineales que Pearson se pierde.
    # Consulta propia: `corr()` de PostgreSQL solo calcula Pearson.
    consulta = sql.SQL(
        """
        SELECT corr(rango_edad, rango_venta)::double precision AS spearman
        FROM (
            SELECT
                rank() OVER (ORDER BY c.edad)::double precision AS rango_edad,
                rank() OVER (ORDER BY v.venta_total)::double precision AS rango_venta
            FROM {} c
            JOIN {} v ON v.id_cliente = c.id_cliente
        ) AS rangos
        """
    ).format(qualified_table("cliente"), qualified_table("venta"))
    spearman = (fetch_one(consulta) or {}).get("spearman")

    _encabezado("5.a  CORRELACIÓN ENTRE TOTAL DE LA VENTA Y EDAD DEL CLIENTE")
    print(f"Tamaño de muestra           : {n:,} observaciones")
    print(f"Correlación de Pearson (r)  : {r:+.4f}")
    if spearman is not None:
        print(f"Correlación de Spearman     : {spearman:+.4f}")
    if prueba["r2_porcentaje"] is not None:
        print(
            f"Varianza explicada (r²)     : {prueba['r2_porcentaje']:.3f}% "
            "del gasto"
        )
        print(f"Contraste H0: r = 0         : {_veredicto(prueba['p'])}")
    print(f"Interpretación              : {resultado['interpretacion']}")
    print()
    print(
        "Lectura: el contraste rechaza por poco la hipótesis de correlación cero,\n"
        "pero r² muestra que la edad explica una fracción despreciable del gasto.\n"
        "Con 6,500 observaciones incluso una desviación mínima respecto de cero\n"
        "resulta significativa: el hallazgo es estadísticamente detectable y a la\n"
        "vez irrelevante para la operación."
    )

    resultado["spearman"] = spearman
    resultado.update(prueba)
    return resultado


def correlacion_genero_pago() -> dict[str, Any]:
    """5.b — Asociación entre el género del cliente y el método de pago."""
    resultado = queries.get_gender_payment_relationship()
    tabla = resultado["tabla_contingencia"]
    generos = list(dict.fromkeys(fila["genero"] for fila in tabla))
    metodos = list(dict.fromkeys(fila["metodo_pago"] for fila in tabla))
    grados_libertad = (len(generos) - 1) * (len(metodos) - 1)
    p = _p_chi_cuadrado(resultado["chi_cuadrado"], grados_libertad)

    _encabezado("5.b  ASOCIACIÓN ENTRE GÉNERO Y MÉTODO DE PAGO")
    print("Tabla de contingencia (cantidad de ventas)")
    print(f"{'Género':<12}" + "".join(f"{metodo:>18}" for metodo in metodos))
    print("-" * 78)
    for genero in generos:
        fila_valores = {
            f["metodo_pago"]: f["cantidad_ventas"] for f in tabla if f["genero"] == genero
        }
        print(
            f"{genero:<12}" + "".join(f"{fila_valores[m]:>18,}" for m in metodos)
        )
    print()
    print(f"Chi-cuadrado          : {resultado['chi_cuadrado']:.4f} "
          f"({grados_libertad} grados de libertad)")
    print(f"V de Cramér           : {resultado['cramers_v']:.4f}")
    print(f"Contraste de independencia : {_veredicto(p)}")
    print(f"Interpretación        : {resultado['interpretacion']}")
    print()
    print(
        "Lectura: no se rechaza la independencia. Género y método de pago se\n"
        "comportan como variables no relacionadas en este conjunto de datos."
    )

    resultado["grados_libertad"] = grados_libertad
    resultado["p"] = p
    return resultado


def correlacion_boletin_vale() -> dict[str, Any]:
    """5.c — Asociación entre los clientes que utilizan boletines y vales."""
    resultado = queries.get_newsletter_voucher_relationship()
    tabla = resultado["tabla_contingencia"]
    grados_libertad = 1
    p = _p_chi_cuadrado(resultado["chi_cuadrado"], grados_libertad)

    matriz = {
        (fila["boletin"], fila["vale"]): fila["cantidad_ventas"] for fila in tabla
    }
    con_boletin = matriz[("Sí", "Sí")] + matriz[("Sí", "No")]
    sin_boletin = matriz[("No", "Sí")] + matriz[("No", "No")]
    tasa_con = matriz[("Sí", "Sí")] / con_boletin * 100
    tasa_sin = matriz[("No", "Sí")] / sin_boletin * 100

    _encabezado("5.c  ASOCIACIÓN ENTRE EL USO DE BOLETINES Y VALES")
    print("Tabla de contingencia (cantidad de ventas)")
    print(f"{'':<14}{'Vale = Sí':>14}{'Vale = No':>14}{'Total':>12}")
    print("-" * 78)
    for boletin in ("Sí", "No"):
        con_vale = matriz[(boletin, "Sí")]
        sin_vale = matriz[(boletin, "No")]
        print(
            f"{'Boletín = ' + boletin:<14}{con_vale:>14,}{sin_vale:>14,}"
            f"{con_vale + sin_vale:>12,}"
        )
    print()
    print(f"Chi-cuadrado          : {resultado['chi_cuadrado']:.4f} "
          f"({grados_libertad} grado de libertad)")
    print(f"V de Cramér           : {resultado['cramers_v']:.4f}")
    print(f"Contraste de independencia : {_veredicto(p)}")
    print(f"Interpretación        : {resultado['interpretacion']}")
    print()
    print(f"Tasa de uso de vale entre suscritos al boletín    : {tasa_con:.1f}%")
    print(f"Tasa de uso de vale entre NO suscritos al boletín : {tasa_sin:.1f}%")
    print(
        f"Razón de tasas: los suscritos usan vale {tasa_con / tasa_sin:.2f} veces más."
    )
    print()
    print(
        "Lectura: es la única asociación de este bloque que resulta significativa.\n"
        "El vale no se distribuye de forma pareja: se concentra en quienes ya\n"
        "reciben el boletín, que es el canal por el que se entrega."
    )

    resultado["grados_libertad"] = grados_libertad
    resultado["p"] = p
    resultado["tasa_vale_con_boletin"] = tasa_con
    resultado["tasa_vale_sin_boletin"] = tasa_sin
    return resultado


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


def grafica_segmentacion_edad(filas: list[dict[str, Any]]) -> None:
    """Barras verticales: ticket promedio por rango de edad.

    La pregunta es «¿gastan distinto los clientes según su edad?». Se grafica
    el ticket promedio y no la facturación total, porque esta última seguiría
    el tamaño de cada segmento y respondería otra pregunta.
    """
    rangos = [fila["rango_edad"] for fila in filas]
    tickets = [fila["ticket_promedio"] for fila in filas]
    clientes = [fila["clientes"] for fila in filas]
    promedio_global = sum(
        fila["total_ventas"] for fila in filas
    ) / sum(fila["compras"] for fila in filas)

    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    barras = ax.bar(rangos, tickets, color=COLOR_ACENTO, width=0.68)

    maximo = max(tickets)
    minimo = min(tickets)
    for barra, ticket in zip(barras, tickets):
        if ticket == maximo:
            barra.set_color(COLOR_APOYO)
        elif ticket == minimo:
            barra.set_color(COLOR_SECUNDARIO)

    # Las cifras van dentro de la barra: la línea del promedio general cruza a
    # la altura del ticket y cualquier etiqueta colocada encima chocaría con ella.
    for barra, ticket, cantidad in zip(barras, tickets, clientes):
        ax.annotate(
            f"Q{ticket:,.2f}\nn = {cantidad:,}",
            (barra.get_x() + barra.get_width() / 2, ticket),
            textcoords="offset points",
            xytext=(0, -14),
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color="white",
        )

    ax.axhline(
        promedio_global,
        color=COLOR_PRINCIPAL,
        linestyle="--",
        linewidth=1.4,
        label=f"Promedio general Q{promedio_global:,.2f}",
    )

    ax.set_title(
        "Ticket promedio por rango de edad del cliente", fontsize=13, pad=14
    )
    ax.set_xlabel("Rango de edad (años)")
    ax.set_ylabel("Ticket promedio (quetzales)")
    # El eje arranca en cero: se comparan magnitudes entre categorías y recortar
    # la base exageraría visualmente una brecha que es de apenas Q20.
    ax.set_ylim(0, maximo * 1.22)
    ax.yaxis.set_major_formatter(lambda valor, _: f"Q{valor:,.0f}")
    ax.legend(frameon=False, loc="upper right")
    _limpiar_ejes(ax)
    _guardar(fig, "06-segmentacion-edad.png")


def grafica_genero_metodo_pago(datos: dict[str, Any]) -> None:
    """Barras horizontales 100 %: método de pago dentro de cada género.

    Al normalizar cada género a 100 % los dos grupos se vuelven comparables a
    pesar de tener distinto tamaño, y la ausencia de diferencia —que es el
    hallazgo— se ve como dos franjas prácticamente idénticas.
    """
    reparto = datos["reparto_pago"]
    metodos = datos["metodos"]
    generos = list(reparto.keys())
    colores = (COLOR_PRINCIPAL, COLOR_ACENTO, COLOR_APOYO, COLOR_NEUTRO)

    fig, ax = plt.subplots(figsize=(11, 4))
    izquierda = [0.0] * len(generos)
    for indice, metodo in enumerate(metodos):
        valores = [reparto[genero][metodo] for genero in generos]
        barras = ax.barh(
            generos,
            valores,
            left=izquierda,
            height=0.62,
            color=colores[indice % len(colores)],
            label=metodo,
        )
        for barra, valor in zip(barras, valores):
            ax.annotate(
                f"{valor:.1f}%",
                (barra.get_x() + valor / 2, barra.get_y() + barra.get_height() / 2),
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold",
            )
        izquierda = [acumulado + valor for acumulado, valor in zip(izquierda, valores)]

    ax.set_title(
        "Reparto del método de pago dentro de cada género", fontsize=13, pad=52
    )
    ax.set_xlabel("Porcentaje de las compras del género (%)")
    ax.set_ylabel("Género")
    ax.set_xlim(0, 100)
    # La leyenda va arriba y no debajo: abajo competiría con la línea de fuente
    # que `_guardar` añade al pie de todas las gráficas del informe.
    ax.legend(
        title="Método de pago",
        frameon=False,
        ncols=len(metodos),
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
    )
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    _guardar(fig, "07-genero-metodo-pago.png")


def grafica_dispersion_edad_venta(correlacion: dict[str, Any]) -> None:
    """Dispersión con recta de regresión: edad frente a total de la venta.

    Es el gráfico que sostiene el punto 5.a. La nube de puntos muestra que no
    hay estructura y la recta, casi horizontal, traduce el r ≈ 0 a una forma
    que se interpreta de un vistazo.
    """
    consulta = sql.SQL(
        """
        SELECT c.edad::int AS edad, v.venta_total::double precision AS venta_total
        FROM {} c
        JOIN {} v ON v.id_cliente = c.id_cliente
        """
    ).format(qualified_table("cliente"), qualified_table("venta"))
    filas = fetch_all(consulta)
    edades = [fila["edad"] for fila in filas]
    ventas = [fila["venta_total"] for fila in filas]

    n = len(edades)
    media_edad = sum(edades) / n
    media_venta = sum(ventas) / n
    covarianza = sum(
        (edad - media_edad) * (venta - media_venta)
        for edad, venta in zip(edades, ventas)
    )
    varianza_edad = sum((edad - media_edad) ** 2 for edad in edades)
    pendiente = covarianza / varianza_edad
    interseccion = media_venta - pendiente * media_edad

    r = correlacion["correlacion_pearson"]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.scatter(
        edades,
        ventas,
        s=14,
        alpha=0.28,
        color=COLOR_ACENTO,
        edgecolors="none",
        label=f"Ventas individuales (n = {n:,})",
    )

    extremos = [min(edades), max(edades)]
    ax.plot(
        extremos,
        [interseccion + pendiente * edad for edad in extremos],
        color=COLOR_SECUNDARIO,
        linewidth=2,
        label=(
            f"Recta de regresión (pendiente {pendiente:+.2f} Q por año)"
        ),
    )
    ax.axhline(
        media_venta,
        color=COLOR_PRINCIPAL,
        linestyle="--",
        linewidth=1.3,
        label=f"Venta promedio Q{media_venta:,.2f}",
    )

    ax.set_title(
        "Relación entre la edad del cliente y el total de la venta",
        fontsize=13,
        pad=14,
    )
    ax.set_xlabel("Edad del cliente (años)")
    ax.set_ylabel("Total de la venta (quetzales)")
    # Holgura superior para que la leyenda y el recuadro del coeficiente no se
    # encimen con los valores atípicos más altos.
    ax.set_ylim(min(ventas) - max(ventas) * 0.03, max(ventas) * 1.20)
    ax.yaxis.set_major_formatter(lambda valor, _: f"Q{valor:,.0f}")
    ax.annotate(
        f"r de Pearson = {r:+.4f}\nr² = {r ** 2 * 100:.3f}% de la varianza\n"
        "Sin relación aprovechable",
        xy=(0.985, 0.96),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#f2f2f2", "edgecolor": "#cccccc"},
    )
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    _limpiar_ejes(ax)
    _guardar(fig, "08-dispersion-edad-venta.png")


def grafica_boletin_vale_ticket(filas: list[dict[str, Any]]) -> None:
    """Mapa de calor 2x2: ticket promedio por combinación de boletín y vale.

    Las cuatro celdas son el cruce completo de dos variables binarias. El mapa
    de calor deja ver de golpe que la separación ocurre entre filas —boletín—
    y no entre columnas —vale—, que es exactamente el hallazgo del punto 4.c.
    """
    orden_boletin = ("Sí", "No")
    orden_vale = ("Sí", "No")
    matriz = {
        (fila["boletin"], fila["vale"]): fila for fila in filas
    }
    valores = [
        [matriz[(boletin, vale)]["promedio_venta"] for vale in orden_vale]
        for boletin in orden_boletin
    ]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    imagen = ax.imshow(valores, cmap="Blues", aspect="auto")

    minimo = min(min(fila) for fila in valores)
    maximo = max(max(fila) for fila in valores)
    for i, boletin in enumerate(orden_boletin):
        for j, vale in enumerate(orden_vale):
            celda = matriz[(boletin, vale)]
            ticket = celda["promedio_venta"]
            # Texto claro sobre celdas oscuras para mantener el contraste.
            color = "white" if ticket > (minimo + maximo) / 2 else "#1a1a1a"
            ax.text(
                j,
                i,
                f"Q{ticket:,.2f}\n{celda['compras']:,} compras",
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold",
                color=color,
            )

    ax.set_xticks(range(len(orden_vale)))
    ax.set_xticklabels([f"Vale: {vale}" for vale in orden_vale])
    ax.set_yticks(range(len(orden_boletin)))
    ax.set_yticklabels([f"Boletín: {boletin}" for boletin in orden_boletin])
    ax.set_title(
        "Ticket promedio según uso de boletín y vale", fontsize=13, pad=14
    )
    ax.set_xlabel("¿La compra usó vale de descuento?")
    ax.set_ylabel("¿El cliente está suscrito al boletín?")

    barra_color = fig.colorbar(imagen, ax=ax, shrink=0.85)
    barra_color.set_label("Ticket promedio (quetzales)")
    barra_color.formatter = plt.FuncFormatter(lambda valor, _: f"Q{valor:,.0f}")
    barra_color.update_ticks()

    ax.set_xticks([x - 0.5 for x in range(1, len(orden_vale))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(orden_boletin))], minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)
    _guardar(fig, "09-boletin-vale-ticket.png")


# ---------------------------------------------------------------------------


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Segmentación de clientes y análisis de correlación · ventas {ANIO}")

    edad = segmentacion_edad()
    genero = segmentacion_genero()
    boletin_vale = segmentacion_boletin_vale()

    correlacion_edad = correlacion_venta_edad()
    correlacion_genero_pago()
    correlacion_boletin_vale()

    _encabezado("6.  GENERACIÓN DE GRÁFICAS")
    grafica_segmentacion_edad(edad)
    grafica_genero_metodo_pago(genero)
    grafica_dispersion_edad_venta(correlacion_edad)
    grafica_boletin_vale_ticket(boletin_vale)


if __name__ == "__main__":
    main()
