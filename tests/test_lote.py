import pytest

from sistema_calidad import Lote, DatosInvalidos


@pytest.fixture(autouse=True)
def reset_lote_state():
    Lote.contador = 0


def test_creacion_lote_valido():
    """Prueba que un lote con cantidad fabricada válida se crea sin errores."""
    lote = Lote(1000)
    assert isinstance(lote, Lote)


def test_cantidad_fabricada_cero_lanza_error():
    """Prueba que un lote con cantidad fabricada 0 lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(0)


def test_cantidad_fabricada_negativa_lanza_error():
    """Prueba que un lote con cantidad fabricada negativa lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(-100)


def test_cantidad_fabricada_float_lanza_error():
    """Prueba que la cantidad fabricada tiene que ser un entero, no un float."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(100.5)


def test_cantidad_fabricada_bool_lanza_error():
    """Prueba que True se rechaza aunque en Python bool sea subclase de int."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(True)


def test_cantidad_fabricada_texto_lanza_error():
    """Prueba que cantidad fabricada como string lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote("1000")  # Cantidad como string en lugar de int
