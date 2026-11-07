from pathlib import Path

import numpy as np
import pandas as pd

N = 50_000
rng = np.random.default_rng(42)  # semilla fija: siempre genera los mismos datos


def generar_transacciones(n: int = N) -> pd.DataFrame:
    id_cliente = rng.integers(1, 2001, n)

    df = pd.DataFrame({
        "id_transaccion": np.arange(1, n + 1),
        "id_cliente": id_cliente,
        "id_cuenta": id_cliente * 10 + rng.integers(1, 3, n),
        "fecha": pd.to_datetime("2026-01-01")
        + pd.to_timedelta(rng.integers(0, 300 * 24 * 60, n), unit="m"),
        "tipo": rng.choice(
            ["deposito", "retiro", "transferencia", "pago_tarjeta", "pago_servicio"],
            n,
            p=[0.25, 0.25, 0.2, 0.15, 0.15],
        ),
        "canal": rng.choice(["cajero", "app_movil", "sucursal", "web"], n),
        "estado": rng.choice(["completada", "pendiente", "rechazada"], n, p=[0.9, 0.07, 0.03]),
        "monto": np.round(rng.lognormal(mean=5, sigma=1, size=n), 2),
    })

    # Datos sucios a propósito, para practicar la limpieza
    idx_nulos = rng.choice(df.index, 500, replace=False)
    df.loc[idx_nulos, "monto"] = np.nan

    idx_neg = rng.choice(df.index, 200, replace=False)
    df.loc[idx_neg, "monto"] = -df.loc[idx_neg, "monto"]

    duplicados = df.sample(300, random_state=1)
    df = pd.concat([df, duplicados], ignore_index=True)

    return df


if __name__ == "__main__":
    carpeta_data = Path(__file__).resolve().parent.parent / "data"
    carpeta_data.mkdir(exist_ok=True)

    df = generar_transacciones()
    df.to_csv(carpeta_data / "transacciones.csv", index=False)
    print(f"Archivo generado con {len(df)} filas")