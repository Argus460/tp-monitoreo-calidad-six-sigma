import pytest

from datetime import date, datetime

from sistema_calidad import Reporte, Muestra, Lote, Profesional, Defecto, DatosInvalidos


@pytest.fixture(autouse=True)
def reset_reporte_state():
    Reporte.contador = 0


def crear_datos_reporte():
    muestra = Muestra(10)
    lote = Lote(100)
    profesional = Profesional('nombre')
    defecto = Defecto(
        'tipo',
        'descripcion de defecto',
        3
    )
    return muestra, lote, profesional, (defecto,)


def test_creacion_reporte_valido():
    muestra, lote, profesional, defectos = crear_datos_reporte()

    reporte = Reporte(muestra, lote, profesional, date(2026, 5, 1), defectos)

    assert isinstance(reporte, Reporte)
    assert reporte._id == 'Rep0'
    assert reporte._muestra == muestra
    assert reporte._lote == lote
    assert reporte._profesional == profesional
    assert reporte._fecha == date(2026, 5, 1)
    assert reporte._defectos == defectos


def test_fecha_que_no_es_date_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()

    with pytest.raises(DatosInvalidos):
        Reporte(muestra, lote, profesional, '2026-05-01', defectos)


def test_fecha_datetime_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()

    with pytest.raises(DatosInvalidos):
        Reporte(muestra, lote, profesional,
            datetime(2026, 5, 1, 10, 30),
            defectos
        )


def test_defectos_que_no_es_tupla_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()

    with pytest.raises(DatosInvalidos):
        Reporte(muestra, lote, profesional,
            date(2026, 5, 1),
            list(defectos)
        )


def test_defectos_vacios_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()

    with pytest.raises(DatosInvalidos):
        Reporte(muestra, lote, profesional,
            date(2026, 5, 1),
            ()
        )


'''
Falta
    validar que muestra.lote() sea el lote recibido
    validar que la muestra sea NO_CONFORME

    def causas(self):
    def resumen(self):
    def id(self):
    def fecha(self):
    def muestra(self):
    def lote(self):
    def profesional(self):
    def __str__(self):
'''