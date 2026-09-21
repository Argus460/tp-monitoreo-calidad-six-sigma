import pytest
from sistema_calidad import Validar

@pytest.fixture(autouse=True)
def reset_Validar_estado():
    """
    Se ejecuta automaticamente. 
    Se usa para resetear los atributos de clase
    compartidos por todos los objetos.
    """

def test_texto_no_vacio():
    with pytest.raises(DatosInvalidos):
        Validar.texto_no_vacio("")


