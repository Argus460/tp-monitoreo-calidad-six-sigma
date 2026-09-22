import pytest
from sistema_calidad import DatosInvalidos, Procedimiento, ProcedimientoVisual, ProcedimientoDimensional

@pytest.fixture(autouse=True)
def reset_procedimiento_state():
    Procedimiento.contador=0

def test_creacion_procedimiento_valido():
    """Prueba la creación de un procedimiento visual válido."""
    proc = ProcedimientoVisual(5, "visual", None, ("soldadura",))
    assert proc.limite_gravedad() == 5
    assert proc.categoria_equipo() == "visual"
    assert proc.certificacion_requerida() is None
    assert proc.id() == "Proced0"
    
def test_ids_consecutivos():
    p1=ProcedimientoVisual(5, "visual", None, ("soldadura",))
    p2=ProcedimientoVisual(5, "visual", None, ("soldadura",))
    assert p1.id() == "Proced0"
    assert p2.id() == "Proced1"
def test_limite_gravedad_invalido_lanza_error():
    with pytest.raises(DatosInvalidos, match="limite_gravedad"):
        ProcedimientoVisual(0,"visual", None, ("soldadura",))
def test_categoria_equipo_vacio_lanza_error():
    with pytest.raises(DatosInvalidos, match="categoria_equipo"):
        ProcedimientoVisual(5,"", None, ("soldadura",))

def test_procedimiento_visual_hereda_de_procedimiento():
    """Prueba que ProcedimientoVisual hereda de Procedimiento."""
    proc = ProcedimientoVisual(5, "visual", None, ("soldadura",))
    assert isinstance(proc, Procedimiento)
    assert issubclass(ProcedimientoVisual, Procedimiento)

def test_creacion_procedimiento_dimensional_valido(): 
    """Prueba la creación de un procedimiento dimensional válido."""
    proc = ProcedimientoDimensional(10, "dimensional", "Metrología", 10.0, 0.1) 
    assert proc.limite_gravedad() == 10 
    assert proc.categoria_equipo() == "dimensional" 
    assert proc.certificacion_requerida() == "Metrología" 
    assert proc.id() == "Proced0" 

def test_dimensional_hereda_de_procedimiento(): 
    """Prueba que ProcedimientoDimensional hereda de Procedimiento."""
    proc = ProcedimientoDimensional(10, "dimensional", "Metrología", 10.0, 0.1) 
    assert isinstance(proc, Procedimiento) 
    assert issubclass(ProcedimientoDimensional, Procedimiento) 

