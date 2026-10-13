from datetime import date, datetime, timedelta
 
import pytest
 
from sistema_calidad import (Inspeccion, Lote, Muestra, Reporte, Profesional,
                             Certificacion, Equipo, Procedimiento,
                             ProcedimientoDimensional, ProcedimientoVisual,
                             EstadoMuestra, EstadoLote, DatosInvalidos,
                             EquipoNoApto, CertificacionFaltante,
                             TransicionIlegal)
 
 
HOY = date(2026, 9, 23)
UN_DIA = timedelta(days=1)
 
 
@pytest.fixture(autouse=True)
def reset_contadores():
    """Vuelve todos los contadores a 0 antes de cada test."""
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
# Procedimiento dimensional: nominal 10 mm, tolerancia 0.1 mm, límite 5,
# exige la certificación "Metrologia" y un equipo "calibre".
# Gravedades que produce (desvío / tolerancia, redondeado hacia arriba):
#   10.05 -> dentro de tolerancia, sin defecto
#   10.15 -> 1.5 -> gravedad 2
#   10.25 -> 2.5 -> gravedad 3
#   10.60 -> 6.0 -> tope en 5 (crítico)
#
# Procedimiento visual: límite 5, sin certificación, equipo "camara",
# zona crítica "borde" (gravedad 5); cualquier otra zona, gravedad 2.
 
 
def nueva_muestra():
    """Una muestra PENDIENTE que ya pertenece a un lote."""
    lote = Lote(100)
    muestra = Muestra(10)
    lote.agregar_muestra(muestra)
    return muestra
 
 
def profesional_certificado(vencimiento=date(2027, 1, 1)):
    profesional = Profesional("Ana")
    profesional.agregar_certificacion(Certificacion("Metrologia", vencimiento))
    return profesional
 
 
def procedimiento_dimensional():
    return ProcedimientoDimensional(5, "calibre", "Metrologia", 10.0, 0.1)
 
 
def procedimiento_visual():
    return ProcedimientoVisual(5, "camara", None, ("borde",))
 
 
def inspeccion_dimensional(muestra=None, profesional=None, equipo=None):
    """Una inspección dimensional válida. Cada test cambia SOLO el
    participante que quiere romper."""
    if muestra is None:
        muestra = nueva_muestra()
    if profesional is None:
        profesional = profesional_certificado()
    if equipo is None:
        equipo = Equipo("calibre", HOY)
    return Inspeccion(muestra, profesional, equipo,
                      procedimiento_dimensional(), HOY)
 
 
def inspeccion_visual(muestra=None):
    if muestra is None:
        muestra = nueva_muestra()
    return Inspeccion(muestra, Profesional("Beto"), Equipo("camara", HOY),
                      procedimiento_visual(), HOY)
 
 
def hallazgo(zona):
    """Una observación visual en el formato que espera evaluar()."""
    return {"zona_afectada": zona, "patron": "fisura"}
 
 
def esta_intacta(muestra):
    """PENDIENTE y sin defectos: como si la inspección nunca se hubiera
    intentado."""
    return muestra.esta_pendiente() and muestra.defectos() == ()
 
 
# =====================================================================
# Creación
# =====================================================================
 
 
def test_creacion_inspeccion_valida():
    muestra = nueva_muestra()
    profesional = profesional_certificado()
    equipo = Equipo("calibre", HOY)
    procedimiento = procedimiento_dimensional()
    insp = Inspeccion(muestra, profesional, equipo, procedimiento, HOY)
    assert insp.get_id() == "Insp0"
    assert insp.get_muestra() is muestra
    assert insp.get_profesional() is profesional
    assert insp.get_equipo() is equipo
    assert insp.get_procedimiento() is procedimiento
    assert insp.get_fecha() == HOY
 
 
def test_inspeccion_nueva_no_esta_ejecutada_ni_tiene_reporte():
    insp = inspeccion_dimensional()
    assert insp.fue_ejecutada() is False
    assert insp.get_reporte() is None
 
 
def test_crear_la_inspeccion_no_toca_la_muestra():
    """La muestra recién cambia de estado al ejecutar, no al crear."""
    muestra = nueva_muestra()
    inspeccion_dimensional(muestra=muestra)
    assert esta_intacta(muestra)
 
 
def test_ids_consecutivos():
    assert inspeccion_dimensional().get_id() == "Insp0"
    assert inspeccion_dimensional().get_id() == "Insp1"
 
 
def test_fecha_que_no_es_date_lanza_error():
    with pytest.raises(DatosInvalidos, match="fecha de inspección"):
        Inspeccion(nueva_muestra(), profesional_certificado(),
                   Equipo("calibre", HOY), procedimiento_dimensional(),
                   "2026-09-23")
 
 
def test_fecha_datetime_lanza_error():
    """Se rechaza aunque datetime sea subclase de date."""
    with pytest.raises(DatosInvalidos, match="fecha de inspección"):
        Inspeccion(nueva_muestra(), profesional_certificado(),
                   Equipo("calibre", HOY), procedimiento_dimensional(),
                   datetime(2026, 9, 23, 9, 0))
 
 
def test_muestra_sin_lote_lanza_error():
    with pytest.raises(DatosInvalidos, match="no tiene un lote"):
        inspeccion_dimensional(muestra=Muestra(10))
 
 
def test_inspeccion_rechazada_no_consume_id():
    with pytest.raises(DatosInvalidos):
        inspeccion_dimensional(muestra=Muestra(10))
    assert inspeccion_dimensional().get_id() == "Insp0"
 
 
def test_muestra_que_no_es_muestra_lanza_error():
    with pytest.raises(DatosInvalidos, match="Muestra"):
        Inspeccion("Mue0", profesional_certificado(), Equipo("calibre", HOY),
                   procedimiento_dimensional(), HOY)
 
 
def test_profesional_que_no_es_profesional_lanza_error():
    with pytest.raises(DatosInvalidos, match="Profesional"):
        Inspeccion(nueva_muestra(), "Ana", Equipo("calibre", HOY),
                   procedimiento_dimensional(), HOY)
 
 
def test_equipo_que_no_es_equipo_lanza_error():
    with pytest.raises(DatosInvalidos, match="Equipo"):
        Inspeccion(nueva_muestra(), profesional_certificado(), "calibre",
                   procedimiento_dimensional(), HOY)
 
 
def test_procedimiento_que_no_es_procedimiento_lanza_error():
    with pytest.raises(DatosInvalidos, match="Procedimiento"):
        Inspeccion(nueva_muestra(), profesional_certificado(),
                   Equipo("calibre", HOY), "dimensional", HOY)
 
 
# =====================================================================
# Certificación (regla 5)
# =====================================================================
 
 
def test_certificacion_vigente_el_dia_exacto_del_vencimiento():
    """Vigencia inclusiva: vencer HOY todavía permite inspeccionar HOY."""
    insp = inspeccion_dimensional(
        profesional=profesional_certificado(vencimiento=HOY))
    assert insp.ejecutar([10.05]) is None
    assert insp.fue_ejecutada()
 
 
def test_certificacion_vencida_ayer_lanza_error():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(
        muestra=muestra,
        profesional=profesional_certificado(vencimiento=HOY - UN_DIA))
    with pytest.raises(CertificacionFaltante, match="Metrologia"):
        insp.ejecutar([10.05])
    assert esta_intacta(muestra)
    assert insp.fue_ejecutada() is False
 
 
def test_certificacion_ausente_lanza_error():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(muestra=muestra,
                                  profesional=Profesional("Beto"))
    with pytest.raises(CertificacionFaltante, match="Metrologia"):
        insp.ejecutar([10.05])
    assert esta_intacta(muestra)
 
 
def test_certificacion_con_otro_nombre_no_sirve():
    profesional = Profesional("Beto")
    profesional.agregar_certificacion(Certificacion("Soldadura",
                                                    date(2027, 1, 1)))
    insp = inspeccion_dimensional(profesional=profesional)
    with pytest.raises(CertificacionFaltante):
        insp.ejecutar([10.05])
 
 
def test_procedimiento_sin_certificacion_no_la_exige():
    """El visual no exige certificación: un profesional sin ninguna
    puede ejecutarlo."""
    insp = inspeccion_visual()
    assert insp.ejecutar([hallazgo("cara")]) is None
 
 
# =====================================================================
# Equipo (regla 4)
# =====================================================================
 
 
def test_calibracion_exactamente_a_182_dias_es_apta():
    insp = inspeccion_dimensional(
        equipo=Equipo("calibre", HOY - timedelta(days=182)))
    assert insp.ejecutar([10.05]) is None
 
 
def test_calibracion_a_183_dias_lanza_error():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(
        muestra=muestra, equipo=Equipo("calibre", HOY - timedelta(days=183)))
    with pytest.raises(EquipoNoApto, match="no es apto"):
        insp.ejecutar([10.05])
    assert esta_intacta(muestra)
 
 
def test_calibracion_el_mismo_dia_es_apta():
    insp = inspeccion_dimensional(equipo=Equipo("calibre", HOY))
    assert insp.ejecutar([10.05]) is None
 
 
def test_calibracion_con_fecha_futura_lanza_error():
    """El borde superior también cuenta: fecha_calibracion <= fecha."""
    insp = inspeccion_dimensional(equipo=Equipo("calibre", HOY + UN_DIA))
    with pytest.raises(EquipoNoApto):
        insp.ejecutar([10.05])
 
 
def test_equipo_de_categoria_incompatible_lanza_error():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(muestra=muestra,
                                  equipo=Equipo("camara", HOY))
    with pytest.raises(EquipoNoApto, match="calibre"):
        insp.ejecutar([10.05])
    assert esta_intacta(muestra)
 
 
def test_con_dos_requisitos_mal_sale_primero_la_certificacion():
    """El orden de validar_requisitos() está documentado: certificación,
    equipo, estado de la muestra."""
    insp = inspeccion_dimensional(profesional=Profesional("Beto"),
                                  equipo=Equipo("camara", HOY))
    with pytest.raises(CertificacionFaltante):
        insp.ejecutar([10.05])
 
 
# =====================================================================
# Conformidad y reporte (reglas 8 y 10)
# =====================================================================
 
 
def test_muestra_conforme_devuelve_none_y_no_genera_reporte():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(muestra=muestra)
    assert insp.ejecutar([10.05]) is None
    assert muestra.get_estado() is EstadoMuestra.CONFORME
    assert insp.get_reporte() is None
    assert insp.fue_ejecutada()
 
 
def test_sin_observaciones_queda_conforme_y_sin_defectos():
    muestra = nueva_muestra()
    assert inspeccion_dimensional(muestra=muestra).ejecutar([]) is None
    assert muestra.get_estado() is EstadoMuestra.CONFORME
    assert muestra.defectos() == ()
 
 
def test_suma_justo_en_el_limite_queda_conforme():
    """3 + 2 = 5, límite 5: no es estrictamente mayor."""
    muestra = nueva_muestra()
    assert inspeccion_dimensional(muestra=muestra).ejecutar([10.25, 10.15]) is None
    assert muestra.suma_gravedades() == 5
    assert muestra.get_estado() is EstadoMuestra.CONFORME
 
 
def test_suma_por_encima_del_limite_queda_no_conforme():
    """3 + 3 = 6 > 5, sin ningún defecto crítico."""
    muestra = nueva_muestra()
    reporte = inspeccion_dimensional(muestra=muestra).ejecutar([10.25, 10.25])
    assert muestra.suma_gravedades() == 6
    assert muestra.get_estado() is EstadoMuestra.NO_CONFORME
    assert isinstance(reporte, Reporte)
 
 
def test_un_defecto_critico_alcanza_para_no_conforme():
    """Un solo defecto de gravedad 5: la suma (5) no supera el límite (5),
    pero el crítico la hace NO_CONFORME igual."""
    muestra = nueva_muestra()
    reporte = inspeccion_visual(muestra=muestra).ejecutar([hallazgo("borde")])
    assert muestra.suma_gravedades() == 5
    assert muestra.get_estado() is EstadoMuestra.NO_CONFORME
    assert isinstance(reporte, Reporte)
 
 
def test_reporte_tiene_muestra_lote_profesional_fecha_y_causas():
    muestra = nueva_muestra()
    profesional = profesional_certificado()
    insp = inspeccion_dimensional(muestra=muestra, profesional=profesional)
    reporte = insp.ejecutar([10.6])
    assert reporte.get_muestra() is muestra
    assert reporte.get_lote() is muestra.get_lote()
    assert reporte.get_profesional() is profesional
    assert reporte.get_fecha() == HOY
    assert reporte.causas() == muestra.defectos()
    assert len(reporte.causas()) == 1
 
 
def test_get_reporte_devuelve_el_mismo_reporte_que_ejecutar():
    insp = inspeccion_dimensional()
    reporte = insp.ejecutar([10.6])
    assert insp.get_reporte() is reporte
 
 
def test_cada_procedimiento_registra_su_propio_tipo_de_defecto():
    """Polimorfismo: la misma operación ejecutar() con dos procedimientos
    distintos produce defectos de su propio tipo y con sus propios datos."""
    muestra_dim = nueva_muestra()
    muestra_vis = nueva_muestra()
    inspeccion_dimensional(muestra=muestra_dim).ejecutar([10.6])
    inspeccion_visual(muestra=muestra_vis).ejecutar([hallazgo("borde")])
 
    defecto_dim = muestra_dim.defectos()[0]
    defecto_vis = muestra_vis.defectos()[0]
    assert defecto_dim.get_tipo() == "dimensional"
    assert defecto_dim.datos_observacion()["valor_medido_mm"] == 10.6
    assert defecto_vis.get_tipo() == "visual"
    assert defecto_vis.datos_observacion()["zona_afectada"] == "borde"
 
 
# =====================================================================
# Transiciones (reglas 6 y 9)
# =====================================================================
 
 
def test_ejecutar_dos_veces_la_misma_inspeccion_lanza_error():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(muestra=muestra)
    reporte = insp.ejecutar([10.6])
    defectos = muestra.defectos()
    with pytest.raises(TransicionIlegal, match="ya fue ejecutada"):
        insp.ejecutar([10.05])
    assert muestra.defectos() == defectos
    assert muestra.es_no_conforme()
    assert insp.get_reporte() is reporte
 
 
def test_reinspeccionar_una_muestra_cerrada_lanza_error():
    """Una segunda inspección sobre la misma muestra se rechaza y no
    cambia ni el resultado ni los defectos de la primera."""
    muestra = nueva_muestra()
    inspeccion_dimensional(muestra=muestra).ejecutar([10.6])
    defectos = muestra.defectos()
 
    segunda = inspeccion_dimensional(muestra=muestra)
    with pytest.raises(TransicionIlegal, match="no está PENDIENTE"):
        segunda.ejecutar([10.05])
    assert muestra.defectos() == defectos
    assert muestra.es_no_conforme()
    assert segunda.fue_ejecutada() is False
    assert segunda.get_reporte() is None
 
 
def test_validar_requisitos_sobre_muestra_cerrada_lanza_error():
    """El chequeo de estado vive en validar_requisitos(), no depende de
    que después falle marcar_en_inspeccion()."""
    muestra = nueva_muestra()
    inspeccion_dimensional(muestra=muestra).ejecutar([10.05])
    with pytest.raises(TransicionIlegal, match="no está PENDIENTE"):
        inspeccion_dimensional(muestra=muestra).validar_requisitos()
 
 
# =====================================================================
# Rollback
# =====================================================================
 
 
def test_observaciones_mal_formadas_dejan_la_muestra_intacta():
    muestra = nueva_muestra()
    insp = inspeccion_dimensional(muestra=muestra)
    with pytest.raises(DatosInvalidos, match="medición"):
        insp.ejecutar(["10.6"])
    assert esta_intacta(muestra)
    assert insp.fue_ejecutada() is False
    assert insp.get_reporte() is None
 
 
def test_despues_del_rollback_se_puede_reintentar():
    """Una ejecución fallida no cuenta: la misma inspección se reintenta
    con observaciones corregidas."""
    muestra = nueva_muestra()
    insp = inspeccion_visual(muestra=muestra)
    with pytest.raises(DatosInvalidos):
        insp.ejecutar([{"zona": "borde"}])
    reporte = insp.ejecutar([hallazgo("borde")])
    assert isinstance(reporte, Reporte)
    assert muestra.es_no_conforme()
 
 
# =====================================================================
# Circuito completo
# =====================================================================
 
 
def test_circuito_completo_un_reporte_por_muestra_no_conforme():
    """20 muestras, una sola no conforme: exactamente un reporte, 5 % y
    el lote queda APROBADO."""
    lote = Lote(100)
    muestras = []
    for _ in range(20):
        muestra = Muestra(1)
        lote.agregar_muestra(muestra)
        muestras.append(muestra)
 
    reportes = []
    reporte = inspeccion_visual(muestra=muestras[0]).ejecutar([hallazgo("borde")])
    reportes.append(reporte)
    for muestra in muestras[1:]:
        reporte = inspeccion_visual(muestra=muestra).ejecutar([hallazgo("cara")])
        if reporte is not None:
            reportes.append(reporte)
 
    assert len(reportes) == 1
    assert reportes[0].get_muestra() is muestras[0]
    assert lote.porcentaje_no_conformes() == 5.0
    assert lote.decidir() is EstadoLote.APROBADO
 