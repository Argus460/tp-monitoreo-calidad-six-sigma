"""Tests de Agenda: programar y procesar inspecciones en orden de llegada."""

from datetime import date

import pytest

from sistema_calidad import (Agenda, Certificacion, DatosInvalidos, Equipo,
                             EstadoMuestra, Inspeccion, Lote, Muestra,
                             Procedimiento, ProcedimientoDimensional,
                             ProcedimientoVisual, Profesional, Registro,
                             Reporte, TransicionIlegal)

HOY = date(2026, 9, 23)


@pytest.fixture(autouse=True)
def reiniciar_contadores():
    for clase in (Lote, Muestra, Profesional, Equipo, Procedimiento,
                  Inspeccion, Reporte):
        clase.contador = 0


# --- armado del escenario --------------------------------------------

def escenario(cantidad_muestras=3):
    """Un lote con muestras, una profesional certificada, un calibre y una
    cámara calibrados, y los dos procedimientos. Devuelve un diccionario
    para que cada test tome solo lo que necesita."""
    lote = Lote(1000)
    muestras = []
    for _ in range(cantidad_muestras):
        muestra = Muestra(10)
        lote.agregar_muestra(muestra)
        muestras.append(muestra)
    ana = Profesional("Ana")
    ana.agregar_certificacion(Certificacion("Metrologia", date(2027, 3, 1)))
    return {
        "lote": lote,
        "muestras": muestras,
        "ana": ana,
        "calibre": Equipo("calibre", date(2026, 8, 1)),
        "camara": Equipo("camara", date(2026, 9, 1)),
        "dimensional": ProcedimientoDimensional(5, "calibre", "Metrologia",
                                                nominal_mm=10.0,
                                                tolerancia_mm=0.1),
        "visual": ProcedimientoVisual(4, "camara", None,
                                      zonas_criticas=("borde",)),
    }


def inspeccion_dimensional(e, indice):
    return Inspeccion(e["muestras"][indice], e["ana"], e["calibre"],
                      e["dimensional"], HOY)


def inspeccion_visual(e, indice):
    return Inspeccion(e["muestras"][indice], e["ana"], e["camara"],
                      e["visual"], HOY)


# --- creación --------------------------------------------------------

def test_agenda_sin_registro_lanza_error():
    with pytest.raises(DatosInvalidos, match="necesita un Registro"):
        Agenda("no soy un registro")


def test_agenda_nueva_no_tiene_pendientes():
    agenda = Agenda(Registro())
    assert agenda.cantidad_pendientes() == 0
    assert agenda.pendientes() == []


# --- programar -------------------------------------------------------

def test_programar_algo_que_no_es_inspeccion_lanza_error():
    with pytest.raises(DatosInvalidos, match="Solo se pueden programar"):
        Agenda(Registro()).programar("Insp0", [10.0])


def test_programar_dos_veces_la_misma_inspeccion_lanza_error():
    e = escenario()
    agenda = Agenda(Registro())
    inspeccion = inspeccion_dimensional(e, 0)
    agenda.programar(inspeccion, [10.0])
    with pytest.raises(DatosInvalidos, match="ya está programada"):
        agenda.programar(inspeccion, [10.0])
    assert agenda.cantidad_pendientes() == 1


def test_programar_una_inspeccion_ya_ejecutada_lanza_error():
    e = escenario()
    inspeccion = inspeccion_dimensional(e, 0)
    inspeccion.ejecutar([10.0])
    with pytest.raises(TransicionIlegal, match="ya fue ejecutada"):
        Agenda(Registro()).programar(inspeccion, [10.0])


def test_pendientes_respeta_el_orden_y_no_saca_nada():
    e = escenario()
    agenda = Agenda(Registro())
    agenda.programar(inspeccion_dimensional(e, 0), [10.0])
    agenda.programar(inspeccion_visual(e, 1), [])
    agenda.programar(inspeccion_dimensional(e, 2), [10.0])
    assert agenda.pendientes() == ["Insp0", "Insp1", "Insp2"]
    assert agenda.cantidad_pendientes() == 3
    assert agenda.pendientes() == ["Insp0", "Insp1", "Insp2"]


# --- procesar de a una -----------------------------------------------

def test_procesar_agenda_vacia_lanza_error():
    with pytest.raises(DatosInvalidos, match="No hay inspecciones"):
        Agenda(Registro()).procesar_siguiente()


def test_procesar_siguiente_respeta_el_orden_de_llegada():
    e = escenario()
    agenda = Agenda(Registro())
    primera = inspeccion_dimensional(e, 0)
    segunda = inspeccion_dimensional(e, 1)
    agenda.programar(primera, [10.0])
    agenda.programar(segunda, [10.0])
    agenda.procesar_siguiente()
    assert primera.fue_ejecutada()
    assert not segunda.fue_ejecutada()
    assert agenda.pendientes() == ["Insp1"]


def test_procesar_conforme_registra_la_inspeccion_sin_reporte():
    e = escenario()
    registro = Registro()
    agenda = Agenda(registro)
    inspeccion = inspeccion_dimensional(e, 0)
    agenda.programar(inspeccion, [10.02, 10.35])  # un defecto de gravedad 4
    assert agenda.procesar_siguiente() is None
    assert registro.inspecciones() == [inspeccion]
    assert registro.reportes() == []


def test_procesar_no_conforme_registra_inspeccion_y_reporte():
    e = escenario()
    registro = Registro()
    agenda = Agenda(registro)
    agenda.programar(inspeccion_visual(e, 0),
                     [{"zona_afectada": "borde", "patron": "fisura"}])
    reporte = agenda.procesar_siguiente()
    assert isinstance(reporte, Reporte)
    assert registro.reportes() == [reporte]


def test_inspeccion_fallida_sale_de_la_cola_sin_registrarse():
    e = escenario()
    registro = Registro()
    agenda = Agenda(registro)
    inspeccion = inspeccion_dimensional(e, 0)
    agenda.programar(inspeccion, [10.0, "diez"])
    with pytest.raises(DatosInvalidos):
        agenda.procesar_siguiente()
    assert agenda.cantidad_pendientes() == 0
    assert registro.inspecciones() == []
    assert e["muestras"][0].get_estado() is EstadoMuestra.PENDIENTE


# --- procesar toda la cola -------------------------------------------

def test_procesar_todas_devuelve_el_resumen():
    e = escenario()
    registro = Registro()
    agenda = Agenda(registro)
    agenda.programar(inspeccion_dimensional(e, 0), [10.0])
    agenda.programar(inspeccion_dimensional(e, 1), [10.0, "diez"])
    agenda.programar(inspeccion_visual(e, 2),
                     [{"zona_afectada": "borde", "patron": "fisura"}])
    resumen = agenda.procesar_todas()
    assert resumen == {"completadas": 2, "fallidas": 1,
                       "ids_fallidas": ["Insp1"]}
    assert agenda.cantidad_pendientes() == 0
    assert len(registro.inspecciones()) == 2
    assert len(registro.reportes()) == 1


def test_procesar_todas_sin_pendientes_da_resumen_vacio():
    assert Agenda(Registro()).procesar_todas() == {
        "completadas": 0, "fallidas": 0, "ids_fallidas": []}


def test_una_inspeccion_fallida_se_puede_volver_a_programar():
    e = escenario()
    agenda = Agenda(Registro())
    inspeccion = inspeccion_dimensional(e, 0)
    agenda.programar(inspeccion, [10.0, "diez"])
    agenda.procesar_todas()
    agenda.programar(inspeccion, [10.0, 10.0])  # observaciones corregidas
    assert agenda.procesar_todas()["completadas"] == 1
    assert inspeccion.fue_ejecutada()


def test_un_error_de_requisitos_tambien_cuenta_como_fallida():
    e = escenario()
    agenda = Agenda(Registro())
    # Calibre para un procedimiento visual, que pide cámara -> EquipoNoApto
    agenda.programar(Inspeccion(e["muestras"][0], e["ana"], e["calibre"],
                                e["visual"], HOY), [])
    resumen = agenda.procesar_todas()
    assert resumen["fallidas"] == 1
    assert e["muestras"][0].esta_pendiente()
