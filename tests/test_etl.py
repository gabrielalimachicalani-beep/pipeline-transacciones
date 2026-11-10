import sqlite3

import pandas as pd

from etl import extract, load, transform


def test_no_hay_duplicados(datos_crudos):
    limpio = transform(datos_crudos)
    assert limpio["id_transaccion"].is_unique


def test_no_hay_montos_nulos_ni_invalidos(datos_crudos):
    limpio = transform(datos_crudos)
    assert limpio["monto"].notna().all()
    assert (limpio["monto"] > 0).all()


def test_fechas_son_validas(datos_crudos):
    limpio = transform(datos_crudos)
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha"])
    assert limpio["fecha"].notna().all()


def test_conteo_de_filas_tras_transform(datos_crudos):
    limpio = transform(datos_crudos)
    assert len(limpio) == 3
    assert len(limpio) <= len(datos_crudos)
    assert sorted(limpio["id_transaccion"]) == [1, 2, 6]


def test_texto_normalizado(datos_crudos):
    limpio = transform(datos_crudos)
    assert "transferencia" in limpio["tipo"].values


def test_transform_no_modifica_el_original(datos_crudos):
    copia = datos_crudos.copy()
    transform(datos_crudos)
    pd.testing.assert_frame_equal(datos_crudos, copia)


def test_pipeline_completo_extract_transform_load(datos_crudos, tmp_path):
    """Test de integración: CSV -> limpieza -> SQLite, todo en una carpeta temporal."""
    ruta_csv = tmp_path / "entrada.csv"
    ruta_db = tmp_path / "prueba.db"
    datos_crudos.to_csv(ruta_csv, index=False)

    load(transform(extract(ruta_csv)), ruta_db)

    with sqlite3.connect(ruta_db) as con:
        filas = con.execute("SELECT COUNT(*) FROM transacciones").fetchone()[0]
        minimo = con.execute("SELECT MIN(monto) FROM transacciones").fetchone()[0]
    assert filas == 3
    assert minimo > 0


def test_full_refresh_es_idempotente(datos_crudos, tmp_path):
    """Cargar dos veces el mismo dato no debe duplicarlo."""
    ruta_db = tmp_path / "prueba.db"
    limpio = transform(datos_crudos)
    load(limpio, ruta_db)
    load(limpio, ruta_db)

    with sqlite3.connect(ruta_db) as con:
        filas = con.execute("SELECT COUNT(*) FROM transacciones").fetchone()[0]
    assert filas == 3