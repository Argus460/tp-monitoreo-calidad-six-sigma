import pytest
from datetime import date, datetime

from sistema_calidad import Equipo, DatosInvalidos


@pytest.fixture(autouse=True)
def reset_equipo_state():
    Equipo.contador = 0


def test_creacion_equipo_valido():
    """Prueba que un equipo con datos válidos se crea sin errores."""
    equipo = Equipo("calibre", date(2026, 3, 1))
    assert isinstance(equipo, Equipo)


def test_categoria_vacia_lanza_error():
    """Prueba que crear un equipo con categoría vacía lanza un error."""
    with pytest.raises(DatosInvalidos, match="categoria del equipo"):
        Equipo("", date(2026, 3, 1))


def test_categoria_solo_espacios_lanza_error():
    """Prueba que una categoría con solo espacios también se rechaza."""
    with pytest.raises(DatosInvalidos, match="categoria del equipo"):
        Equipo("   ", date(2026, 3, 1))


def test_categoria_que_no_es_texto_lanza_error():
    """Prueba que una categoría que no es str lanza un error."""
    with pytest.raises(DatosInvalidos, match="categoria del equipo"):
        Equipo(123, date(2026, 3, 1))


def test_fecha_calibracion_que_no_es_date_lanza_error():
    """Prueba que una fecha de calibración como string lanza un error."""
    with pytest.raises(DatosInvalidos, match="fecha_calibracion"):
        Equipo("calibre", "2026-03-01")  # Fecha como string en lugar de date


def test_fecha_calibracion_datetime_lanza_error():
    """Prueba que un datetime se rechaza aunque sea subclase de date."""
    with pytest.raises(DatosInvalidos, match="fecha_calibracion"):
        Equipo("calibre", datetime(2026, 3, 1, 10, 30))
