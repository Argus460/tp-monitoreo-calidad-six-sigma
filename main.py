"""Punto de entrada del sistema de monitoreo de calidad industrial.

Este archivo NO contiene lógica de negocio: solo arma objetos del dominio
y los usa, para poder probar el flujo a mano. Toda la lógica vive en
sistema_calidad.py.
"""

from datetime import date

from sistema_calidad import (
    Certificacion,
    Equipo,
    Inspeccion,
    Lote,
    Muestra,
    ProcedimientoDimensional,
    ProcedimientoVisual,
    Profesional,
    Registro,
)


def armar_escenario() -> Registro:
    """Crea un registro con lote, muestras, profesionales, equipos y
    procedimientos de ejemplo."""
    pass


def correr_inspecciones(registro: Registro) -> None:
    """Ejecuta las inspecciones del escenario y muestra los resultados."""
    pass


def main() -> None:
    pass


if __name__ == "__main__":
    main()