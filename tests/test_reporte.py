import pytest

from datetime import date, datetime

from sistema_calidad import (Reporte, Muestra, Lote, Profesional, Defecto,
                             ProcedimientoVisual, DatosInvalidos)


HOY = date(2026, 5, 1)


@pytest.fixture(autouse=True)
def reset_contadores():
    Reporte.contador = 0
    Lote.contador = 0
    Muestra.contador = 0
    Profesional.contador = 0


def crear_datos_reporte():
    """Arma lo que necesita un reporte válido: una muestra que pertenece a
    un lote y quedó NO_CONFORME (un defecto crítico), cerrada a mano sin
    pasar por Inspeccion, como en test_lote.py."""
    lote = Lote(100)
    muestra = Muestra(10)
    lote.agregar_muestra(muestra)
    muestra.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    muestra.registrar_defecto("visual", "fisura en el borde", 5,
                              zona_afectada="borde", patron="fisura")
    muestra.cerrar(5)
    return muestra, lote, Profesional("Ana"), muestra.defectos()


# =====================================================================
# Creación válida
# =====================================================================


def test_creacion_reporte_valido():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    reporte = Reporte(muestra, lote, profesional, HOY, defectos)

    assert reporte.get_id() == "Rep0"
    assert reporte.get_muestra() is muestra
    assert reporte.get_lote() is lote
    assert reporte.get_profesional() is profesional
    assert reporte.get_fecha() == HOY
    assert reporte.causas() == defectos


def test_causas_es_una_tupla():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    reporte = Reporte(muestra, lote, profesional, HOY, defectos)
    assert isinstance(reporte.causas(), tuple)


def test_resumen_incluye_los_datos_y_las_causas():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    texto = Reporte(muestra, lote, profesional, HOY, defectos).resumen()
    assert "Rep0" in texto
    assert "Mue0" in texto
    assert "Lot0" in texto
    assert "Ana" in texto
    assert "fisura en el borde" in texto


def test_str_delega_en_resumen():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    reporte = Reporte(muestra, lote, profesional, HOY, defectos)
    assert str(reporte) == reporte.resumen()


# =====================================================================
# Validaciones (una regla rota por test)
# =====================================================================


def test_fecha_que_no_es_date_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos, match="fecha del reporte"):
        Reporte(muestra, lote, profesional, "2026-05-01", defectos)


def test_fecha_datetime_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos, match="fecha del reporte"):
        Reporte(muestra, lote, profesional, datetime(2026, 5, 1, 10, 30), defectos)


def test_muestra_de_otro_lote_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos, match="no pertenece al lote"):
        Reporte(muestra, Lote(100), profesional, HOY, defectos)


def test_muestra_conforme_no_genera_reporte():
    lote = Lote(100)
    muestra = Muestra(10)
    lote.agregar_muestra(muestra)
    muestra.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    muestra.cerrar(5)                                    # sin defectos -> CONFORME
    with pytest.raises(DatosInvalidos, match="NO_CONFORME"):
        Reporte(muestra, lote, Profesional("Ana"), HOY, muestra.defectos())


def test_defectos_que_no_es_tupla_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos, match="tupla"):
        Reporte(muestra, lote, profesional, HOY, list(defectos))


def test_defectos_vacios_lanza_error():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos, match="al menos un defecto"):
        Reporte(muestra, lote, profesional, HOY, ())


def test_defectos_ajenos_a_la_muestra_lanza_error():
    """Un defecto igualito, pero creado aparte, no es de la muestra."""
    muestra, lote, profesional, defectos = crear_datos_reporte()
    ajeno = Defecto("visual", "fisura en el borde", 5,
                    zona_afectada="borde", patron="fisura")
    with pytest.raises(DatosInvalidos, match="no son los de la muestra"):
        Reporte(muestra, lote, profesional, HOY, (ajeno,))


def test_reporte_invalido_no_consume_id():
    muestra, lote, profesional, defectos = crear_datos_reporte()
    with pytest.raises(DatosInvalidos):
        Reporte(muestra, lote, profesional, "2026-05-01", defectos)
    assert Reporte(muestra, lote, profesional, HOY, defectos).get_id() == "Rep0"