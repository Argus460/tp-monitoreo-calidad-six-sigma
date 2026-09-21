import pytest

from sistema_calidad import Muestra, DatosInvalidos


@pytest.fixture(autouse=True)
def reset_muestra_state():
    Muestra.contador = 0


def test_creacion_muestra_valida():
    """Prueba que una muestra con unidades válidas se crea sin errores."""
    muestra = Muestra(10)
    assert isinstance(muestra, Muestra)


def test_unidades_cero_lanza_error():
    """Prueba que una muestra con 0 unidades lanza un error."""
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(0)


def test_unidades_negativas_lanza_error():
    """Prueba que una muestra con unidades negativas lanza un error."""
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(-5)


def test_unidades_float_lanza_error():
    """Prueba que las unidades tienen que ser un entero, no un float."""
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(2.5)


def test_unidades_bool_lanza_error():
    """Prueba que True se rechaza aunque en Python bool sea subclase de int."""
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(True)


def test_unidades_texto_lanza_error():
    """Prueba que unidades como string lanza un error."""
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra("10")  # Unidades como string en lugar de int
