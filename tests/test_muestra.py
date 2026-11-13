import pytest

from sistema_calidad import (
    Muestra,
    Lote,
    Defecto,
    DatosInvalidos,
    TransicionIlegal,
    EstadoMuestra
)


# ============================================================
# RESET AUTOMÁTICO ANTES DE CADA TEST
# ============================================================

@pytest.fixture(autouse=True)
def reset_muestra_state():
    Muestra.contador = 0
    Lote.contador = 0


# ============================================================
# CONSTRUCTOR
# ============================================================

def test_creacion_muestra_valida():
    muestra = Muestra(10)

    assert isinstance(muestra, Muestra)


def test_creacion_muestra_estado_inicial():
    muestra = Muestra(10)

    assert muestra.get_id() == "Mue0"
    assert muestra.get_unidades() == 10
    assert muestra.get_estado() is EstadoMuestra.PENDIENTE
    assert muestra.get_lote() is None
    assert muestra.defectos() == ()


def test_id_muestra_autoincremental():
    muestra1 = Muestra(10)
    muestra2 = Muestra(20)

    assert muestra1.get_id() == "Mue0"
    assert muestra2.get_id() == "Mue1"


def test_unidades_cero_lanza_error():
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(0)


def test_unidades_negativas_lanza_error():
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(-5)


def test_unidades_float_lanza_error():
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(2.5)


def test_unidades_bool_lanza_error():
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra(True)


def test_unidades_texto_lanza_error():
    with pytest.raises(DatosInvalidos, match="unidades"):
        Muestra("10")


# ============================================================
# ASIGNAR LOTE
# ============================================================

def test_asignar_lote():
    muestra = Muestra(10)
    lote = Lote(100)

    muestra.asignar_lote(lote)

    assert muestra.get_lote() is lote


def test_asignar_lote_dos_veces_lanza_error():
    muestra = Muestra(10)
    lote1 = Lote(100)
    lote2 = Lote(100)

    muestra.asignar_lote(lote1)

    with pytest.raises(TransicionIlegal):
        muestra.asignar_lote(lote2)

    assert muestra.get_lote() is lote1


# ============================================================
# MARCAR EN INSPECCIÓN
# ============================================================

def test_marcar_en_inspeccion():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    assert muestra.get_estado() is EstadoMuestra.EN_INSPECCION


def test_marcar_en_inspeccion_dos_veces_lanza_error():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    with pytest.raises(TransicionIlegal):
        muestra.marcar_en_inspeccion(campos)


# ============================================================
# REGISTRAR DEFECTOS
# ============================================================

def test_registrar_defecto_valido():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "dimensional",
        "Medición fuera de tolerancia",
        3,
        valor_medido_mm=12,
        nominal_mm=10,
        tolerancia_mm=1
    )

    defectos = muestra.defectos()

    assert len(defectos) == 1
    assert isinstance(defectos[0], Defecto)
    assert defectos[0].get_tipo() == "dimensional"
    assert defectos[0].get_gravedad() == 3


def test_registrar_defecto_en_muestra_pendiente_lanza_error():
    muestra = Muestra(10)

    with pytest.raises(TransicionIlegal):
        muestra.registrar_defecto(
            "dimensional",
            "Medición fuera de tolerancia",
            3,
            valor_medido_mm=12,
            nominal_mm=10,
            tolerancia_mm=1
        )


def test_registrar_defecto_con_datos_faltantes_lanza_error():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    with pytest.raises(DatosInvalidos, match="faltan"):
        muestra.registrar_defecto(
            "dimensional",
            "Medición fuera de tolerancia",
            3,
            valor_medido_mm=12,
            nominal_mm=10
        )


def test_registrar_defecto_con_datos_sobrantes_lanza_error():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    with pytest.raises(DatosInvalidos, match="sobran"):
        muestra.registrar_defecto(
            "dimensional",
            "Medición fuera de tolerancia",
            3,
            valor_medido_mm=12,
            nominal_mm=10,
            tolerancia_mm=1,
            color="rojo"
        )


def test_defecto_invalido_no_se_agrega():
    muestra = Muestra(10)

    campos = (
        "valor_medido_mm",
        "nominal_mm",
        "tolerancia_mm"
    )

    muestra.marcar_en_inspeccion(campos)

    with pytest.raises(DatosInvalidos):
        muestra.registrar_defecto(
            "dimensional",
            "Medición incorrecta",
            8,
            valor_medido_mm=12,
            nominal_mm=10,
            tolerancia_mm=1
        )

    assert len(muestra.defectos()) == 0


# ============================================================
# SUMA DE GRAVEDADES
# ============================================================

def test_suma_gravedades():
    muestra = Muestra(10)

    campos = (
        "zona_afectada",
        "patron"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "visual",
        "Defecto 1",
        2,
        zona_afectada="frente",
        patron="raya"
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto 2",
        3,
        zona_afectada="costado",
        patron="mancha"
    )

    assert muestra.suma_gravedades() == 5


def test_suma_gravedades_sin_defectos():
    muestra = Muestra(10)

    assert muestra.suma_gravedades() == 0


# ============================================================
# CERRAR MUESTRA
# ============================================================

def test_cerrar_muestra_conforme():
    muestra = Muestra(10)

    campos = (
        "zona_afectada",
        "patron"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "visual",
        "Defecto leve",
        2,
        zona_afectada="frente",
        patron="raya"
    )

    estado = muestra.cerrar(5)

    assert estado is EstadoMuestra.CONFORME
    assert muestra.get_estado() is EstadoMuestra.CONFORME


def test_cerrar_no_conforme_por_suma_gravedades():
    muestra = Muestra(10)

    campos = (
        "zona_afectada",
        "patron"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "visual",
        "Defecto 1",
        3,
        zona_afectada="frente",
        patron="raya"
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto 2",
        3,
        zona_afectada="costado",
        patron="mancha"
    )

    estado = muestra.cerrar(5)

    assert estado is EstadoMuestra.NO_CONFORME


def test_cerrar_no_conforme_por_defecto_critico():
    muestra = Muestra(10)

    campos = (
        "zona_afectada",
        "patron"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "visual",
        "Defecto crítico",
        5,
        zona_afectada="frente",
        patron="rotura"
    )

    estado = muestra.cerrar(100)

    assert estado is EstadoMuestra.NO_CONFORME


def test_suma_igual_al_limite_es_conforme():
    muestra = Muestra(10)

    campos = (
        "zona_afectada",
        "patron"
    )

    muestra.marcar_en_inspeccion(campos)

    muestra.registrar_defecto(
        "visual",
        "Defecto 1",
        2,
        zona_afectada="frente",
        patron="raya"
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto 2",
        2,
        zona_afectada="costado",
        patron="mancha"
    )

    estado = muestra.cerrar(4)

    assert estado is EstadoMuestra.CONFORME


def test_cerrar_muestra_pendiente_lanza_error():
    muestra = Muestra(10)

    with pytest.raises(TransicionIlegal):
        muestra.cerrar(5)


def test_cerrar_dos_veces_lanza_error():
    muestra = Muestra(10)

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    muestra.cerrar(5)

    with pytest.raises(TransicionIlegal):
        muestra.cerrar(5)


# ============================================================
# REVERTIR A PENDIENTE
# ============================================================

def test_revertir_a_pendiente():
    muestra = Muestra(10)

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto",
        2,
        zona_afectada="frente",
        patron="raya"
    )

    muestra.revertir_a_pendiente()

    assert muestra.get_estado() is EstadoMuestra.PENDIENTE
    assert muestra.defectos() == ()


def test_revertir_pendiente_fuera_de_inspeccion_lanza_error():
    muestra = Muestra(10)

    with pytest.raises(TransicionIlegal):
        muestra.revertir_a_pendiente()


# ============================================================
# CONSULTAS DE ESTADO
# ============================================================

def test_esta_pendiente():
    muestra = Muestra(10)

    assert muestra.esta_pendiente() is True

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    assert muestra.esta_pendiente() is False


def test_esta_cerrada():
    muestra = Muestra(10)

    assert muestra.esta_cerrada() is False

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    assert muestra.esta_cerrada() is False

    muestra.cerrar(5)

    assert muestra.esta_cerrada() is True


def test_es_no_conforme():
    muestra = Muestra(10)

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto crítico",
        5,
        zona_afectada="frente",
        patron="rotura"
    )

    muestra.cerrar(100)

    assert muestra.es_no_conforme() is True


def test_muestra_conforme_no_es_no_conforme():
    muestra = Muestra(10)

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    muestra.cerrar(5)

    assert muestra.es_no_conforme() is False


# ============================================================
# DEFECTOS
# ============================================================

def test_defectos_devuelve_tupla():
    muestra = Muestra(10)

    assert isinstance(muestra.defectos(), tuple)


def test_defectos_contiene_defectos_registrados():
    muestra = Muestra(10)

    muestra.marcar_en_inspeccion(
        ("zona_afectada", "patron")
    )

    muestra.registrar_defecto(
        "visual",
        "Defecto",
        2,
        zona_afectada="frente",
        patron="raya"
    )

    defectos = muestra.defectos()

    assert isinstance(defectos, tuple)
    assert len(defectos) == 1


# ============================================================
# __str__
# ============================================================

def test_str_muestra():
    muestra = Muestra(10)

    texto = str(muestra)

    assert "Mue0" in texto
    assert "10" in texto
    assert "PENDIENTE" in texto
    assert "defectos:0" in texto



# ============================================================
# MUESTRA CERRADA (regla 9)
# ============================================================

def test_registrar_defecto_en_muestra_cerrada_lanza_error():
    """Una vez cerrada, a la muestra no se le pueden agregar defectos:
    ni el resultado ni los defectos cambian."""
    muestra = Muestra(10)
    muestra.marcar_en_inspeccion(("zona_afectada", "patron"))
    muestra.registrar_defecto("visual", "Defecto leve", 2,
                              zona_afectada="frente", patron="raya")
    muestra.cerrar(5)

    with pytest.raises(TransicionIlegal, match="EN_INSPECCION"):
        muestra.registrar_defecto("visual", "Defecto crítico", 5,
                                  zona_afectada="frente", patron="rotura")

    assert len(muestra.defectos()) == 1
    assert muestra.get_estado() is EstadoMuestra.CONFORME


def test_revertir_una_muestra_cerrada_lanza_error():
    """El rollback no sirve para reabrir una muestra cerrada."""
    muestra = Muestra(10)
    muestra.marcar_en_inspeccion(("zona_afectada", "patron"))
    muestra.cerrar(5)

    with pytest.raises(TransicionIlegal):
        muestra.revertir_a_pendiente()

    assert muestra.get_estado() is EstadoMuestra.CONFORME