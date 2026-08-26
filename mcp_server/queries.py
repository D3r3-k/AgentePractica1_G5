"""Consultas de análisis utilizadas por las herramientas del MCPServer."""

from __future__ import annotations

from datetime import date
import math
from typing import Any, Iterable

from psycopg2 import sql

from .database import fetch_all, fetch_one, qualified_table


MONTH_NAMES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def _table(name: str) -> sql.Composed:
    return qualified_table(name)


def _validate_year(year: int) -> None:
    if not 1900 <= year <= 2100:
        raise ValueError("El año debe estar entre 1900 y 2100.")


def get_basic_statistics() -> list[dict[str, Any]]:
    """Calcula media, mediana y moda de las variables numéricas."""
    query = sql.SQL(
        """
        SELECT variable, media, mediana, moda
        FROM (
            SELECT
                'edad'::text AS variable,
                AVG(c.edad)::double precision AS media,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY c.edad)::double precision AS mediana,
                mode() WITHIN GROUP (ORDER BY c.edad)::double precision AS moda
            FROM {} c

            UNION ALL

            SELECT
                'venta_total'::text AS variable,
                AVG(v.venta_total)::double precision AS media,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY v.venta_total)::double precision AS mediana,
                mode() WITHIN GROUP (ORDER BY v.venta_total)::double precision AS moda
            FROM {} v

            UNION ALL

            SELECT
                'num_compra'::text AS variable,
                AVG(v.num_compra)::double precision AS media,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY v.num_compra)::double precision AS mediana,
                mode() WITHIN GROUP (ORDER BY v.num_compra)::double precision AS moda
            FROM {} v

            UNION ALL

            SELECT
                'monto_compra'::text AS variable,
                AVG(v.monto_compra)::double precision AS media,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY v.monto_compra)::double precision AS mediana,
                mode() WITHIN GROUP (ORDER BY v.monto_compra)::double precision AS moda
            FROM {} v

            UNION ALL

            SELECT
                'tiempo'::text AS variable,
                AVG(v.tiempo)::double precision AS media,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY v.tiempo)::double precision AS mediana,
                mode() WITHIN GROUP (ORDER BY v.tiempo)::double precision AS moda
            FROM {} v
        ) AS estadisticas
        ORDER BY CASE variable
            WHEN 'edad' THEN 1
            WHEN 'venta_total' THEN 2
            WHEN 'num_compra' THEN 3
            WHEN 'monto_compra' THEN 4
            WHEN 'tiempo' THEN 5
        END
        """
    ).format(
        _table("cliente"),
        _table("venta"),
        _table("venta"),
        _table("venta"),
        _table("venta"),
    )
    return fetch_all(query)


def get_monthly_sales(year: int = 2021) -> list[dict[str, Any]]:
    """Obtiene cantidad, total y promedio de ventas agrupados por mes."""
    _validate_year(year)
    query = sql.SQL(
        """
        SELECT
            EXTRACT(MONTH FROM v.fecha_compra)::int AS mes,
            COUNT(*)::int AS cantidad_ventas,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} v
        WHERE v.fecha_compra >= %s AND v.fecha_compra < %s
        GROUP BY 1
        ORDER BY 1
        """
    ).format(_table("venta"))
    rows = fetch_all(query, (date(year, 1, 1), date(year + 1, 1, 1)))
    for row in rows:
        month = int(row["mes"])
        row["mes_nombre"] = MONTH_NAMES[month - 1]
    return rows


def get_payment_distribution() -> list[dict[str, Any]]:
    """Obtiene la distribución de ventas por método de pago."""
    query = sql.SQL(
        """
        SELECT
            mp.nombre AS metodo_pago,
            COUNT(v.id_venta)::int AS cantidad_ventas,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} v
        JOIN {} mp ON mp.id_metodo_pago = v.id_metodo_pago
        GROUP BY mp.id_metodo_pago, mp.nombre
        ORDER BY total_ventas DESC
        """
    ).format(_table("venta"), _table("metodo_pago"))
    return fetch_all(query)


def get_browser_distribution() -> list[dict[str, Any]]:
    """Obtiene la distribución de ventas por navegador/canal registrado."""
    query = sql.SQL(
        """
        SELECT
            n.nombre AS navegador,
            COUNT(v.id_venta)::int AS cantidad_ventas,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} v
        JOIN {} n ON n.id_navegador = v.id_navegador
        GROUP BY n.id_navegador, n.nombre
        ORDER BY cantidad_ventas DESC
        """
    ).format(_table("venta"), _table("navegador"))
    return fetch_all(query)


def get_newsletter_voucher_usage() -> list[dict[str, Any]]:
    """Obtiene el uso combinado de boletines y vales."""
    query = sql.SQL(
        """
        SELECT
            v.boletin::int AS boletin,
            CASE v.boletin WHEN 1 THEN 'Sí' ELSE 'No' END AS boletin_nombre,
            v.vale::int AS vale,
            CASE v.vale WHEN 1 THEN 'Sí' ELSE 'No' END AS vale_nombre,
            COUNT(v.id_venta)::int AS cantidad_ventas,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} v
        GROUP BY v.boletin, v.vale
        ORDER BY v.boletin, v.vale
        """
    ).format(_table("venta"))
    return fetch_all(query)


def get_trends(year: int = 2021) -> dict[str, Any]:
    """Identifica los meses de mayores y menores ventas."""
    monthly = get_monthly_sales(year)
    if not monthly:
        return {
            "anio": year,
            "meses_mayores_ventas": [],
            "meses_menores_ventas": [],
            "ventas_por_mes": [],
        }

    max_total = max(row["total_ventas"] for row in monthly)
    min_total = min(row["total_ventas"] for row in monthly)
    return {
        "anio": year,
        "meses_mayores_ventas": [
            row for row in monthly if row["total_ventas"] == max_total
        ],
        "meses_menores_ventas": [
            row for row in monthly if row["total_ventas"] == min_total
        ],
        "ventas_por_mes": monthly,
    }


def _age_filter(
    edad_minima: int | None,
    edad_maxima: int | None,
) -> tuple[sql.SQL, list[int]]:
    conditions: list[sql.SQL] = []
    params: list[int] = []
    if edad_minima is not None:
        if edad_minima < 0 or edad_minima > 120:
            raise ValueError("edad_minima debe estar entre 0 y 120.")
        conditions.append(sql.SQL("c.edad >= %s"))
        params.append(edad_minima)
    if edad_maxima is not None:
        if edad_maxima < 0 or edad_maxima > 120:
            raise ValueError("edad_maxima debe estar entre 0 y 120.")
        conditions.append(sql.SQL("c.edad <= %s"))
        params.append(edad_maxima)
    if edad_minima is not None and edad_maxima is not None and edad_minima > edad_maxima:
        raise ValueError("edad_minima no puede ser mayor que edad_maxima.")
    if not conditions:
        return sql.SQL(""), params
    return sql.SQL("WHERE ") + sql.SQL(" AND ").join(conditions), params


def get_age_segments(
    edad_minima: int | None = None,
    edad_maxima: int | None = None,
) -> list[dict[str, Any]]:
    """Agrupa clientes y ventas por rangos de edad."""
    where_clause, params = _age_filter(edad_minima, edad_maxima)
    query = sql.SQL(
        """
        SELECT
            CASE
                WHEN c.edad < 18 THEN '<18'
                WHEN c.edad BETWEEN 18 AND 25 THEN '18-25'
                WHEN c.edad BETWEEN 26 AND 35 THEN '26-35'
                WHEN c.edad BETWEEN 36 AND 45 THEN '36-45'
                WHEN c.edad BETWEEN 46 AND 55 THEN '46-55'
                ELSE '56+'
            END AS rango_edad,
            MIN(c.edad)::int AS edad_minima,
            MAX(c.edad)::int AS edad_maxima,
            COUNT(DISTINCT c.id_cliente)::int AS clientes,
            COUNT(v.id_venta)::int AS compras,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} c
        LEFT JOIN {} v ON v.id_cliente = c.id_cliente
        {}
        GROUP BY 1
        ORDER BY MIN(c.edad)
        """
    ).format(_table("cliente"), _table("venta"), where_clause)
    return fetch_all(query, params)


def get_gender_segments() -> list[dict[str, Any]]:
    """Compara clientes, compras y ventas entre géneros."""
    query = sql.SQL(
        """
        SELECT
            g.nombre AS genero,
            COUNT(DISTINCT c.id_cliente)::int AS clientes,
            COUNT(v.id_venta)::int AS compras,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} c
        JOIN {} g ON g.id_genero = c.id_genero
        LEFT JOIN {} v ON v.id_cliente = c.id_cliente
        GROUP BY g.id_genero, g.nombre
        ORDER BY total_ventas DESC
        """
    ).format(_table("cliente"), _table("genero"), _table("venta"))
    return fetch_all(query)


def get_newsletter_voucher_segments() -> list[dict[str, Any]]:
    """Compara el comportamiento de compra según boletines y vales."""
    query = sql.SQL(
        """
        SELECT
            CASE v.boletin WHEN 1 THEN 'Sí' ELSE 'No' END AS boletin,
            CASE v.vale WHEN 1 THEN 'Sí' ELSE 'No' END AS vale,
            COUNT(DISTINCT v.id_cliente)::int AS clientes,
            COUNT(v.id_venta)::int AS compras,
            COALESCE(SUM(v.venta_total), 0)::double precision AS total_ventas,
            COALESCE(AVG(v.venta_total), 0)::double precision AS promedio_venta
        FROM {} v
        GROUP BY v.boletin, v.vale
        ORDER BY v.boletin, v.vale
        """
    ).format(_table("venta"))
    return fetch_all(query)


def get_sale_age_correlation() -> dict[str, Any]:
    """Calcula la correlación de Pearson entre edad y venta total."""
    query = sql.SQL(
        """
        SELECT
            COUNT(*)::int AS tamano_muestra,
            corr(c.edad::double precision, v.venta_total::double precision)::double precision
                AS correlacion_pearson
        FROM {} c
        JOIN {} v ON v.id_cliente = c.id_cliente
        """
    ).format(_table("cliente"), _table("venta"))
    result = fetch_one(query) or {"tamano_muestra": 0, "correlacion_pearson": None}
    result["interpretacion"] = _correlation_interpretation(result["correlacion_pearson"])
    return result


def _correlation_interpretation(value: float | None) -> str:
    if value is None:
        return "No se pudo calcular la correlación con los datos disponibles."
    absolute = abs(value)
    if absolute < 0.1:
        strength = "prácticamente nula"
    elif absolute < 0.3:
        strength = "débil"
    elif absolute < 0.5:
        strength = "moderada"
    elif absolute < 0.7:
        strength = "fuerte"
    else:
        strength = "muy fuerte"
    direction = "positiva" if value > 0 else "negativa" if value < 0 else "nula"
    return f"La relación lineal es {strength} y {direction}; correlación no implica causalidad."


def _categorical_association(
    rows: Iterable[dict[str, Any]],
    row_key: str,
    column_key: str,
    value_key: str,
) -> dict[str, Any]:
    """Calcula chi-cuadrado y V de Cramér desde una tabla de frecuencias."""
    rows = list(rows)
    row_labels = list(dict.fromkeys(str(row[row_key]) for row in rows))
    column_labels = list(dict.fromkeys(str(row[column_key]) for row in rows))
    matrix = {
        row_label: {column_label: 0 for column_label in column_labels}
        for row_label in row_labels
    }
    for row in rows:
        matrix[str(row[row_key])][str(row[column_key])] = int(row[value_key])

    total = sum(sum(columns.values()) for columns in matrix.values())
    if total == 0 or len(row_labels) < 2 or len(column_labels) < 2:
        return {
            "tabla_contingencia": rows,
            "chi_cuadrado": 0.0,
            "cramers_v": 0.0,
            "interpretacion": "No hay suficientes categorías o registros para medir asociación.",
        }

    row_totals = {label: sum(matrix[label].values()) for label in row_labels}
    column_totals = {
        label: sum(matrix[row_label][label] for row_label in row_labels)
        for label in column_labels
    }
    chi_square = 0.0
    for row_label in row_labels:
        for column_label in column_labels:
            expected = row_totals[row_label] * column_totals[column_label] / total
            observed = matrix[row_label][column_label]
            if expected > 0:
                chi_square += (observed - expected) ** 2 / expected

    denominator = min(len(row_labels) - 1, len(column_labels) - 1)
    cramers_v = math.sqrt((chi_square / total) / denominator) if denominator else 0.0
    return {
        "tabla_contingencia": rows,
        "chi_cuadrado": round(chi_square, 6),
        "cramers_v": round(cramers_v, 6),
        "interpretacion": _association_interpretation(cramers_v),
    }


def _association_interpretation(value: float) -> str:
    if value < 0.1:
        strength = "muy débil"
    elif value < 0.3:
        strength = "débil"
    elif value < 0.5:
        strength = "moderada"
    else:
        strength = "fuerte"
    return f"La asociación entre las variables es {strength}; asociación no implica causalidad."


def get_gender_payment_relationship() -> dict[str, Any]:
    """Examina la asociación entre género y método de pago."""
    query = sql.SQL(
        """
        SELECT
            g.nombre AS genero,
            mp.nombre AS metodo_pago,
            COUNT(v.id_venta)::int AS cantidad_ventas
        FROM {} v
        JOIN {} c ON c.id_cliente = v.id_cliente
        JOIN {} g ON g.id_genero = c.id_genero
        JOIN {} mp ON mp.id_metodo_pago = v.id_metodo_pago
        GROUP BY g.nombre, mp.nombre
        ORDER BY g.nombre, mp.nombre
        """
    ).format(
        _table("venta"),
        _table("cliente"),
        _table("genero"),
        _table("metodo_pago"),
    )
    rows = fetch_all(query)
    return _categorical_association(rows, "genero", "metodo_pago", "cantidad_ventas")


def get_newsletter_voucher_relationship() -> dict[str, Any]:
    """Examina la asociación entre el uso de boletines y vales."""
    query = sql.SQL(
        """
        SELECT
            CASE v.boletin WHEN 1 THEN 'Sí' ELSE 'No' END AS boletin,
            CASE v.vale WHEN 1 THEN 'Sí' ELSE 'No' END AS vale,
            COUNT(v.id_venta)::int AS cantidad_ventas
        FROM {} v
        GROUP BY v.boletin, v.vale
        ORDER BY v.boletin, v.vale
        """
    ).format(_table("venta"))
    rows = fetch_all(query)
    return _categorical_association(rows, "boletin", "vale", "cantidad_ventas")
