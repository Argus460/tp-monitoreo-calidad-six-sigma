import pytest
from sistema_calidad import Profesional, DatosInvalidos

@pytest.fixture(autouse=True)
def reset_Profesional_estado():
    Profesional.contador = 0

def test_creacion_profesional():
    profesional = Profesional(
        'nombre'
    )

    assert profesional._id == 'Prof0'
    assert profesional._nombre == 'nombre'
    assert profesional._certificaciones == {}

def test_nombre_invalido():
    with pytest.raises(DatosInvalidos):
        Profesional('')

def test_nombre_solo_espacios():
    with pytest.raises(DatosInvalidos):
        Profesional('   ')

def test_nombre_no_texto():
    with pytest.raises(DatosInvalidos):
        Profesional(123)


'''
Falta  
    def agregar_certificacion(self, cert):
    def tiene_certificacion_vigente(self, nombre, fecha):
    def id(self):
    def nombre(self):
'''
