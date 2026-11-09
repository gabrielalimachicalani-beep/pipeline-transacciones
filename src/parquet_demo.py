import shutil
import time
from pathlib import Path

import pandas as pd

from etl import RUTA_CSV, extract, transform

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_CSV_LIMPIO = BASE_DIR / "data" / "transacciones_limpio.csv"
RUTA_PARQUET = BASE_DIR / "data" / "transacciones.parquet"
CARPETA_PARTICIONADA = BASE_DIR / "data" / "transacciones_particionado"


def tamano_mb(ruta: Path) -> float:
    if ruta.is_dir():
        total = sum(f.stat().st_size for f in ruta.rglob("*") if f.is_file())
    else:
        total = ruta.stat().st_size
    return total / 1024 / 1024


def medir(funcion, repeticiones: int = 5) -> float:
    """Devuelve el tiempo promedio en segundos."""
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion()
        tiempos.append(time.perf_counter() - inicio)
    return sum(tiempos) / len(tiempos)


def paso1_comparar_formatos(df: pd.DataFrame) -> None:
    df.to_csv(RUTA_CSV_LIMPIO, index=False)
    df.to_parquet(RUTA_PARQUET, index=False)

    print("\n=== PASO 1: CSV vs PARQUET ===")
    print(f"Tamaño CSV:     {tamano_mb(RUTA_CSV_LIMPIO):.2f} MB")
    print(f"Tamaño Parquet: {tamano_mb(RUTA_PARQUET):.2f} MB")

    t_csv = medir(lambda: pd.read_csv(RUTA_CSV_LIMPIO))
    t_parquet = medir(lambda: pd.read_parquet(RUTA_PARQUET))
    t_csv_col = medir(lambda: pd.read_csv(RUTA_CSV_LIMPIO, usecols=["monto"]))
    t_parquet_col = medir(lambda: pd.read_parquet(RUTA_PARQUET, columns=["monto"]))

    print(f"Leer todo, CSV:               {t_csv:.4f} s")
    print(f"Leer todo, Parquet:           {t_parquet:.4f} s")
    print(f"Leer solo 'monto', CSV:       {t_csv_col:.4f} s")
    print(f"Leer solo 'monto', Parquet:   {t_parquet_col:.4f} s")


def paso2_particionar(df: pd.DataFrame) -> None:
    df = df.copy()
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    # Si la carpeta ya existe, la borramos: si no, se duplicarían los datos
    if CARPETA_PARTICIONADA.exists():
        shutil.rmtree(CARPETA_PARTICIONADA)

    df.to_parquet(CARPETA_PARTICIONADA, partition_cols=["anio", "mes"], index=False)

    print("\n=== PASO 2: PARQUET PARTICIONADO ===")
    print(f"Tamaño total particionado: {tamano_mb(CARPETA_PARTICIONADA):.2f} MB")

    t_todo = medir(lambda: pd.read_parquet(RUTA_PARQUET).query("mes == 3")
                   if "mes" in pd.read_parquet(RUTA_PARQUET, columns=["fecha"]).columns
                   else pd.read_parquet(RUTA_PARQUET, columns=["fecha", "monto"])
                   .query("fecha.dt.month == 3"))
    t_particion = medir(lambda: pd.read_parquet(
        CARPETA_PARTICIONADA, filters=[("mes", "=", 3)]))

    marzo = pd.read_parquet(CARPETA_PARTICIONADA, filters=[("mes", "=", 3)])
    print(f"Filas leídas solo de marzo: {len(marzo)} de {len(df)}")
    print(f"Leer todo y filtrar marzo:      {t_todo:.4f} s")
    print(f"Leer solo la partición de marzo: {t_particion:.4f} s")


if __name__ == "__main__":
    df_limpio = transform(extract(RUTA_CSV))
    paso1_comparar_formatos(df_limpio)
    paso2_particionar(df_limpio)