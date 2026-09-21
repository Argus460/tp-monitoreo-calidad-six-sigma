import pytest
from sistema_calidad import Defecto

def test_creacion_defecto():
    defect = Defecto(
        "tipo",
        'descripcion de defecto',
        3,
        temperatura=4,
        abolladuras = 12
    )

    assert defect._tipo == 'tipo'
    assert defect._descripcion == 'descripcion de defecto'
    assert defect._gravedad == 3
    assert defect._datos_observacion == {'temperatura': 4,
            'abolladuras': 12}

'''
Falta validar los metodos que todavia no estan hechos
    def gravedad(self):
    def es_critico(self):
    def tipo(self):
    def descripcion(self):
    def datos_observacion(self):
'''
