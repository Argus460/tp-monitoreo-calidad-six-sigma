import pytest
from datetime import date
from sistema_calidad import Profesional, DatosInvalidos, Certificacion


@pytest.fixture(autouse=True)
def reset_Profesional_estado():
    Profesional.contador = 0

def test_creacion_profesional():
    profesional = Profesional(
        'nombre'
    )

    assert profesional.get_id() == 'Prof0'
    assert profesional.get_nombre() == 'nombre'


def test_ids_autoincrementales():
    primero = Profesional('Ana')
    segundo = Profesional('Luis')

    assert primero.get_id() == 'Prof0'
    assert segundo.get_id() == 'Prof1'

def test_nombre_invalido():
    with pytest.raises(DatosInvalidos):
        Profesional('')

def test_nombre_solo_espacios():
    with pytest.raises(DatosInvalidos):
        Profesional('   ')

def test_nombre_no_texto():
    with pytest.raises(DatosInvalidos):
        Profesional(123)

def test_agregar_algo_que_no_es_certificacion_se_rechaza():
    p = Profesional("Ana")
    with pytest.raises(DatosInvalidos):
        p.agregar_certificacion("metrologia")

def test_no_tiene_una_certificacion_que_nunca_agregó():
    p = Profesional("Ana")
    assert not p.tiene_certificacion_vigente("metrologia", date(2026, 10, 1))

def test_certificacion_vigente_el_dia_exacto_del_vencimiento():
    p = Profesional("Ana")
    p.agregar_certificacion(Certificacion("metrologia", date(2026, 10, 1)))
    assert p.tiene_certificacion_vigente("metrologia", date(2026, 10, 1))

def test_renovar_certificacion_reemplaza_la_anterior():
    p = Profesional("Ana")
    p.agregar_certificacion(Certificacion("metrologia", date(2026, 1, 1)))
    assert not p.tiene_certificacion_vigente("metrologia", date(2026, 6, 1))
    p.agregar_certificacion(Certificacion("metrologia", date(2027, 1, 1)))
    assert p.tiene_certificacion_vigente("metrologia", date(2026, 6, 1))