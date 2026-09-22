import pytest
from datetime import date

from sistema_calidad import Certificacion, DatosInvalidos


def test_certificacion_valida_se_crea_sin_errores():
    """Prueba que una certificación con datos válidos se crea sin errores."""
    cert = Certificacion("ISO 9001", date(2026, 12, 31))
    assert isinstance(cert, Certificacion)


def test_creacion_certificacion_valida():
    """Prueba la creación de una certificación válida."""
    cert = Certificacion("ISO 9001", date(2026, 12, 31))
    assert cert._nombre == "ISO 9001"
    assert cert._vencimiento == date(2026, 12, 31)

def test_nombre_vacio_lanza_error():
    """Prueba que crear una certificación con nombre vacío lanza un error."""
    with pytest.raises(DatosInvalidos, match="nombre de la certificación"):
        Certificacion("", date(2026, 12, 31))


def test_vencimiento_que_no_es_date_lanza_error():
    """Prueba que crear una certificación con vencimiento que no es date lanza un error."""
    with pytest.raises(DatosInvalidos, match="vencimiento"):
        Certificacion("ISO 9001", "2026-12-31")  # Vencimiento como string en lugar de date
