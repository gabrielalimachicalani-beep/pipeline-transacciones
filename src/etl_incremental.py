import sqlite3
from pathlib import Path

from etl import BASE_DIR, RUTA_DB, extract, load, log, transform

RUTA_NUEVAS = BASE_DIR / "data" / "transacciones_nuevas.csv"


def obtener_ultimo_id(ruta_db: Path) -> int:
    """Marca de agua: el id más alto ya cargado."""
    try:
        with sqlite3.connect(ruta_db) as con:
            fila = con.execute("SELECT MAX(id_transaccion) FROM transacciones").fetchone()
            return fila[0] or 0
    except sqlite3.OperationalError:  # la tabla aún no existe
        return 0


def main() -> None:
    ultimo_id = obtener_ultimo_id(RUTA_DB)
    log.info("Marca de agua (último id cargado): %s", ultimo_id)

    df = extract(RUTA_NUEVAS)
    df = df[df["id_transaccion"] > ultimo_id]
    log.info("Registros nuevos a procesar: %s", len(df))

    if df.empty:
        log.info("No hay datos nuevos. Fin.")
        return

    df = transform(df)
    load(df, RUTA_DB, modo="append")


if __name__ == "__main__":
    main()