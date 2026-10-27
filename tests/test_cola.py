"""Tests de Cola (lista enlazada) y de sus consultas recursivas."""

import pytest

from sistema_calidad import Cola, DatosInvalidos


# --- cola vacía ------------------------------------------------------

def test_cola_nueva_esta_vacia():
    cola = Cola()
    assert cola.esta_vacia()
    assert cola.cantidad() == 0
    assert cola.a_lista() == []


def test_desencolar_cola_vacia_lanza_error():
    with pytest.raises(DatosInvalidos, match="cola está vacía"):
        Cola().desencolar()


def test_frente_cola_vacia_lanza_error():
    with pytest.raises(DatosInvalidos, match="no hay frente"):
        Cola().frente()


# --- FIFO ------------------------------------------------------------

def test_sale_primero_el_primero_que_entro():
    cola = Cola()
    cola.encolar("a")
    cola.encolar("b")
    cola.encolar("c")
    assert cola.desencolar() == "a"
    assert cola.desencolar() == "b"
    assert cola.desencolar() == "c"
    assert cola.esta_vacia()


def test_frente_no_saca_el_elemento():
    cola = Cola()
    cola.encolar("a")
    cola.encolar("b")
    assert cola.frente() == "a"
    assert cola.frente() == "a"
    assert cola.cantidad() == 2


def test_cola_vaciada_se_puede_volver_a_usar():
    """Al vaciarse, el final también vuelve a None: si no, el próximo
    encolar engancharía el nodo nuevo a un nodo que ya salió."""
    cola = Cola()
    cola.encolar("a")
    cola.desencolar()
    cola.encolar("b")
    assert cola.frente() == "b"
    assert cola.a_lista() == ["b"]


# --- consultas recursivas --------------------------------------------

def test_cantidad_cuenta_todos_los_nodos():
    cola = Cola()
    for dato in ["a", "b", "c", "d"]:
        cola.encolar(dato)
    assert cola.cantidad() == 4


def test_a_lista_respeta_el_orden_de_llegada():
    cola = Cola()
    for dato in ["a", "b", "c"]:
        cola.encolar(dato)
    assert cola.a_lista() == ["a", "b", "c"]


def test_las_consultas_no_modifican_la_cola():
    cola = Cola()
    cola.encolar("a")
    cola.encolar("b")
    cola.cantidad()
    cola.a_lista()
    assert cola.desencolar() == "a"
    assert cola.desencolar() == "b"


def test_a_lista_devuelve_una_lista_nueva():
    cola = Cola()
    cola.encolar("a")
    lista = cola.a_lista()
    lista.append("intruso")
    assert cola.a_lista() == ["a"]
