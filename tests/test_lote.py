"""Tests de Lote.

Cómo se cierran las muestras en estos tests: con las transiciones de
Muestra llamadas a mano (marcar_en_inspeccion, registrar_defecto, cerrar),
a través de la función cerrar_muestra(). No se usa Inspeccion a propósito:
así estos tests prueban SOLO a Lote, y no fallan por un error en otra
clase. El circuito completo con Inspeccion se prueba en test_inspeccion.py.

Se ejecutan desde la raíz del proyecto con:  py -m pytest -v
"""

import pytest

from sistema_calidad import (Lote, Muestra, Reporte, Profesional, Equipo,
                             Procedimiento, Inspeccion,
                             ProcedimientoDimensional, ProcedimientoVisual,
                             EstadoLote, EstadoMuestra,
                             DatosInvalidos, TransicionIlegal)


@pytest.fixture(autouse=True)
def reset_contadores():
    """Vuelve todos los contadores a 0 antes de cada test, para poder
    esperar ids exactos como 'Lot0' o 'Mue0'."""
    Lote.contador = 0
    Muestra.contador = 0
    Reporte.contador = 0
    Profesional.contador = 0
    Equipo.contador = 0
    Procedimiento.contador = 0
    Inspeccion.contador = 0


# =====================================================================
# Funciones auxiliares
# =====================================================================


def cerrar_muestra(muestra, gravedades, limite=10, tipo="visual"):
    """Cierra una muestra a mano con un defecto por cada gravedad.

    Con el límite por defecto (10) la muestra queda CONFORME salvo que
    haya un 5. Para que quede NO_CONFORME alcanza con gravedades=[5]."""
    if tipo == "visual":
        muestra.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
        for gravedad in gravedades:
            muestra.registrar_defecto("visual", "defecto de prueba", gravedad,
                                      zona_afectada="cara", patron="raya")
    else:
        muestra.marcar_en_inspeccion(ProcedimientoDimensional.CAMPOS_OBSERVACION)
        for gravedad in gravedades:
            muestra.registrar_defecto("dimensional", "defecto de prueba",
                                      gravedad, valor_medido_mm=10.3,
                                      nominal_mm=10.0, tolerancia_mm=0.1)
    muestra.cerrar(limite)


def agregar_conforme(lote):
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    cerrar_muestra(muestra, [])
    return muestra


def agregar_no_conforme(lote):
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    cerrar_muestra(muestra, [5])
    return muestra


def lote_cerrado(total, no_conformes):
    """Un lote con 'total' muestras cerradas, de las cuales
    'no_conformes' quedaron NO_CONFORME."""
    lote = Lote(1000)
    for i in range(total):
        if i < no_conformes:
            agregar_no_conforme(lote)
        else:
            agregar_conforme(lote)
    return lote


# =====================================================================
# Creación
# =====================================================================


def test_creacion_lote_valido():
    """Prueba que un lote con cantidad fabricada válida se crea sin errores."""
    lote = Lote(1000)
    assert isinstance(lote, Lote)


def test_cantidad_fabricada_cero_lanza_error():
    """Prueba que un lote con cantidad fabricada 0 lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(0)


def test_cantidad_fabricada_negativa_lanza_error():
    """Prueba que un lote con cantidad fabricada negativa lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(-100)


def test_cantidad_fabricada_float_lanza_error():
    """Prueba que la cantidad fabricada tiene que ser un entero, no un float."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(100.5)


def test_cantidad_fabricada_bool_lanza_error():
    """Prueba que True se rechaza aunque en Python bool sea subclase de int."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote(True)


def test_cantidad_fabricada_texto_lanza_error():
    """Prueba que cantidad fabricada como string lanza un error."""
    with pytest.raises(DatosInvalidos, match="cantidad_fabricada"):
        Lote("1000")  # Cantidad como string en lugar de int


def test_lote_nuevo_nace_abierto_y_sin_muestras():
    """Un lote recién creado está ABIERTO, sin muestras ni unidades."""
    lote = Lote(1000)
    assert lote.get_id() == "Lot0"
    assert lote.get_cantidad_fabricada() == 1000
    assert lote.get_estado() is EstadoLote.ABIERTO
    assert lote.muestras() == []
    assert lote.unidades_asignadas() == 0


def test_ids_autoincrementales():
    """Cada lote nuevo toma el siguiente número del contador."""
    assert Lote(10).get_id() == "Lot0"
    assert Lote(10).get_id() == "Lot1"


def test_lote_invalido_no_consume_id():
    """Si el constructor falla, el contador no avanza."""
    with pytest.raises(DatosInvalidos):
        Lote(0)
    assert Lote(10).get_id() == "Lot0"


def test_str_muestra_id_y_estado():
    """__str__ incluye el id y el estado del lote."""
    texto = str(Lote(1000))
    assert "Lot0" in texto
    assert "ABIERTO" in texto


# =====================================================================
# agregar_muestra
# =====================================================================


def test_agregar_muestra_la_incorpora_y_le_asigna_el_lote():
    """La muestra queda en el lote y el lote queda en la muestra."""
    lote = Lote(100)
    muestra = Muestra(10)
    lote.agregar_muestra(muestra)
    assert lote.muestras() == [muestra]
    assert muestra.get_lote() is lote


def test_unidades_asignadas_suma_todas_las_muestras():
    lote = Lote(100)
    lote.agregar_muestra(Muestra(10))
    lote.agregar_muestra(Muestra(25))
    assert lote.unidades_asignadas() == 35


def test_agregar_justo_hasta_la_cantidad_fabricada_se_permite():
    """Llegar exactamente a la cantidad fabricada es válido."""
    lote = Lote(100)
    lote.agregar_muestra(Muestra(60))
    lote.agregar_muestra(Muestra(40))
    assert lote.unidades_asignadas() == 100


def test_agregar_muestra_que_excede_lo_fabricado_lanza_error():
    lote = Lote(100)
    lote.agregar_muestra(Muestra(60))
    with pytest.raises(DatosInvalidos, match="solo se fabricaron"):
        lote.agregar_muestra(Muestra(41))


def test_muestra_rechazada_por_exceso_no_queda_a_medio_agregar():
    """Un rechazo no deja la muestra en el lote ni el lote en la muestra."""
    lote = Lote(100)
    lote.agregar_muestra(Muestra(60))
    grande = Muestra(41)
    with pytest.raises(DatosInvalidos):
        lote.agregar_muestra(grande)
    assert grande.get_lote() is None
    assert len(lote.muestras()) == 1
    assert lote.unidades_asignadas() == 60


def test_agregar_algo_que_no_es_muestra_lanza_error():
    lote = Lote(100)
    with pytest.raises(DatosInvalidos, match="Solo se pueden agregar muestras"):
        lote.agregar_muestra("Mue0")


def test_agregar_la_misma_muestra_dos_veces_lanza_error():
    lote = Lote(100)
    muestra = Muestra(10)
    lote.agregar_muestra(muestra)
    with pytest.raises(TransicionIlegal, match="ya pertenece a un lote"):
        lote.agregar_muestra(muestra)
    assert len(lote.muestras()) == 1


def test_una_muestra_no_puede_moverse_a_otro_lote():
    """Regla 2: la muestra sigue en su lote original y el otro queda vacío."""
    lote_a = Lote(100)
    lote_b = Lote(100)
    muestra = Muestra(10)
    lote_a.agregar_muestra(muestra)
    with pytest.raises(TransicionIlegal, match="ya pertenece a un lote"):
        lote_b.agregar_muestra(muestra)
    assert muestra.get_lote() is lote_a
    assert lote_b.muestras() == []


def test_id_de_muestra_repetido_en_el_lote_lanza_error():
    """Dos muestras distintas con el mismo id. Con ids autoincrementales
    solo pasa si se reinicia el contador, que es lo que hace este test."""
    lote = Lote(100)
    lote.agregar_muestra(Muestra(10))       # Mue0
    Muestra.contador = 0
    repetida = Muestra(10)                  # otra vez Mue0
    with pytest.raises(DatosInvalidos, match="ya tiene una muestra con id"):
        lote.agregar_muestra(repetida)
    assert repetida.get_lote() is None


def test_no_se_agregan_muestras_a_un_lote_decidido():
    lote = Lote(100)
    agregar_conforme(lote)
    lote.decidir()
    with pytest.raises(TransicionIlegal, match="ya fue decidido"):
        lote.agregar_muestra(Muestra(1))


def test_muestras_devuelve_una_copia():
    """Modificar la lista devuelta no cambia al lote."""
    lote = Lote(100)
    lote.agregar_muestra(Muestra(10))
    copia = lote.muestras()
    copia.clear()
    assert len(lote.muestras()) == 1


# =====================================================================
# todas_cerradas
# =====================================================================


def test_todas_cerradas_en_lote_vacio_es_true():
    """Verdadero de forma trivial; por eso decidir() chequea aparte que
    haya muestras."""
    assert Lote(100).todas_cerradas() is True


def test_todas_cerradas_con_una_pendiente_es_false():
    lote = Lote(100)
    agregar_conforme(lote)
    lote.agregar_muestra(Muestra(1))
    assert lote.todas_cerradas() is False


def test_todas_cerradas_con_una_en_inspeccion_es_false():
    lote = Lote(100)
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    muestra.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    assert lote.todas_cerradas() is False


def test_todas_cerradas_con_conformes_y_no_conformes_es_true():
    lote = Lote(100)
    agregar_conforme(lote)
    agregar_no_conforme(lote)
    assert lote.todas_cerradas() is True


# =====================================================================
# porcentaje_no_conformes
# =====================================================================


def test_porcentaje_en_lote_vacio_lanza_error():
    with pytest.raises(DatosInvalidos, match="no tiene muestras"):
        Lote(100).porcentaje_no_conformes()


def test_porcentaje_cuenta_muestras_no_conformes_sobre_el_total():
    assert lote_cerrado(4, 1).porcentaje_no_conformes() == 25.0


def test_porcentaje_sin_no_conformes_es_cero():
    assert lote_cerrado(3, 0).porcentaje_no_conformes() == 0.0


def test_porcentaje_no_se_redondea():
    """1 de 3 da 33.333..., no 33 ni 33.33."""
    assert round(lote_cerrado(3, 1).porcentaje_no_conformes(), 6) == 33.333333


def test_porcentaje_preliminar_con_muestras_abiertas():
    """Se puede pedir antes de decidir: la pendiente cuenta en el total,
    pero no como no conforme."""
    lote = Lote(100)
    agregar_no_conforme(lote)
    lote.agregar_muestra(Muestra(1))
    assert lote.porcentaje_no_conformes() == 50.0


def test_porcentaje_no_cambia_el_estado_del_lote():
    """Regla 12: es una consulta, se puede llamar muchas veces."""
    lote = lote_cerrado(4, 1)
    lote.porcentaje_no_conformes()
    lote.porcentaje_no_conformes()
    assert lote.get_estado() is EstadoLote.ABIERTO


# =====================================================================
# contar_criticos
# =====================================================================


def test_contar_criticos_en_lote_vacio_es_cero():
    assert Lote(100).contar_criticos() == 0


def test_contar_criticos_cuenta_solo_gravedad_5():
    lote = Lote(100)
    m1 = Muestra(1)
    m2 = Muestra(1)
    lote.agregar_muestra(m1)
    lote.agregar_muestra(m2)
    cerrar_muestra(m1, [5, 2, 4])
    cerrar_muestra(m2, [5])
    assert lote.contar_criticos() == 2


def test_contar_criticos_ignora_muestras_sin_cerrar():
    """Una muestra EN_INSPECCION con un defecto crítico no cuenta todavía."""
    lote = Lote(100)
    agregar_no_conforme(lote)
    abierta = Muestra(1)
    lote.agregar_muestra(abierta)
    abierta.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    abierta.registrar_defecto("visual", "defecto de prueba", 5,
                              zona_afectada="borde", patron="fisura")
    assert lote.contar_criticos() == 1


def test_contar_criticos_no_tiene_efectos_secundarios():
    """Regla 12: no cambia muestras, defectos ni estado del lote."""
    lote = Lote(100)
    muestra = agregar_no_conforme(lote)
    lote.contar_criticos()
    lote.contar_criticos()
    assert lote.get_estado() is EstadoLote.ABIERTO
    assert muestra.get_estado() is EstadoMuestra.NO_CONFORME
    assert len(muestra.defectos()) == 1


# =====================================================================
# contar_defectos_por_tipo
# =====================================================================


def test_contar_por_tipo_en_lote_vacio_es_diccionario_vacio():
    assert Lote(100).contar_defectos_por_tipo() == {}


def test_contar_por_tipo_agrupa_por_tipo():
    lote = Lote(100)
    m1 = Muestra(1)
    m2 = Muestra(1)
    lote.agregar_muestra(m1)
    lote.agregar_muestra(m2)
    cerrar_muestra(m1, [2, 3], tipo="visual")
    cerrar_muestra(m2, [4], tipo="dimensional")
    assert lote.contar_defectos_por_tipo() == {"visual": 2, "dimensional": 1}


def test_contar_por_tipo_no_incluye_tipos_que_no_aparecieron():
    lote = Lote(100)
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    cerrar_muestra(muestra, [2], tipo="visual")
    assert lote.contar_defectos_por_tipo() == {"visual": 1}


def test_contar_por_tipo_incluye_defectos_de_muestras_conformes():
    """Una muestra conforme puede tener defectos, y cuentan igual."""
    lote = Lote(100)
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    cerrar_muestra(muestra, [2])
    assert muestra.get_estado() is EstadoMuestra.CONFORME
    assert lote.contar_defectos_por_tipo() == {"visual": 1}


def test_contar_por_tipo_ignora_muestras_sin_cerrar():
    lote = Lote(100)
    abierta = Muestra(1)
    lote.agregar_muestra(abierta)
    abierta.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    abierta.registrar_defecto("visual", "defecto de prueba", 2,
                              zona_afectada="cara", patron="raya")
    assert lote.contar_defectos_por_tipo() == {}


def test_contar_por_tipo_devuelve_un_diccionario_nuevo():
    """Modificar el resultado no afecta a la próxima consulta."""
    lote = Lote(100)
    agregar_no_conforme(lote)
    conteo = lote.contar_defectos_por_tipo()
    conteo["visual"] = 99
    assert lote.contar_defectos_por_tipo() == {"visual": 1}


# =====================================================================
# decidir
# =====================================================================


def test_decidir_lote_vacio_lanza_error():
    lote = Lote(100)
    with pytest.raises(DatosInvalidos, match="no tiene muestras"):
        lote.decidir()
    assert lote.get_estado() is EstadoLote.ABIERTO


def test_decidir_lote_incompleto_lanza_error():
    lote = Lote(100)
    agregar_conforme(lote)
    lote.agregar_muestra(Muestra(1))
    with pytest.raises(TransicionIlegal, match="sin cerrar"):
        lote.decidir()
    assert lote.get_estado() is EstadoLote.ABIERTO


def test_decidir_dos_veces_lanza_error():
    """Regla 11: la decisión es final."""
    lote = lote_cerrado(10, 5)
    lote.decidir()
    with pytest.raises(TransicionIlegal, match="ya fue decidido"):
        lote.decidir()
    assert lote.get_estado() is EstadoLote.RECHAZADO


def test_decidir_devuelve_el_estado_y_lo_guarda():
    lote = lote_cerrado(2, 0)
    resultado = lote.decidir()
    assert resultado is EstadoLote.APROBADO
    assert lote.get_estado() is resultado


def test_decidir_sin_no_conformes_aprueba():
    assert lote_cerrado(5, 0).decidir() is EstadoLote.APROBADO


def test_decidir_exactamente_5_por_ciento_aprueba():
    """1 de 20 = 5 %: el rechazo exige superar el umbral."""
    lote = lote_cerrado(20, 1)
    assert lote.porcentaje_no_conformes() == 5.0
    assert lote.decidir() is EstadoLote.APROBADO


def test_decidir_por_encima_del_5_por_ciento_rechaza():
    """Ejemplo de la consigna: 3 de 50 = 6 %."""
    lote = lote_cerrado(50, 3)
    assert lote.porcentaje_no_conformes() == 6.0
    assert lote.decidir() is EstadoLote.RECHAZADO


def test_decidir_por_debajo_del_5_por_ciento_aprueba():
    """Ejemplo de la consigna: 2 de 50 = 4 %."""
    lote = lote_cerrado(50, 2)
    assert lote.porcentaje_no_conformes() == 4.0
    assert lote.decidir() is EstadoLote.APROBADO


def test_decidir_todas_no_conformes_rechaza():
    assert lote_cerrado(3, 3).decidir() is EstadoLote.RECHAZADO


def test_decidir_no_modifica_las_muestras():
    """Decidir cambia el lote, no sus muestras ni sus defectos."""
    lote = Lote(100)
    muestra = agregar_no_conforme(lote)
    lote.decidir()
    assert muestra.get_estado() is EstadoMuestra.NO_CONFORME
    assert len(muestra.defectos()) == 1