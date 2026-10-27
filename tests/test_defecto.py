"""Tests de Defecto: creación, validaciones de tipo, descripción y gravedad,
y que sus datos no se puedan modificar desde afuera.

Defecto no tiene id ni contador, así que este archivo no necesita el
fixture que reinicia los contadores."""

import pytest

from sistema_calidad import DatosInvalidos, Defecto


# --- creación --------------------------------------------------------

def test_creacion_defecto():
    defecto = Defecto(
        "visual",
        "Hallazgo visual en zona borde",
        3,
        zona_afectada="borde",
        patron="fisura"
    )

    assert defecto.get_tipo() == "visual"
    assert defecto.get_descripcion() == "Hallazgo visual en zona borde"
    assert defecto.get_gravedad() == 3
    assert defecto.datos_observacion() == {"zona_afectada": "borde",
                                           "patron": "fisura"}


def test_creacion_defecto_dimensional():
    defecto = Defecto("dimensional", "Medición 10.35 fuera de tolerancia", 4,
                      valor_medido_mm=10.35, nominal_mm=10.0,
                      tolerancia_mm=0.1)
    assert defecto.get_tipo() == "dimensional"
    assert defecto.datos_observacion()["valor_medido_mm"] == 10.35


# --- tipo y descripción ----------------------------------------------

def test_tipo_inexistente_lanza_error():
    with pytest.raises(DatosInvalidos, match="dimensional o visual"):
        Defecto("termico", "descripcion", 3)


def test_tipo_vacio_lanza_error():
    with pytest.raises(DatosInvalidos, match="'tipo' debe ser un texto"):
        Defecto("", "descripcion", 3)


def test_descripcion_vacia_lanza_error():
    with pytest.raises(DatosInvalidos, match="'descripcion' debe ser un texto"):
        Defecto("visual", "   ", 3)


# --- gravedad (pruebas mínimas de la consigna: 1, 5 y fuera de rango) --

def test_gravedad_1_es_valida():
    assert Defecto("visual", "descripcion", 1).get_gravedad() == 1


def test_gravedad_5_es_valida():
    assert Defecto("visual", "descripcion", 5).get_gravedad() == 5


def test_gravedad_0_lanza_error():
    with pytest.raises(DatosInvalidos, match="entero entre 1 y 5"):
        Defecto("visual", "descripcion", 0)


def test_gravedad_6_lanza_error():
    with pytest.raises(DatosInvalidos, match="entero entre 1 y 5"):
        Defecto("visual", "descripcion", 6)


def test_gravedad_no_entera_lanza_error():
    with pytest.raises(DatosInvalidos, match="entero entre 1 y 5"):
        Defecto("visual", "descripcion", 2.5)


def test_gravedad_booleana_lanza_error():
    """True es un int en Python: sin la exclusión pasaría como gravedad 1."""
    with pytest.raises(DatosInvalidos, match="entero entre 1 y 5"):
        Defecto("visual", "descripcion", True)


# --- es_critico ------------------------------------------------------

def test_gravedad_5_es_critico():
    assert Defecto("visual", "descripcion", 5).es_critico() is True


def test_gravedad_4_no_es_critico():
    assert Defecto("visual", "descripcion", 4).es_critico() is False


# --- inmutabilidad de los datos de observación ------------------------

def test_datos_observacion_devuelve_una_copia():
    defecto = Defecto("visual", "descripcion", 2,
                      zona_afectada="cara", patron="raya")
    datos = defecto.datos_observacion()
    datos["zona_afectada"] = "borde"
    assert defecto.datos_observacion()["zona_afectada"] == "cara"


def test_el_diccionario_original_no_queda_compartido():
    datos = {"zona_afectada": "cara", "patron": "raya"}
    defecto = Defecto("visual", "descripcion", 2, **datos)
    datos["patron"] = "otro"
    assert defecto.datos_observacion()["patron"] == "raya"