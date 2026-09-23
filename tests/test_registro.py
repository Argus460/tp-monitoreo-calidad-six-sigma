"""Tests de Registro.

Registro es la clase que garantiza que los ids sean únicos dentro de cada
categoría (regla 1). Estos tests están escritos a partir de sus
docstrings:
  - registrar_*: DatosInvalidos si el id ya existe en su categoría.
  - obtener_*:   DatosInvalidos si el id no existe.
  - inspecciones() y reportes(): una lista nueva, nunca el diccionario interno.

Los mensajes de error se chequean con match= buscando el id involucrado,
así que el mensaje de cada DatosInvalidos tiene que mencionarlo
(por ejemplo: "Ya hay un lote registrado con id Lot0.").

Con ids autoincrementales, dos objetos distintos no pueden tener el mismo
id... salvo que se reinicie el contador. Los tests de "id repetido con
objetos distintos" hacen justamente eso.

Al final del archivo hay tres tests PENDIENTES, vacíos y con skip, que
se completan cuando Inspeccion funcione.

Se ejecutan desde la raíz del proyecto con:  py -m pytest -v
"""

from datetime import date

import pytest

from sistema_calidad import (Registro, Lote, Muestra, Reporte, Profesional,
                             Equipo, Procedimiento, ProcedimientoVisual,
                             Inspeccion, DatosInvalidos)


HOY = date(2026, 9, 23)


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


def nuevo_procedimiento():
    return ProcedimientoVisual(5, "camara", None, ("borde",))


def nuevo_reporte():
    """Un reporte armado a mano sobre una muestra cerrada NO_CONFORME,
    sin pasar por Inspeccion."""
    lote = Lote(100)
    muestra = Muestra(1)
    lote.agregar_muestra(muestra)
    muestra.marcar_en_inspeccion(ProcedimientoVisual.CAMPOS_OBSERVACION)
    muestra.registrar_defecto("visual", "fisura en el borde", 5,
                              zona_afectada="borde", patron="fisura")
    muestra.cerrar(5)
    return Reporte(muestra, lote, Profesional("Ana"), HOY, muestra.defectos())


# =====================================================================
# Registro vacío
# =====================================================================


def test_registro_nuevo_no_tiene_inspecciones_ni_reportes():
    registro = Registro()
    assert registro.inspecciones() == []
    assert registro.reportes() == []


# =====================================================================
# Alta y consulta por id
# =====================================================================


def test_registrar_y_obtener_lote():
    registro = Registro()
    lote = Lote(100)
    registro.registrar_lote(lote)
    assert registro.obtener_lote("Lot0") is lote


def test_registrar_y_obtener_profesional():
    registro = Registro()
    profesional = Profesional("Ana")
    registro.registrar_profesional(profesional)
    assert registro.obtener_profesional("Prof0") is profesional


def test_registrar_y_obtener_equipo():
    registro = Registro()
    equipo = Equipo("camara", HOY)
    registro.registrar_equipo(equipo)
    assert registro.obtener_equipo("Equip0") is equipo


def test_registrar_y_obtener_procedimiento():
    registro = Registro()
    procedimiento = nuevo_procedimiento()
    registro.registrar_procedimiento(procedimiento)
    assert registro.obtener_procedimiento("Proced0") is procedimiento


def test_registrar_varios_de_la_misma_categoria():
    registro = Registro()
    lote_a = Lote(100)
    lote_b = Lote(200)
    registro.registrar_lote(lote_a)
    registro.registrar_lote(lote_b)
    assert registro.obtener_lote("Lot0") is lote_a
    assert registro.obtener_lote("Lot1") is lote_b


def test_registrar_reporte_aparece_en_reportes():
    registro = Registro()
    reporte = nuevo_reporte()
    registro.registrar_reporte(reporte)
    assert registro.reportes() == [reporte]


# =====================================================================
# Ids duplicados: el mismo objeto dos veces
# =====================================================================


def test_registrar_el_mismo_lote_dos_veces_lanza_error():
    registro = Registro()
    lote = Lote(100)
    registro.registrar_lote(lote)
    with pytest.raises(DatosInvalidos, match="Lot0"):
        registro.registrar_lote(lote)


def test_registrar_el_mismo_profesional_dos_veces_lanza_error():
    registro = Registro()
    profesional = Profesional("Ana")
    registro.registrar_profesional(profesional)
    with pytest.raises(DatosInvalidos, match="Prof0"):
        registro.registrar_profesional(profesional)


def test_registrar_el_mismo_equipo_dos_veces_lanza_error():
    registro = Registro()
    equipo = Equipo("camara", HOY)
    registro.registrar_equipo(equipo)
    with pytest.raises(DatosInvalidos, match="Equip0"):
        registro.registrar_equipo(equipo)


def test_registrar_el_mismo_procedimiento_dos_veces_lanza_error():
    registro = Registro()
    procedimiento = nuevo_procedimiento()
    registro.registrar_procedimiento(procedimiento)
    with pytest.raises(DatosInvalidos, match="Proced0"):
        registro.registrar_procedimiento(procedimiento)


def test_registrar_el_mismo_reporte_dos_veces_lanza_error():
    registro = Registro()
    reporte = nuevo_reporte()
    registro.registrar_reporte(reporte)
    with pytest.raises(DatosInvalidos, match="Rep0"):
        registro.registrar_reporte(reporte)
    assert len(registro.reportes()) == 1


# =====================================================================
# Ids duplicados: objetos distintos con el mismo id
# =====================================================================


def test_dos_lotes_distintos_con_el_mismo_id_lanza_error():
    """El caso que el contador no cubre: si se reinicia, repite ids."""
    registro = Registro()
    registro.registrar_lote(Lote(100))      # Lot0
    Lote.contador = 0
    with pytest.raises(DatosInvalidos, match="Lot0"):
        registro.registrar_lote(Lote(200))  # otra vez Lot0


def test_un_alta_rechazada_no_reemplaza_al_original():
    """Después del rechazo, el id sigue apuntando al primer lote."""
    registro = Registro()
    original = Lote(100)
    registro.registrar_lote(original)
    Lote.contador = 0
    with pytest.raises(DatosInvalidos):
        registro.registrar_lote(Lote(200))
    assert registro.obtener_lote("Lot0") is original


def test_dos_reportes_distintos_con_el_mismo_id_lanza_error():
    registro = Registro()
    registro.registrar_reporte(nuevo_reporte())     # Rep0
    Reporte.contador = 0
    with pytest.raises(DatosInvalidos, match="Rep0"):
        registro.registrar_reporte(nuevo_reporte())  # otra vez Rep0


# =====================================================================
# Consultas de ids inexistentes
# =====================================================================


def test_obtener_lote_inexistente_lanza_error():
    with pytest.raises(DatosInvalidos, match="Lot99"):
        Registro().obtener_lote("Lot99")


def test_obtener_profesional_inexistente_lanza_error():
    with pytest.raises(DatosInvalidos, match="Prof99"):
        Registro().obtener_profesional("Prof99")


def test_obtener_equipo_inexistente_lanza_error():
    with pytest.raises(DatosInvalidos, match="Equip99"):
        Registro().obtener_equipo("Equip99")


def test_obtener_procedimiento_inexistente_lanza_error():
    with pytest.raises(DatosInvalidos, match="Proced99"):
        Registro().obtener_procedimiento("Proced99")


def test_las_categorias_son_independientes():
    """Un lote registrado no aparece al buscar entre los profesionales."""
    registro = Registro()
    registro.registrar_lote(Lote(100))
    with pytest.raises(DatosInvalidos, match="Lot0"):
        registro.obtener_profesional("Lot0")


# =====================================================================
# Las listas se devuelven copiadas
# =====================================================================


def test_reportes_devuelve_una_copia():
    registro = Registro()
    registro.registrar_reporte(nuevo_reporte())
    copia = registro.reportes()
    copia.clear()
    assert len(registro.reportes()) == 1


# =====================================================================
# PENDIENTES: TERMINAR DE HACER CUANDO INSPECCION FUNCIONE
# =====================================================================
# Estos tests necesitan crear una Inspeccion, y hoy Inspeccion.__init__
# falla (error G2 del informe: llama a muestra.lote(), que no existe).
# Quedan vacíos y marcados con skip: pytest los muestra como SKIPPED, sin
# darlos por aprobados. Cuando Inspeccion esté corregida, se completan y
# se borra el @pytest.mark.skip.

PENDIENTE_INSPECCION = "TERMINAR DE HACER CUANDO INSPECCION FUNCIONE"


@pytest.mark.skip(reason=PENDIENTE_INSPECCION)
def test_registrar_inspeccion_aparece_en_inspecciones():
    """Registrar una inspección hace que aparezca en inspecciones()."""
    pass


@pytest.mark.skip(reason=PENDIENTE_INSPECCION)
def test_registrar_la_misma_inspeccion_dos_veces_lanza_error():
    """Registrar dos veces la misma inspección lanza DatosInvalidos con su
    id en el mensaje, y la lista sigue teniendo una sola."""
    pass


@pytest.mark.skip(reason=PENDIENTE_INSPECCION)
def test_inspecciones_devuelve_una_copia():
    """Modificar la lista que devuelve inspecciones() no cambia al Registro."""
    pass
