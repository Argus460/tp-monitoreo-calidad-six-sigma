import pytest
from sistema_calidad import Defecto

def test_creacion_defecto():
    defect = Defecto(
        'tipo',
        'descripcion de defecto',
        3,
        {'datos', 'defecto grave!'}
    )

    assert defect.tipo == 'tipo'
    assert defect.descripcion == 'descripcion de defecto'
    assert defect.gravedad == 3
    assert defect.datos_observacion == {'datos', 'defecto grave!'}

'''
Falta validar los metodos que todavia no estan hechos
    def gravedad(self):
    def es_critico(self):
    def tipo(self):
    def descripcion(self):
    def datos_observacion(self):
'''
