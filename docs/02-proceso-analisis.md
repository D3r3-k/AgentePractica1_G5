[ ← Regresar ](../README.md)

# Proceso de análisis

## 1. Carga del conjunto de datos

Se inició con la lectura del archivo original `data/raw/Venta_online_c.csv` usando `pandas.read_csv(..., sep=';', encoding='utf-8')`. Este paso permitió validar la estructura inicial del dataset, confirmar el delimitador correcto y conocer la cantidad de filas y columnas disponibles antes de aplicar transformaciones.

## 2. Normalización de nombres de columnas

Se estandarizaron los nombres de las columnas para un formato uniforme y más fácil de manejar en Python y PostgreSQL. La estrategia consistió en:

- eliminar espacios y caracteres no deseados,
- convertir a minúsculas,
- reemplazar espacios o guiones por guiones bajos,
- homogeneizar nombres como `Id_cliente` → `id_cliente`.

Esto evitó errores de referencia al trabajar con el csv y facilitó la integración con la base de datos.

## 3. Selección de variables relevantes

Se identificaron únicamente las columnas necesarias para el análisis y la carga final a la base de datos. Se descartaron atributos no requeridos para el modelo de negocio y se consolidó el conjunto de campos clave:

- `id_cliente`
- `edad`
- `genero`
- `n_compras`
- `venta_total`
- `fecha_compra`
- `monto_compra`
- `metodo_pago`
- `tiempo`
- `navegador`
- `boletin`
- `vale`

Con esta selección se redujo ruido y se evitó trabajar con datos redundantes o sin valor analítico.

## 4. Conversión de tipos y limpieza de valores

Se aplicó una normalización de tipos para asegurar consistencia:

- `edad`, `n_compras`, `venta_total`, `monto_compra`, `tiempo`, `boletin`, `vale` se convirtieron a numéricos.
- `fecha_compra` se transformó a formato de fecha (`datetime`).
- Variables categóricas como `genero`, `metodo_pago` y `navegador` se normalizaron a texto limpio, eliminando espacios y convirtiendo a minúsculas.

Esto fue clave para evitar inconsistencias como fechas mal formateadas.

## 5. Detección y eliminación de filas inválidas

Se revisaron las columnas críticas y se eliminaron las filas que presentaban valores nulos o inconsistentes en campos indispensables. Se aplicó una validación sobre columnas esenciales del negocio y del modelo de datos.

Se registró el número de filas descartadas, permitiendo conocer el impacto de la limpieza y asegurar que no se introdujeran registros corruptos a la base de datos.

## 6. Generación de tablas auxiliares

Para preparar el diseño de bases de datos relacional, se generaron tablas auxiliares a partir de los valores únicos de:

- género
- método de pago
- navegador

Esto permite normalizar dimensiones y evitar la duplicación de valores categóricos en la tabla principal de ventas o clientes.

## 7. Guardado del csv limpio

El resultado final se guardó en `data/processed/Venta_online_c_limpio.csv` con el mismo separador `;` y sin índice. Este archivo ya quedó listo para su carga a PostgreSQL, con una estructura limpia y consistente.

## 8. Preparación para la carga a base de datos

Adicionalmente, en la etapa de carga (`db/carga.py`) se reafirmó la validación del csv final:

- comprobación de columnas requeridas,
- coerción de tipos a enteros y fechas,
- eliminación de filas con valores no insertables,
- preparación de registros para `cliente` y `venta` en formato compatible con PostgreSQL.

Este enfoque garantizó que el archivo limpio pudiera cargarse de forma segura, evitando errores de integridad y facilitando la inserción masiva.

## Conclusión

El proceso de limpieza y preparación siguió un enfoque estructurado basado en: inspección inicial, estandarización, validación de tipos, eliminación de datos inválidos y normalización relacional. Gracias a este flujo, el archivo final quedó consistente, reproducible y listo para análisis y carga en la base de datos.