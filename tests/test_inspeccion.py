import pytest
from datetime import date, datetime

from sistema_calidad import (Inspeccion, Muestra, Profesional, Equipo,
                             Procedimiento, ProcedimientoVisual, DatosInvalidos)


@pytest.fixture(autouse=True)
def reset_inspeccion_state():
    Inspeccion.contador = 0
    Muestra.contador = 0
    Profesional.contador = 0
    Equipo.contador = 0
    Procedimiento.contador = 0


def crear_participantes():
    """Arma los cuatro objetos que necesita una inspección.
    Se usa ProcedimientoVisual porque el __init__ de ProcedimientoDimensional
    todavía está pendiente de corrección."""
    muestra = Muestra(10)
    profesional = Profesional("Ana")
    equipo = Equipo("visual", date(2026, 3, 1))
    procedimiento = ProcedimientoVisual(5, "visual", None, ("soldadura",))
    return muestra, profesional, equipo, procedimiento


def test_creacion_inspeccion_valida():
    """Prueba que una inspección con datos válidos se crea sin errores."""
    muestra, profesional, equipo, procedimiento = crear_participantes()
    insp = Inspeccion(muestra, profesional, equipo, procedimiento, date(2026, 5, 1))
    assert isinstance(insp, Inspeccion)


def test_fecha_que_no_es_date_lanza_error():
    """Prueba que una fecha de inspección como string lanza un error."""
    muestra, profesional, equipo, procedimiento = crear_participantes()
    with pytest.raises(DatosInvalidos, match="fecha de inspección"):
        Inspeccion(muestra, profesional, equipo, procedimiento, "2026-05-01")


def test_fecha_datetime_lanza_error():
    """Prueba que un datetime se rechaza aunque sea subclase de date."""
    muestra, profesional, equipo, procedimiento = crear_participantes()
    with pytest.raises(DatosInvalidos, match="fecha de inspección"):
        Inspeccion(muestra, profesional, equipo, procedimiento,
                   datetime(2026, 5, 1, 9, 0))

# PENDIENTE: cuando esté la validación de que la muestra tenga lote
# (y lote.agregar_muestra), el caso válido va a tener que agregar la muestra
# a un Lote antes de crear la inspección, y se suma un test de
# "muestra sin lote lanza DatosInvalidos".
