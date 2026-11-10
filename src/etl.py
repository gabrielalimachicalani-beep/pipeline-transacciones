import logging
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV = BASE_DIR / "data" / "transacciones.csv"
RUTA_DB = BASE_DIR / "data" / "banco.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


def extract(ruta: Path) -> pd.DataFrame:
    """Lee los datos crudos desde el CSV."""
    df = pd.read_csv(ruta)
    log.info("Extract: %s filas leídas", len(df))
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia los datos: duplicados, nulos, montos inválidos y tipos."""
    df = df.copy()
    filas_inicio = len(df)

    # 1. Duplicados (la llave es id_transaccion)
    df = df.drop_duplicates(subset="id_transaccion")
    log.info("Transform: %s duplicados eliminados", filas_inicio - len(df))

    # 2. Montos nulos
    antes = len(df)
    df = df.dropna(subset=["monto"])
    log.info("Transform: %s filas con monto nulo eliminadas", antes - len(df))

    # 3. Montos inválidos (negativos o cero)
    antes = len(df)
    df = df[df["monto"] > 0]
    log.info("Transform: %s filas con monto inválido eliminadas", antes - len(df))

    # 4. Tipos de datos y texto normalizado
    df["fecha"] = pd.to_datetime(df["fecha"])
    for col in ["tipo", "canal", "estado"]:
        df[col] = df[col].str.strip().str.lower()

    # 5. Columna derivada útil para particionar y analizar
    df["fecha_dia"] = df["fecha"].dt.date.astype(str)

    log.info("Transform: %s filas finales", len(df))
    return df


def load(df: pd.DataFrame, ruta_db: Path, tabla: str = "transacciones", modo: str = "replace") -> None:
    """Carga en SQLite. modo='replace' = full refresh, modo='append' = incremental."""
    with sqlite3.connect(ruta_db) as conexion:
        df.to_sql(tabla, conexion, if_exists=modo, index=False)
    log.info("Load (%s): %s filas cargadas en la tabla '%s'", modo, len(df), tabla)


def main() -> None:
    df_crudo = extract(RUTA_CSV)
    df_limpio = transform(df_crudo)
    load(df_limpio, RUTA_DB)


if __name__ == "__main__":
    main()