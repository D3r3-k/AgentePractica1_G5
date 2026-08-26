import sys
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2 import Error, sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os


# En consolas Windows (cp1252) los símbolos ✓/✗ rompen la salida.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Esquema destino: todas las consultas se califican con él.
ESQUEMA = os.getenv("DB_SCHEMA", "geren2")

# Tamaño de lote para las inserciones masivas.
TAM_LOTE = 1000

COLUMNAS_ENTERAS = [
    "Id_cliente",
    "Edad",
    "Genero",
    "N_Compras",
    "MetodoPago",
    "Tiempo",
    "Navegador",
    "Boletin",
    "Vale"
]
COLUMNAS_DECIMALES = ["Venta_total", "MontoCompra"]
COLUMNA_FECHA = "FechaCompra"


def tabla(nombre):
    """Devuelve el identificador calificado geren2.<tabla>."""
    return sql.Identifier(ESQUEMA, nombre)


def conectar_bd(host, user, password, database, port=5432, sslmode=None):
    """Conecta a la base de datos PostgreSQL."""
    try:
        conexion = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            sslmode=sslmode or "prefer"
        )
        print(f"✓ Conexión exitosa a {database}")
        return conexion
    except Error as err:
        print(f"✗ Error de conexión: {err}")
        return None


def verificar_esquema(conexion):
    """Comprueba que el esquema y las tablas existan antes de insertar."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
            (ESQUEMA,)
        )
        if cursor.fetchone() is None:
            print(f"✗ No existe el esquema '{ESQUEMA}'. Ejecuta primero db/schema.sql")
            return False

        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name IN ('genero','metodo_pago','navegador','cliente','venta')
            """,
            (ESQUEMA,)
        )
        existentes = {fila[0] for fila in cursor.fetchall()}
        faltantes = {'genero', 'metodo_pago', 'navegador', 'cliente', 'venta'} - existentes
        if faltantes:
            print(f"✗ Faltan tablas en '{ESQUEMA}': {', '.join(sorted(faltantes))}")
            print("✓ Ejecuta primero db/schema.sql")
            return False

    print(f"✓ Esquema '{ESQUEMA}' verificado")
    return True


def cargar_datos_limpios(ruta_csv):
    """Carga el CSV limpio."""
    try:
        df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8')
        print(f"✓ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        return df
    except Exception as err:
        print(f"✗ Error al cargar CSV: {err}")
        return None


def preparar_datos(df):
    """Convierte los tipos y descarta filas no insertables."""
    requeridas = COLUMNAS_ENTERAS + COLUMNAS_DECIMALES + [COLUMNA_FECHA]
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        print(f"✗ Faltan columnas en el CSV: {', '.join(faltantes)}")
        return None

    df = df.copy()
    for columna in COLUMNAS_ENTERAS + COLUMNAS_DECIMALES:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
    df[COLUMNA_FECHA] = pd.to_datetime(df[COLUMNA_FECHA], errors="coerce")

    filas_previas = len(df)
    df = df.dropna(subset=requeridas)
    descartadas = filas_previas - len(df)
    if descartadas > 0:
        print(f"✗ Filas descartadas por valores inválidos: {descartadas}")

    for columna in COLUMNAS_ENTERAS:
        df[columna] = df[columna].astype("int64")
    df[COLUMNA_FECHA] = df[COLUMNA_FECHA].dt.date

    print(f"✓ Filas listas para insertar: {len(df)}")
    return df


def hay_datos_previos(conexion):
    """Indica si la tabla venta ya tiene registros."""
    with conexion.cursor() as cursor:
        cursor.execute(sql.SQL("SELECT EXISTS (SELECT 1 FROM {})").format(tabla("venta")))
        return cursor.fetchone()[0]


def vaciar_tablas(conexion):
    """Vacía venta y cliente reiniciando la secuencia de venta."""
    with conexion.cursor() as cursor:
        cursor.execute(
            sql.SQL("TRUNCATE {}, {} RESTART IDENTITY").format(tabla("venta"), tabla("cliente"))
        )
    print("✓ Tablas venta y cliente vaciadas")


def insertar_clientes(conexion, df):
    """Inserta los clientes únicos en la tabla Cliente."""
    clientes = df[['Id_cliente', 'Edad', 'Genero']].drop_duplicates(subset=['Id_cliente'])
    filas = list(clientes.itertuples(index=False, name=None))

    print(f"\nInsertando clientes ({len(filas)} únicos)...")

    consulta = sql.SQL("""
        INSERT INTO {} (id_cliente, edad, id_genero)
        VALUES %s
        ON CONFLICT (id_cliente) DO NOTHING
        RETURNING id_cliente
    """).format(tabla("cliente"))

    with conexion.cursor() as cursor:
        resultado = execute_values(cursor, consulta, filas, page_size=TAM_LOTE, fetch=True)

    insertados = len(resultado)
    print(f"✓ Clientes insertados: {insertados}")
    if insertados < len(filas):
        print(f"  (omitidos por ya existir: {len(filas) - insertados})")
    return insertados


def insertar_ventas(conexion, df):
    """Inserta todas las ventas en la tabla Venta."""
    columnas = [
        'Id_cliente', 'Venta_total', 'N_Compras', COLUMNA_FECHA, 'MontoCompra',
        'MetodoPago', 'Tiempo', 'Navegador', 'Boletin', 'Vale'
    ]
    filas = list(df[columnas].itertuples(index=False, name=None))

    print(f"\nInsertando ventas ({len(filas)} filas)...")

    consulta = sql.SQL("""
        INSERT INTO {}
        (id_cliente, venta_total, num_compra, fecha_compra, monto_compra,
         id_metodo_pago, tiempo, id_navegador, boletin, vale)
        VALUES %s
    """).format(tabla("venta"))

    with conexion.cursor() as cursor:
        execute_values(cursor, consulta, filas, page_size=TAM_LOTE)

    print(f"✓ Ventas insertadas: {len(filas)}")
    return len(filas)


def generar_reporte(conexion):
    """Genera un reporte de los datos insertados."""
    print("\n" + "="*60)
    print("=== REPORTE DE BASE DE DATOS ===")
    print("="*60)

    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(tabla("cliente")))
            num_clientes = cursor.fetchone()[0]
            print(f"Total de clientes:          {num_clientes:,}")

            # Un solo recorrido de venta para conteo, rango de fechas y montos.
            cursor.execute(sql.SQL("""
                SELECT COUNT(*), MIN(fecha_compra), MAX(fecha_compra),
                       SUM(venta_total), AVG(venta_total)
                FROM {}
            """).format(tabla("venta")))
            num_ventas, fecha_min, fecha_max, total_ventas, promedio_ventas = cursor.fetchone()

            print(f"Total de ventas:            {num_ventas:,}")
            if num_ventas == 0:
                print("(sin ventas registradas)")
                print("="*60)
                return

            print(f"Rango de fechas:            {fecha_min} a {fecha_max}")
            print(f"Venta total:                ${total_ventas:,.2f}")
            print(f"Promedio por venta:         ${promedio_ventas:,.2f}")

            cursor.execute(sql.SQL("""
                SELECT g.nombre, COUNT(*) AS cantidad
                FROM {} c
                JOIN {} g ON c.id_genero = g.id_genero
                GROUP BY g.nombre
                ORDER BY cantidad DESC
            """).format(tabla("cliente"), tabla("genero")))
            print("\nDistribución por género:")
            for nombre, cantidad in cursor.fetchall():
                print(f"  - {nombre}: {cantidad:,}")

            cursor.execute(sql.SQL("""
                SELECT m.nombre, COUNT(*) AS cantidad
                FROM {} v
                JOIN {} m ON v.id_metodo_pago = m.id_metodo_pago
                GROUP BY m.nombre
                ORDER BY cantidad DESC
            """).format(tabla("venta"), tabla("metodo_pago")))
            print("\nMétodos de pago más usados:")
            for nombre, cantidad in cursor.fetchall():
                print(f"  - {nombre}: {cantidad:,}")

    except Error as err:
        print(f"✗ Error al generar reporte: {err}")

    print("="*60)


def main():
    reemplazar = "--reemplazar" in sys.argv

    # Cargar variables de entorno
    base_dir = Path(__file__).resolve().parents[1]
    env_path = base_dir / ".env"

    if not env_path.exists():
        print(f"✗ No se encontró el archivo .env en {env_path}")
        print("✓ Crea un archivo .env con las variables DB_*")
        return

    load_dotenv(env_path)

    # Leer configuración desde .env
    global ESQUEMA
    ESQUEMA = os.getenv("DB_SCHEMA", "geren2")
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 5432))
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    database = os.getenv("DB_NAME", "ventas_online")
    sslmode = os.getenv("DB_SSLMODE")

    ruta_csv = base_dir / "data" / "processed" / "Venta_online_c_limpio.csv"

    # Validar que el CSV existe
    if not ruta_csv.exists():
        print(f"✗ No se encontró el archivo: {ruta_csv}")
        print("✓ Ejecuta primero: py .\\db\\limpieza.py")
        return

    print("="*60)
    print("=== CARGA DE DATOS A BASE DE DATOS ===")
    print("="*60)
    print(f"CSV entrada: {ruta_csv}")
    print(f"BD destino:  {database}@{host}:{port} (esquema {ESQUEMA})\n")

    # Conectar
    conexion = conectar_bd(host, user, password, database, port, sslmode)
    if not conexion:
        print("✗ No se pudo conectar a la BD. Verifica las credenciales en .env")
        return

    try:
        if not verificar_esquema(conexion):
            return

        # Cargar y preparar datos
        df = cargar_datos_limpios(ruta_csv)
        if df is None or df.empty:
            print("✗ El CSV está vacío o no se pudo cargar.")
            return

        df = preparar_datos(df)
        if df is None or df.empty:
            print("✗ No quedaron filas válidas para insertar.")
            return

        if hay_datos_previos(conexion):
            if not reemplazar:
                print(f"\n✗ La tabla {ESQUEMA}.venta ya tiene datos.")
                print("✓ Vuelve a ejecutar con --reemplazar para vaciarlas y recargar.")
                return
            vaciar_tablas(conexion)

        # Insertar datos: cliente y venta van en la misma transacción.
        insertar_clientes(conexion, df)
        insertar_ventas(conexion, df)
        conexion.commit()

        # Reporte final
        generar_reporte(conexion)

        print("\n✓ Carga completada exitosamente")

    except Exception as err:
        print(f"✗ Error inesperado: {err}")
        conexion.rollback()
        print("✓ Se revirtieron los cambios (rollback)")

    finally:
        conexion.close()


if __name__ == "__main__":
    main()
