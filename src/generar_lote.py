import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(7)


def generar_lote(n: int, id_inicial: int) -> pd.DataFrame:
    id_cliente = rng.integers(1, 2001, n)
    df = pd.DataFrame({
        "id_transaccion": np.arange(id_inicial, id_inicial + n),
        "id_cliente": id_cliente,
        "id_cuenta": id_cliente * 10 + rng.integers(1, 3, n),
        "fecha": pd.to_datetime("2026-10-29")
        + pd.to_timedelta(rng.integers(0, 5 * 24 * 60, n), unit="m"),
        "tipo": rng.choice(
            ["deposito", "retiro", "transferencia", "pago_tarjeta", "pago_servicio"], n),
        "canal": rng.choice(["cajero", "app_movil", "sucursal", "web"], n),
        "estado": rng.choice(["completada", "pendiente", "rechazada"], n, p=[0.9, 0.07, 0.03]),
        "monto": np.round(rng.lognormal(mean=5, sigma=1, size=n), 2),
    })
    # Un poco de suciedad para que el transform tenga trabajo
    df.loc[rng.choice(df.index, 30, replace=False), "monto"] = np.nan
    return pd.concat([df, df.sample(50, random_state=2)], ignore_index=True)


if __name__ == "__main__":
    id_inicial = int(sys.argv[1]) if len(sys.argv) > 1 else 50001
    df = generar_lote(5000, id_inicial)
    df.to_csv(BASE_DIR / "data" / "transacciones_nuevas.csv", index=False)
    print(f"Lote generado: {len(df)} filas, ids desde {id_inicial}")