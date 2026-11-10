import pandas as pd
import pytest


@pytest.fixture
def datos_crudos() -> pd.DataFrame:
    """7 filas: 3 válidas (ids 1, 2, 6) y 4 problemáticas."""
    return pd.DataFrame({
        "id_transaccion": [1, 2, 2, 3, 4, 5, 6],
        "id_cliente": [10, 11, 11, 12, 13, 14, 15],
        "id_cuenta": [101, 111, 111, 121, 131, 141, 151],
        "fecha": [
            "2026-03-01 10:00:00", "2026-03-02 11:30:00", "2026-03-02 11:30:00",
            "2026-03-03 09:15:00", "2026-03-04 16:45:00", "2026-03-05 08:00:00",
            "2026-03-06 20:10:00",
        ],
        "tipo": ["deposito", "retiro", "retiro", "deposito", "retiro", "deposito", " Transferencia "],
        "canal": ["web", "cajero", "cajero", "app_movil", "web", "cajero", "sucursal"],
        "estado": ["completada"] * 7,
        "monto": [100.0, 50.0, 50.0, None, -20.0, 0.0, 75.5],
    })