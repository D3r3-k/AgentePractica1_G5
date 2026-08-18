from pathlib import Path
import pandas as pd


def cargar_csv(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    return pd.read_csv(ruta, sep=';', encoding='utf-8-sig', dtype=str)


def normalizar_decimal(valor):
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto == "":
        return None
    return texto.replace(",", ".")


def validar_decimal(df, columnas):
    for columna in columnas:
        if columna not in df.columns:
            print(f"Advertencia: la columna '{columna}' no existe.")
            continue

        valores = df[columna].map(normalizar_decimal)
        serie_numeric = pd.to_numeric(valores, errors="coerce")
        invalidos = serie_numeric.isna()

        if invalidos.any():
            print(f"Valores inválidos en '{columna}': {int(invalidos.sum())}")
            print(df.loc[invalidos, [columna]].head())

        df[columna] = serie_numeric
        print(f"Estadísticas '{columna}' -> Máx: {df[columna].max():.2f}, Media: {df[columna].mean():.2f}")

    return df


def validar_fecha(df, columna):
    if columna not in df.columns:
        print(f"Advertencia: la columna '{columna}' no existe.")
        return df

    # Formato real del CSV: dd.mm.yy
    serie_fecha = pd.to_datetime(df[columna], format="%d.%m.%y", errors="coerce")
    invalidos = serie_fecha.isna()

    if invalidos.any():
        print(f"Valores inválidos en '{columna}': {int(invalidos.sum())}")
        print(df.loc[invalidos, [columna]].head())
    else:
        print(f"Todas las fechas en '{columna}' validadas correctamente.")

    df[columna] = serie_fecha
    return df


def validar_codigos(df, reglas):
    for columna, valores_permitidos in reglas.items():
        if columna not in df.columns:
            print(f"Advertencia: la columna '{columna}' no existe.")
            continue

        valores = df[columna].astype(str).str.strip()
        permitidos = {str(v) for v in valores_permitidos}
        invalidos = ~valores.isin(permitidos)

        if invalidos.any():
            print(f"Valores inválidos en '{columna}': {int(invalidos.sum())}")
            print(df.loc[invalidos, [columna]].head())
        else:
            print(f"Todos los valores en '{columna}' son válidos.")

        df[columna] = pd.to_numeric(valores, errors="coerce")

    return df


def revisar(df):
    print("=== Revisión inicial ===")
    print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
    print("\nValores nulos por columna:")
    print(df.isna().sum())
    print(f"\nFilas duplicadas: {int(df.duplicated().sum())}")
    print("\nTipos de datos:")
    print(df.dtypes)


def limpiar_csv(ruta_entrada, ruta_salida):
    df = cargar_csv(ruta_entrada)
    revisar(df)

    filas_iniciales = len(df)

    # 1) Eliminar duplicados
    df = df.drop_duplicates()
    filas_sin_duplicados = len(df)

    # 2) Validaciones por tipo
    print("\n=== Validando decimales ===")
    df = validar_decimal(df, ["Venta_total", "MontoCompra"])

    print("\n=== Validando fechas ===")
    df = validar_fecha(df, "FechaCompra")

    print("\n=== Validando códigos ===")
    reglas = {
        "Genero": [0, 1],
        "MetodoPago": [0, 1, 2],
        "Navegador": [0, 1, 2, 3, 4],
        "Boletin": [0, 1],
        "Vale": [0, 1]
    }
    df = validar_codigos(df, reglas)

    # 3) Eliminar filas con datos inválidos
    columnas_obligatorias = [
        "Venta_total",
        "MontoCompra",
        "FechaCompra",
        "Genero",
        "MetodoPago",
        "Navegador",
        "Boletin",
        "Vale"
    ]
    df = df.dropna(subset=columnas_obligatorias)
    filas_finales = len(df)

    # 4) Guardar archivo limpio
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, sep=';', index=False, encoding='utf-8')

    # 5) Reporte final
    print("\n" + "="*50)
    print("=== REPORTE FINAL DE LIMPIEZA ===")
    print("="*50)
    print(f"Filas iniciales:       {filas_iniciales}")
    print(f"Filas sin duplicados:  {filas_sin_duplicados}")
    print(f"Filas finales:         {filas_finales}")
    print(f"Filas eliminadas:      {filas_iniciales - filas_finales}")
    print(f"Archivo guardado en:   {ruta_salida}")
    print("="*50)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[1]

    ruta_entrada = base_dir / "data" / "raw" / "Venta_online_c.csv"
    ruta_salida = base_dir / "data" / "processed" / "Venta_online_c_limpio.csv"

    print(f"Archivo entrada: {ruta_entrada}")
    print(f"Archivo salida: {ruta_salida}\n")

    limpiar_csv(ruta_entrada, ruta_salida)