"""Punto de entrada del sistema de monitoreo de calidad industrial.
 
Este archivo NO contiene lógica de negocio: solo arma objetos del dominio,
los usa y muestra los resultados. Toda la lógica vive en sistema_calidad.py,
y las clases del dominio no imprimen nada: informan con valores de retorno
o con excepciones, y es este archivo el que decide qué mostrar.
 
Se corre desde la raíz del proyecto con:  py main.py
 
El recorrido tiene cinco partes:
    1. Armado del escenario y alta de todo en el Registro.
    2. Inspecciones de a una sobre el lote 1, incluidas dos que fallan por
       requisitos (certificación y equipo) y se vuelven a intentar.
    3. Inspecciones en orden de llegada con la Agenda sobre el lote 2,
       incluida una con un dato mal cargado que se vuelve a programar.
    4. Consultas y decisión de los dos lotes.
    5. Guardado y carga del Registro con pickle.
"""
 
from datetime import date, timedelta
 
from sistema_calidad import (
    Agenda,
    Certificacion,
    Equipo,
    ErrorCalidad,
    Inspeccion,
    Lote,
    Muestra,
    ProcedimientoDimensional,
    ProcedimientoVisual,
    Profesional,
    Registro,
)
 
# Las inspecciones del recorrido se hacen con la fecha del día. Las demás
# fechas del ejemplo (calibraciones y vencimientos) se calculan a partir de
# HOY con timedelta, así el resultado es el mismo cualquier día que se
# corra: el calibre vigente siempre está dentro de los 182 días, el viejo
# siempre afuera y la certificación de Ana siempre vigente.
#
# El dominio, en cambio, nunca llama a date.today(): la fecha le llega
# siempre por parámetro. Es main quien decide que sea la de hoy.
HOY = date.today()
 
# Archivo donde la parte 5 guarda el Registro con pickle.
ARCHIVO_REGISTRO = "registro.pkl"
 
# =====================================================================
# Funciones de presentación
# =====================================================================
 
 
def titulo(texto: str) -> None:
    print()
    print("=" * 70)
    print(texto)
    print("=" * 70)
 
 
def mostrar_error(error: ErrorCalidad) -> None:
    print(f"  Error esperado -> {type(error).__name__}: {error}")
 
 
def inspeccionar(registro: Registro, inspeccion: Inspeccion,
                 observaciones) -> None:
    """Ejecuta una inspección suelta, la registra si salió bien y muestra
    el resultado. Si falla, muestra el error y el estado de la muestra,
    que quedó como estaba gracias al rollback de Inspeccion.ejecutar()."""
    muestra = inspeccion.get_muestra()
    print(f"\n{inspeccion.get_id()}: muestra {muestra.get_id()}, "
          f"{inspeccion.get_profesional().get_nombre()} con "
          f"{inspeccion.get_equipo().get_categoria()} "
          f"({inspeccion.get_equipo().get_id()}), "
          f"observaciones {observaciones}")
    try:
        reporte = inspeccion.ejecutar(observaciones)
    except ErrorCalidad as error:
        mostrar_error(error)
        print(f"  La muestra sigue {muestra.get_estado().value}, "
              f"con {len(muestra.defectos())} defecto(s)")
        return
 
    registro.registrar_inspeccion(inspeccion)
    print(f"  Resultado: {muestra.get_estado().value} - "
          f"{len(muestra.defectos())} defecto(s), "
          f"suma de gravedades {muestra.suma_gravedades()}")
    if reporte is None:
        print("  Sin reporte")
    else:
        registro.registrar_reporte(reporte)
        print(reporte)
 
 
# =====================================================================
# 1. Escenario
# =====================================================================
 
 
def armar_escenario() -> dict:
    """Crea los objetos del ejemplo y los da de alta en un Registro.
    Devuelve un diccionario con todo lo creado, para que cada parte del
    recorrido tome solo lo que necesita."""
    titulo("1. ESCENARIO")
 
    # Lote 1: cuatro muestras, que se inspeccionan de a una (parte 2)
    lote1 = Lote(1000)
    muestras1 = []
    for _ in range(4):
        muestra = Muestra(10)
        lote1.agregar_muestra(muestra)
        muestras1.append(muestra)
 
    # Lote 2: veinte muestras, que se procesan con la Agenda (parte 3)
    lote2 = Lote(500)
    muestras2 = []
    for _ in range(20):
        muestra = Muestra(5)
        lote2.agregar_muestra(muestra)
        muestras2.append(muestra)
 
    # Ana tiene la certificación que exige el dimensional; Beto, ninguna
    ana = Profesional("Ana")
    ana.agregar_certificacion(
        Certificacion("Metrologia", HOY + timedelta(days=180)))
    beto = Profesional("Beto")
 
    # El calibre viejo se calibró hace más de 182 días: no es apto
    calibre = Equipo("calibre", HOY - timedelta(days=50))
    calibre_viejo = Equipo("calibre", HOY - timedelta(days=300))
    camara = Equipo("camara", HOY - timedelta(days=20))
 
    dimensional = ProcedimientoDimensional(5, "calibre", "Metrologia",
                                           nominal_mm=10.0,
                                           tolerancia_mm=0.1)
    visual = ProcedimientoVisual(4, "camara", None,
                                 zonas_criticas=("borde",))
 
    registro = Registro()
    for lote in (lote1, lote2):
        registro.registrar_lote(lote)
    for profesional in (ana, beto):
        registro.registrar_profesional(profesional)
    for equipo in (calibre, calibre_viejo, camara):
        registro.registrar_equipo(equipo)
    for procedimiento in (dimensional, visual):
        registro.registrar_procedimiento(procedimiento)
 
    print(f"Fecha de las inspecciones: {HOY}")
    print(lote1)
    print(lote2)
    print(f"Profesionales: {ana.get_nombre()} ({ana.get_id()}), "
          f"{beto.get_nombre()} ({beto.get_id()})")
    print(f"Equipos: {calibre.get_id()}, {calibre_viejo.get_id()} "
          f"(calibración vencida), {camara.get_id()}")
    print(f"Procedimientos: {dimensional.get_id()} dimensional, "
          f"{visual.get_id()} visual")
 
    print("\nRegistrar dos veces el mismo lote:")
    try:
        registro.registrar_lote(lote1)
    except ErrorCalidad as error:
        mostrar_error(error)
 
    print("\nDecidir el lote 1 antes de inspeccionar sus muestras:")
    try:
        lote1.decidir()
    except ErrorCalidad as error:
        mostrar_error(error)
 
    return {
        "registro": registro,
        "lote1": lote1,
        "lote2": lote2,
        "muestras1": muestras1,
        "muestras2": muestras2,
        "ana": ana,
        "beto": beto,
        "calibre": calibre,
        "calibre_viejo": calibre_viejo,
        "camara": camara,
        "dimensional": dimensional,
        "visual": visual,
    }
 
 
# =====================================================================
# 2. Inspecciones de a una (lote 1)
# =====================================================================
 
 
def inspecciones_de_a_una(e: dict) -> None:
    titulo("2. INSPECCIONES DE A UNA - LOTE 1")
    registro = e["registro"]
    m0, m1, m2, m3 = e["muestras1"]
 
    print("Un defecto de gravedad 4: no supera el límite (5) -> CONFORME")
    inspeccionar(registro, Inspeccion(m0, e["ana"], e["calibre"],
                                      e["dimensional"], HOY),
                 [10.02, 10.35])
 
    print("\nFisura en una zona crítica: gravedad 5 -> NO_CONFORME")
    inspeccionar(registro, Inspeccion(m1, e["ana"], e["camara"],
                                      e["visual"], HOY),
                 [{"zona_afectada": "borde", "patron": "fisura"}])
 
    print("\nReinspeccionar una muestra ya cerrada:")
    inspeccionar(registro, Inspeccion(m1, e["ana"], e["camara"],
                                      e["visual"], HOY), [])
 
    print("\nProfesional sin la certificación que exige el procedimiento:")
    inspeccionar(registro, Inspeccion(m2, e["beto"], e["calibre"],
                                      e["dimensional"], HOY), [10.0])
 
    print("\nLa misma muestra, ahora con Ana. Tres defectos leves "
          "(2 + 3 + 2 = 7 > 5) -> NO_CONFORME sin ningún crítico")
    inspeccionar(registro, Inspeccion(m2, e["ana"], e["calibre"],
                                      e["dimensional"], HOY),
                 [10.15, 10.25, 10.18])
 
    print("\nEquipo con la calibración vencida:")
    inspeccionar(registro, Inspeccion(m3, e["ana"], e["calibre_viejo"],
                                      e["dimensional"], HOY), [10.05])
 
    print("\nLa misma muestra con un calibre vigente, dentro de tolerancia:")
    inspeccionar(registro, Inspeccion(m3, e["ana"], e["calibre"],
                                      e["dimensional"], HOY), [10.05])
 
 
# =====================================================================
# 3. Inspecciones en orden de llegada con la Agenda (lote 2)
# =====================================================================
 
 
def inspecciones_con_agenda(e: dict) -> None:
    titulo("3. AGENDA - LOTE 2")
    agenda = Agenda(e["registro"])
    muestras = e["muestras2"]
 
    # Muestra 0: fisura en el borde -> NO_CONFORME
    agenda.programar(Inspeccion(muestras[0], e["ana"], e["camara"],
                                e["visual"], HOY),
                     [{"zona_afectada": "borde", "patron": "fisura"}])
    # Muestra 1: un dato mal cargado -> la inspección va a fallar
    con_error = Inspeccion(muestras[1], e["ana"], e["calibre"],
                           e["dimensional"], HOY)
    agenda.programar(con_error, [10.01, "diez"])
    # Muestra 2: una raya en una zona no crítica -> defecto leve
    agenda.programar(Inspeccion(muestras[2], e["ana"], e["camara"],
                                e["visual"], HOY),
                     [{"zona_afectada": "cara", "patron": "raya"}])
    # Las 17 restantes, dentro de tolerancia
    for muestra in muestras[3:]:
        agenda.programar(Inspeccion(muestra, e["ana"], e["calibre"],
                                    e["dimensional"], HOY),
                         [10.0, 10.05])
 
    print(f"Inspecciones programadas: {agenda.cantidad_pendientes()}")
    print(f"Las tres primeras de la cola: {agenda.pendientes()[:3]}")
 
    print("\nProgramar dos veces la misma inspección:")
    try:
        agenda.programar(con_error, [10.0])
    except ErrorCalidad as error:
        mostrar_error(error)
 
    print("\nSe procesa solo la primera (la más antigua):")
    reporte = agenda.procesar_siguiente()
    print(reporte)
    print(f"Quedan {agenda.cantidad_pendientes()} pendientes")
 
    print("\nSe procesan todas las demás:")
    print(f"  Resumen: {agenda.procesar_todas()}")
    print(f"  La muestra {muestras[1].get_id()} de la inspección fallida "
          f"quedó {muestras[1].get_estado().value} (rollback)")
 
    print("\nSe corrige el dato y se vuelve a programar la misma "
          "inspección:")
    agenda.programar(con_error, [10.01, 10.0])
    print(f"  Resumen: {agenda.procesar_todas()}")
    print(f"  La muestra {muestras[1].get_id()} quedó "
          f"{muestras[1].get_estado().value}")
 
 
# =====================================================================
# 4. Consultas y decisión de los lotes
# =====================================================================
 
 
def decidir_lotes(e: dict) -> None:
    titulo("4. CONSULTAS Y DECISIÓN DE LOS LOTES")
    for lote in (e["lote1"], e["lote2"]):
        print(f"\n{lote}")
        print(f"  Todas cerradas:          {lote.todas_cerradas()}")
        print(f"  % no conformes:          {lote.porcentaje_no_conformes()}")
        print(f"  Defectos críticos:       {lote.contar_criticos()}")
        print(f"  Defectos por tipo:       {lote.contar_defectos_por_tipo()}")
        print(f"  Decisión:                {lote.decidir().value}")
 
    print("\nEl lote 2 tiene exactamente 5 % de no conformes y queda "
          "APROBADO: el rechazo exige superar el umbral.")
 
    print("\nAgregar una muestra a un lote ya decidido:")
    try:
        e["lote1"].agregar_muestra(Muestra(5))
    except ErrorCalidad as error:
        mostrar_error(error)
 
    print("\nVolver a decidir un lote:")
    try:
        e["lote1"].decidir()
    except ErrorCalidad as error:
        mostrar_error(error)
 
 
# =====================================================================
# 5. Persistencia
# =====================================================================
 
 
def guardar_y_cargar(e: dict) -> None:
    titulo("5. GUARDAR Y CARGAR EL REGISTRO")
    registro = e["registro"]
    archivo = ARCHIVO_REGISTRO
    try:
        registro.guardar(archivo)
        cargado = Registro.cargar(archivo)
    except (OSError, ErrorCalidad) as error:
        print(f"No se pudo guardar o cargar el registro: {error}")
        return
 
    print(f"Registro guardado en '{archivo}' y vuelto a cargar.")
    print(f"  Inspecciones registradas: {len(cargado.inspecciones())}")
    print(f"  Reportes registrados:     {len(cargado.reportes())}")
    for lote in (e["lote1"], e["lote2"]):
        print(f"  {cargado.obtener_lote(lote.get_id())}")
 
 
def main() -> None:
    escenario = armar_escenario()
    inspecciones_de_a_una(escenario)
    inspecciones_con_agenda(escenario)
    decidir_lotes(escenario)
    guardar_y_cargar(escenario)
 
 
if __name__ == "__main__":
    main()