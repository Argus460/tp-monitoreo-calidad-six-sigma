import pytest
from sistema_calidad import Profesional, DatosInvalidos

@pytest.fixture(autouse=True)
def reset_Profesional_estado():
    Profesional.contador = 0

def test_creacion_profesional():
    profesional = Profesional(
        'nombre'
    )

    assert profesional.get_id() == 'Prof0'
    assert profesional.get_nombre() == 'nombre'
    assert profesional.get_certificaciones() == {}

def test_nombre_invalido():
    with pytest.raises(DatosInvalidos):
        Profesional('')

def test_nombre_solo_espacios():
    with pytest.raises(DatosInvalidos):
        Profesional('   ')

def test_nombre_no_texto():
    with pytest.raises(DatosInvalidos):
        Profesional(123)
