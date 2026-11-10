from etl import load, transform
from etl_incremental import obtener_ultimo_id


def test_ultimo_id_sin_tabla_devuelve_cero(tmp_path):
    assert obtener_ultimo_id(tmp_path / "vacia.db") == 0


def test_ultimo_id_con_datos(datos_crudos, tmp_path):
    ruta_db = tmp_path / "prueba.db"
    load(transform(datos_crudos), ruta_db)
    assert obtener_ultimo_id(ruta_db) == 6