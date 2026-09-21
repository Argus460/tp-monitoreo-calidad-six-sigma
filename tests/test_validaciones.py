import pytest
from sistema_calidad import Validar, DatosInvalidos
from datetime import datetime


@pytest.fixture(autouse=True)
def reset_Validar_estado():
    """
    Se ejecuta automaticamente. 
    Se usa para resetear los atributos de clase
    compartidos por todos los objetos.
    """
    pass

def test_texto_no_vacio():
    with pytest.raises(DatosInvalidos):
        Validar.texto_no_vacio("", 'nombre')

def test_entero_positivo():
    with pytest.raises(DatosInvalidos):
        Validar.entero_positivo(-3, 'nombre')
        Validar.entero_positivo(3.5, 'nombre')

def test_entero_en_rango():
    with pytest.raises(DatosInvalidos):
        Validar.entero_en_rango(2,4,7, 'nombre')
        Validar.entero_en_rango(4.7,4,7, 'nombre')

def test_numero_positivo():
    with pytest.raises(DatosInvalidos):
        Validar.numero_positivo(True, 'nombre')
        Validar.numero_positivo(None, 'nombre')
        Validar.numero_positivo('10', 'nombre')
        Validar.numero_positivo([10], 'nombre')
        Validar.numero_positivo(-5, 'nombre')

def test_fecha():
    with pytest.raises(DatosInvalidos):
        Validar.fecha(datetime(2025, 12, 3, 8, 45), 'nombre')
        Validar.fecha('21/09/2026 15:30', 'nombre')

def test_es_entero():
    resultado = Validar._es_entero(True)
    assert resultado == False
    resultado_2 = Validar._es_entero(3.5)
    assert resultado_2 == False
    resultado_3 = Validar._es_entero('hola')
    assert resultado_3 == False
    resultado_4 = Validar._es_entero(4)
    assert resultado_4 == True