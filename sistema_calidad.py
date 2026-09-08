"""Sistema de Monitoreo de Calidad Industrial — lógica del dominio.

Trabajo práctico de Estructura de Datos. Todo el dominio vive en este
archivo; el punto de entrada está separado en main.py, como pide la consigna.

ESTADO: esqueleto. Las clases, los atributos y las firmas están definidos.
Los métodos tienen 'pass' y todavía no hacen nada.

SOBRE LAS COLECCIONES: casi todo usa listas y diccionarios. Las únicas dos
excepciones son Muestra.defectos() y Reporte.causas(), que devuelven tuplas
porque el enunciado exige explícitamente una "copia inmutable" de los
defectos. Todo método que devuelva una colección devuelve una COPIA, nunca
la colección interna.

Orden del archivo:
    1. Excepciones
    2. Estados (enums)
    3. Defecto y sus subclases
    4. Certificacion y Profesional
    5. Equipo
    6. Procedimiento y sus subclases
    7. Muestra
    8. Lote
    9. Reporte
   10. Inspeccion
   11. Registro
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from enum import Enum


# =====================================================================
# 1. EXCEPCIONES
# =====================================================================
# Todas heredan de ErrorCalidad, así un test puede capturar la base
# cuando no le importa el motivo exacto del fallo.


class ErrorCalidad(Exception):
    """Base de todos los errores del dominio. No se lanza directamente."""
    pass


class DatosInvalidos(ErrorCalidad):
    """Id vacío o duplicado, cantidad no positiva, gravedad fuera de rango,
    muestras que exceden la cantidad fabricada del lote, consultas sobre un
    lote sin muestras."""
    pass


class EquipoNoApto(ErrorCalidad):
    """Categoría de equipo incompatible o calibración vencida."""
    pass


class CertificacionFaltante(ErrorCalidad):
    """El profesional no posee la certificación exigida, o la tiene vencida."""
    pass


class TransicionIlegal(ErrorCalidad):
    """Cerrar una muestra ya cerrada, reinspeccionar, decidir un lote
    incompleto o ya decidido."""
    pass


# =====================================================================
# 2. ESTADOS
# =====================================================================
# Se usan Enum en vez de strings para que sea imposible escribir un
# estado con un typo.


class EstadoMuestra(Enum):
    """PENDIENTE y EN_INSPECCION son transitorios.
    CONFORME y NO_CONFORME son finales: no se sale de ellos."""

    PENDIENTE = "PENDIENTE"
    EN_INSPECCION = "EN_INSPECCION"
    CONFORME = "CONFORME"
    NO_CONFORME = "NO_CONFORME"


class EstadoLote(Enum):
    """ABIERTO mientras haya muestras sin cerrar.
    APROBADO y RECHAZADO son finales."""

    ABIERTO = "ABIERTO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


# =====================================================================
# 3. DEFECTOS
# =====================================================================
# CLASES INMUTABLES: nacen completas en el __init__, no tienen setters,
# sus atributos son privados y se leen por getters.
#
# Defecto es abstracta y no recibe la gravedad como número: cada subclase
# la deriva de sus propios datos. Eso es lo que justifica la jerarquía.
#
# INVARIANTE DE LA JERARQUÍA: gravedad() siempre devuelve un entero entre
# GRAVEDAD_MINIMA y GRAVEDAD_MAXIMA. Cada subclase es responsable de que
# su fórmula no se salga del rango, con techo y con piso.


class Defecto(ABC):
    """Contrato común: todo defecto sabe decir su gravedad y si es crítico,
    sin importar cómo la calculó."""

    GRAVEDAD_MINIMA = 1
    GRAVEDAD_MAXIMA = 5
    GRAVEDAD_CRITICA = 5

    def __init__(self, tipo: str, descripcion: str):
        # TODO: validar que tipo y descripcion no estén vacíos -> DatosInvalidos
        self._tipo = tipo
        self._descripcion = descripcion

    @abstractmethod
    def gravedad(self) -> int:
        """Entero entre 1 y 5. Cada subclase lo calcula a su manera."""
        pass

    def es_critico(self) -> bool:
        """True si la gravedad es exactamente 5."""
        pass

    def tipo(self) -> str:
        """La categoría del defecto. Es la clave que usa
        Lote.contar_defectos_por_tipo() para agrupar."""
        pass

    def descripcion(self) -> str:
        pass

    def __str__(self) -> str:
        pass


class DefectoDimensional(Defecto):
    """Defecto de medición. Deriva su gravedad de cuántas veces se pasó
    de la tolerancia admitida."""

    def __init__(self, tipo: str, descripcion: str,
                 desviacion_mm: float, tolerancia_mm: float):
        super().__init__(tipo, descripcion)
        # TODO: validar tolerancia_mm > 0 -> DatosInvalidos
        # TODO: validar desviacion_mm > tolerancia_mm -> DatosInvalidos.
        #       Una desviación que entra en tolerancia no es un defecto:
        #       construir uno así sería un dato incoherente con el
        #       procedimiento que supuestamente lo produjo (regla 3).
        self._desviacion_mm = desviacion_mm
        self._tolerancia_mm = tolerancia_mm

    def gravedad(self) -> int:
        """max(1, min(5, ceil(desviacion_mm / tolerancia_mm))).

        Cuántas veces se pasó de la tolerancia, redondeado hacia arriba,
        con techo en 5 y piso en 1.

        El techo cumple GRAVEDAD_MAXIMA. El piso cumple GRAVEDAD_MINIMA y
        es una segunda línea de defensa: la validación del __init__ ya
        impide construir un defecto con desviación dentro de tolerancia,
        pero sin el max() la fórmula podría devolver 0 y romper el
        invariante de la jerarquía.

        Por la vía normal (ProcedimientoDimensional) el valor cae entre 2
        y 5: una medición dentro de tolerancia no llega a generar defecto,
        así que la gravedad 1 no es alcanzable por este tipo. La gravedad
        1 se produce por la vía visual."""
        pass

    def desviacion_mm(self) -> float:
        pass

    def tolerancia_mm(self) -> float:
        pass


class DefectoVisual(Defecto):
    """Defecto de inspección visual. Pesa menos que el dimensional: salvo
    que afecte una zona crítica, siempre devuelve el mismo valor fijo,
    que le fija el procedimiento que lo produjo."""

    def __init__(self, tipo: str, descripcion: str,
                 zona: str, es_zona_critica: bool, gravedad_base: int):
        super().__init__(tipo, descripcion)
        # TODO: validar zona no vacía y gravedad_base entre 1 y 4
        self._zona = zona
        self._es_zona_critica = es_zona_critica
        self._gravedad_base = gravedad_base

    def gravedad(self) -> int:
        """Zona crítica -> 5 (GRAVEDAD_CRITICA).
        Cualquier otra zona -> gravedad_base, el valor fijo del procedimiento.

        Como gravedad_base está validada entre 1 y 4, el resultado siempre
        cae dentro del rango sin necesidad de recortarlo."""
        pass

    def zona(self) -> str:
        pass

    def es_zona_critica(self) -> bool:
        pass


# =====================================================================
# 4. CERTIFICACION Y PROFESIONAL
# =====================================================================
# Certificacion guarda solo nombre y vencimiento. No lleva fecha de
# emisión porque la regla 5 del enunciado no la usa: define la vigencia
# como "inclusiva en la fecha de inspección", o sea un único borde.


class Certificacion:
    """Una habilitación con fecha de vencimiento. CLASE INMUTABLE."""

    def __init__(self, nombre: str, vencimiento: date):
        # TODO: validar nombre no vacío -> DatosInvalidos
        self._nombre = nombre
        self._vencimiento = vencimiento

    def esta_vigente(self, fecha: date) -> bool:
        """Vigente de forma inclusiva: fecha <= vencimiento.
        El día exacto del vencimiento todavía cuenta como vigente."""
        pass

    def nombre(self) -> str:
        pass

    def vencimiento(self) -> date:
        pass


class Profesional:
    """Quien ejecuta una inspección. Responsable de su identidad y de sus
    certificaciones vigentes. No cambia tolerancias durante una ejecución."""

    contador = 0
    
    def __init__(self, nombre: str):
        # TODO: validar id y nombre no vacíos -> DatosInvalidos
        self._id = 'Prof' + str(Profesional.contador)
        Profesional.contador += 1
        self._nombre = nombre
        self._certificaciones: dict[str, Certificacion] = {}

    def agregar_certificacion(self, cert: Certificacion) -> None:
        """Indexada por nombre. Agregar dos veces el mismo nombre reemplaza
        la anterior: representa una renovación, no un duplicado."""
        pass

    def tiene_certificacion_vigente(self, nombre: str, fecha: date) -> bool:
        """Dos cosas a la vez: que la tenga y que no esté vencida a esa fecha."""
        pass

    def id(self) -> str:
        pass

    def nombre(self) -> str:
        pass


# =====================================================================
# 5. EQUIPO
# =====================================================================
# Responsable de su identidad, su categoría y su última calibración.
# NO decide la conformidad de una muestra y NO realiza mediciones: la
# adquisición de mediciones está fuera de alcance del TP.


class Equipo:

    DIAS_VIGENCIA_CALIBRACION = 182  # los "seis meses" del enunciado
    contador = 0

    def __init__(self, categoria: str, fecha_calibracion: date):
        # TODO: validar id y categoria no vacíos -> DatosInvalidos
        self._id = 'Equip' + str(Equipo.contador)
        Equipo.contador += 1
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    def calibracion_vigente(self, fecha_inspeccion: date) -> bool:
        """Inclusive en ambos bordes:
        fecha_inspeccion - 182 días <= fecha_calibracion <= fecha_inspeccion

        El borde superior también importa: una calibración con fecha futura
        no es válida."""
        pass

    def es_apto(self, categoria_requerida: str, fecha_inspeccion: date) -> bool:
        """Categoría coincidente Y calibración vigente."""
        pass

    def id(self) -> str:
        pass

    def categoria(self) -> str:
        pass

    def fecha_calibracion(self) -> date:
        pass


# =====================================================================
# 6. PROCEDIMIENTOS
# =====================================================================
# Acá vive LA VARIACIÓN POLIMÓRFICA del trabajo práctico. Todos los
# procedimientos exponen la misma operación observable, evaluar(), pero
# cada uno recibe un formato de observación distinto y solo puede fabricar
# su propio tipo de defecto.
#
# evaluar() es una función PURA: no toca la muestra, no guarda estado y
# devuelve defectos nuevos en cada llamada. Eso es lo que permite que
# Inspeccion pueda reintentar o descartar su resultado sin consecuencias.
#
# Un procedimiento NO aprueba el lote por sí solo.


class Procedimiento(ABC):
    """Define sus requisitos (equipo y certificación), su límite de gravedad
    acumulada, y su criterio para convertir observaciones en defectos."""
    contador = 0

    def __init__(self, limite_gravedad: int,
                 categoria_equipo: str, certificacion: str | None):
        # TODO: validar id y categoria_equipo no vacíos, limite_gravedad > 0
        self._id ='Proced' + str(Procedimiento.contador)
        Procedimiento.contador += 1
        self._limite_gravedad = limite_gravedad
        self._categoria_equipo = categoria_equipo
        self._certificacion = certificacion

    @abstractmethod
    def evaluar(self, observaciones) -> list[Defecto]:
        """Convierte las observaciones crudas en cero o más defectos,
        según el criterio propio de cada procedimiento.

        Si las observaciones vienen mal formadas, lanza DatosInvalidos.
        No modifica nada fuera de sí mismo."""
        pass

    def limite_gravedad(self) -> int:
        pass

    def categoria_equipo(self) -> str:
        pass

    def certificacion_requerida(self) -> str | None:
        """None si el procedimiento no exige certificación."""
        pass

    def id(self) -> str:
        pass


class ProcedimientoDimensional(Procedimiento):
    """Compara mediciones contra un valor nominal y su tolerancia."""

    def __init__(self, id: str, limite_gravedad: int, categoria_equipo: str,
                 certificacion: str | None,
                 nominal_mm: float, tolerancia_mm: float):
        super().__init__(id, limite_gravedad, categoria_equipo, certificacion)
        # TODO: validar tolerancia_mm > 0 -> DatosInvalidos
        self._nominal_mm = nominal_mm
        self._tolerancia_mm = tolerancia_mm

    def evaluar(self, mediciones: list[float]) -> list[DefectoDimensional]:
        """Por cada medición fuera de nominal +/- tolerancia, genera un
        DefectoDimensional con la desviación correspondiente. Las que caen
        dentro de tolerancia no generan nada.

        Como solo fabrica defectos con desviación estrictamente mayor que
        la tolerancia, nunca choca con la validación del __init__ de
        DefectoDimensional."""
        pass

    def nominal_mm(self) -> float:
        pass

    def tolerancia_mm(self) -> float:
        pass


class ProcedimientoVisual(Procedimiento):
    """Clasifica hallazgos visuales según la zona en que aparecen.

    Fija la gravedad base que van a tener todos sus defectos no críticos:
    es el procedimiento el que decide cuánto pesa un hallazgo visual."""

    def __init__(self, id: str, limite_gravedad: int, categoria_equipo: str,
                 certificacion: str | None,
                 zonas_criticas: set[str], gravedad_base: int = 2):
        super().__init__(id, limite_gravedad, categoria_equipo, certificacion)
        # TODO: validar gravedad_base entre 1 y 4 -> DatosInvalidos
        self._zonas_criticas = set(zonas_criticas)
        self._gravedad_base = gravedad_base

    def evaluar(self, hallazgos: list[dict]) -> list[DefectoVisual]:
        """Por cada hallazgo genera un DefectoVisual, marcándolo como zona
        crítica si la zona figura en _zonas_criticas, y pasándole la
        gravedad base del procedimiento."""
        pass

    def zonas_criticas(self) -> set[str]:
        """Copia del conjunto de zonas críticas."""
        pass

    def gravedad_base(self) -> int:
        pass


# =====================================================================
# 7. MUESTRA
# =====================================================================
# Responsable de sus defectos, su estado y su resultado de conformidad.
#
# Punto clave del diseño: NO expone un agregar_defecto() público. Recibe
# todos los defectos de una sola vez al cerrar y ahí los congela en una
# tupla. Después del cierre, cualquier intento de modificación lanza
# TransicionIlegal y deja el resultado intacto.
#
# La muestra NO conoce a su Procedimiento: recibe el límite de gravedad
# como parámetro. Eso es lo que la desacopla de un tipo de procedimiento.
#
# QUIÉN LLAMA A LAS TRANSICIONES: marcar_en_inspeccion(), cerrar() y
# revertir_a_pendiente() son públicas porque Python no tiene visibilidad
# de paquete, pero su único llamador legítimo es Inspeccion.ejecutar().
# La encapsulación real la dan las precondiciones: cada una verifica el
# estado de partida y lanza TransicionIlegal si no corresponde, así que
# ninguna secuencia inválida puede dejar la muestra en un estado incoherente.


class Muestra:

    contador = 0

    def __init__(self, unidades: int):
        # TODO: validar id no vacío y unidades entero > 0 -> DatosInvalidos
        self._id = 'Mue' + str(Muestra.contador)
        Muestra.contador += 1
        self._unidades = unidades
        self._estado = EstadoMuestra.PENDIENTE
        self._defectos: tuple[Defecto, ...] = ()
        self._lote: Lote | None = None  # lo asigna lote.agregar_muestra()

    # --- pertenencia ------------------------------------------------

    def asignar_lote(self, lote: Lote) -> None:
        """Solo la llama Lote.agregar_muestra(). Se puede asignar una única
        vez: un segundo intento lanza TransicionIlegal, porque una muestra
        no puede moverse a otro lote."""
        pass

    def lote(self) -> Lote | None:
        pass

    # --- transiciones -----------------------------------------------

    def marcar_en_inspeccion(self) -> None:
        """Solo desde PENDIENTE. Si no, TransicionIlegal.
        Único llamador legítimo: Inspeccion.ejecutar()."""
        pass

    def revertir_a_pendiente(self) -> None:
        """ROLLBACK, no una transición del ciclo de vida normal.

        Solo la llama Inspeccion.ejecutar() cuando su propia ejecución
        falló después de haber marcado la muestra. Devuelve la muestra al
        estado exacto en que estaba antes del intento, para que un error
        en las observaciones no la deje atrapada en EN_INSPECCION y, con
        ella, al lote entero sin poder decidirse.

        Precondiciones estrictas: solo desde EN_INSPECCION y solo si
        _defectos sigue vacío. Desde cualquier otro estado, TransicionIlegal.
        Eso garantiza que nunca pueda usarse para reabrir una muestra ya
        cerrada: CONFORME y NO_CONFORME siguen siendo finales."""
        pass

    def cerrar(self, defectos: list[Defecto], limite: int) -> EstadoMuestra:
        """Congela los defectos y aplica el criterio de conformidad:
        NO_CONFORME si hay al menos un defecto de gravedad 5, o si la suma
        de gravedades es estrictamente mayor que 'limite'. Si no, CONFORME.
        Ambos estados son finales; un segundo llamado lanza TransicionIlegal
        sin tocar el resultado ni los defectos existentes.

        Único llamador legítimo: Inspeccion.ejecutar()."""
        pass

    # --- consultas --------------------------------------------------

    def esta_pendiente(self) -> bool:
        pass

    def esta_cerrada(self) -> bool:
        """True si el estado es CONFORME o NO_CONFORME."""
        pass

    def es_no_conforme(self) -> bool:
        """Solo tiene sentido después del cierre."""
        pass

    def defectos(self) -> tuple[Defecto, ...]:
        """Copia inmutable. Nunca devuelve la colección interna."""
        pass

    def suma_gravedades(self) -> int:
        """Suma manual de las gravedades de los defectos."""
        pass

    def id(self) -> str:
        pass

    def unidades(self) -> int:
        pass

    def estado(self) -> EstadoMuestra:
        pass

    def __str__(self) -> str:
        pass


# =====================================================================
# 8. LOTE
# =====================================================================
# Responsable de su identidad, su cantidad fabricada, sus muestras y su
# estado. NO ejecuta mediciones.
#
# REGLA: un lote sin muestras no es evaluable. Ni porcentaje_no_conformes()
# ni decidir() tienen sentido sobre un conjunto vacío, así que ambos lanzan
# una excepción en vez de inventar un 0 %.
#
# Ojo con la separación entre porcentaje_no_conformes() y decidir(): la
# primera es una consulta pura que se puede llamar mil veces sin efectos;
# la segunda es una transición final.


class Lote:

    UMBRAL_RECHAZO_PORCENTUAL = 5.0
    contador = 0
    def __init__(self, cantidad_fabricada: int):
        # TODO: validar id no vacío y cantidad_fabricada entero > 0
        self._id = 'Lot' + str(Lote.contador)
        Lote.contador += 1
        self._cantidad_fabricada = cantidad_fabricada
        self._muestras: dict[str, Muestra] = {}
        self._estado = EstadoLote.ABIERTO

    # --- alta de muestras -------------------------------------------

    def agregar_muestra(self, muestra: Muestra) -> None:
        """Valida las tres condiciones ANTES de tocar el diccionario interno:

        1. que la muestra no pertenezca ya a un lote (muestra.lote() is None)
           -> TransicionIlegal
        2. que su id no se repita dentro de este lote -> DatosInvalidos
        3. que la suma de unidades no supere cantidad_fabricada
           -> DatosInvalidos

        Recién si las tres pasan, la incorpora al diccionario y llama a
        muestra.asignar_lote(self). Validar primero es lo que garantiza que
        un rechazo no deje la muestra a medio agregar en el lote equivocado."""
        pass

    def unidades_asignadas(self) -> int:
        """Suma manual de las unidades de todas las muestras."""
        pass

    # --- consultas sin efectos secundarios --------------------------

    def todas_cerradas(self) -> bool:
        """Ninguna muestra en PENDIENTE ni EN_INSPECCION.
        Sobre un lote sin muestras devuelve True de forma trivial; por eso
        decidir() chequea aparte que haya al menos una."""
        pass

    def porcentaje_no_conformes(self) -> float:
        """no_conformes / totales * 100, sin redondear.
        Cálculo preliminar: no cambia el estado del lote.

        Un lote sin muestras lanza DatosInvalidos: el porcentaje de un
        conjunto vacío no significa nada y devolver 0.0 daría a entender,
        falsamente, que el lote está en condiciones de aprobarse."""
        pass

    def contar_criticos(self) -> int:
        """Total de defectos de gravedad 5, considerando solo muestras
        cerradas. Sin efectos secundarios. Un lote sin muestras cerradas
        devuelve 0: acá el conjunto vacío sí tiene un resultado con sentido."""
        pass

    def contar_defectos_por_tipo(self) -> dict[str, int]:
        """Conteo por tipo de defecto, solo sobre muestras cerradas.
        Agregación manual con estructuras nativas."""
        pass

    def muestras(self) -> list[Muestra]:
        """Copia de las muestras del lote. Devuelve una lista nueva, nunca
        el diccionario interno."""
        pass

    # --- decisión final ---------------------------------------------

    def decidir(self) -> EstadoLote:
        """Requiere al menos una muestra y que todas estén cerradas; si no,
        TransicionIlegal. RECHAZADO si el porcentaje no conforme es
        estrictamente mayor que 5 %; con exactamente 5 % queda APROBADO.
        La decisión es final: un segundo llamado lanza TransicionIlegal."""
        pass

    def id(self) -> str:
        pass

    def cantidad_fabricada(self) -> int:
        pass

    def estado(self) -> EstadoLote:
        pass

    def __str__(self) -> str:
        pass


# =====================================================================
# 9. REPORTE
# =====================================================================
# CLASE INMUTABLE. Recibe la tupla de defectos ya congelada desde
# muestra.defectos(); no la genera él. Como los Defecto son inmutables,
# la copia superficial alcanza para que las causas queden estables.
#
# El id no se inventa ni se pasa desde afuera: lo deriva Inspeccion a
# partir de su propio id ("REP-" + id de la inspección). Como una muestra
# admite una sola inspección aceptada, ese id es único sin necesidad de
# un contador ni de un registro que lo asigne.
#
# Una muestra conforme NO genera reporte. Una no conforme genera
# exactamente uno.


class Reporte:
    contador = 0
    def __init__(self, muestra: Muestra, lote: Lote,
                 profesional: Profesional, fecha: date,
                 defectos: tuple[Defecto, ...]):
        # TODO: validar id no vacío -> DatosInvalidos
        self._id = 'Rep' + str(Reporte.contador)
        Reporte.contador += 1        
        self._muestra = muestra
        self._lote = lote
        self._profesional = profesional
        self._fecha = fecha
        self._defectos = defectos

    def causas(self) -> tuple[Defecto, ...]:
        """La copia congelada de los defectos que determinaron el rechazo."""
        pass

    def resumen(self) -> str:
        """Texto legible con muestra, lote, profesional, fecha y causas.
        Acá vive la construcción del texto; __str__ delega en este método."""
        pass

    def id(self) -> str:
        pass

    def fecha(self) -> date:
        pass

    def muestra(self) -> Muestra:
        pass

    def lote(self) -> Lote:
        pass

    def profesional(self) -> Profesional:
        pass

    def __str__(self) -> str:
        """Delega en resumen(). No duplica la lógica del texto."""
        pass


# =====================================================================
# 10. INSPECCION
# =====================================================================
# La ORQUESTADORA del sistema. Es la única clase que ve a los cuatro
# participantes al mismo tiempo (muestra, profesional, equipo,
# procedimiento), por eso es la que valida en conjunto antes de tocar nada.
#
# Recibe todo en el constructor y no permite cambiar sus requisitos durante
# la ejecución. No se reutiliza para otra muestra.
#
# La fecha entra por parámetro y nunca se toma de date.today(): es lo que
# hace reproducibles los tests de los bordes de calibración y certificación.


class Inspeccion:

    PREFIJO_REPORTE = "REP-"

    contador = 0
    def __init__(self, id: str, muestra: Muestra, profesional: Profesional,
                 equipo: Equipo, procedimiento: Procedimiento, fecha: date):
        # TODO: validar id no vacío -> DatosInvalidos
        self._id = 'Insp' + str(Inspeccion.contador)
        Inspeccion.contador += 1        
        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._ejecutada = False
        self._reporte: Reporte | None = None

    def validar_requisitos(self) -> None:
        """Chequea, en orden, las tres condiciones previas. Lanza la excepción
        que corresponda ANTES de tocar la muestra, para que un rechazo no deje
        efectos secundarios:

        1. Si el procedimiento exige certificación y el profesional no la
           tiene vigente a la fecha -> CertificacionFaltante
        2. Si el equipo no es apto (categoría o calibración) -> EquipoNoApto
        3. Si la muestra no está PENDIENTE -> TransicionIlegal

        El orden importa para los tests: si un escenario tiene dos requisitos
        mal a la vez, la excepción que sale es la primera de la lista. Cada
        test debería romper un solo requisito por vez.
        """
        pass

    def ejecutar(self, observaciones) -> Reporte | None:
        """Secuencia completa:

        1. Si esta inspección ya se ejecutó -> TransicionIlegal
        2. validar_requisitos()
        3. muestra.marcar_en_inspeccion()
        4. Dentro de un try:
               defectos = procedimiento.evaluar(observaciones)
               muestra.cerrar(defectos, procedimiento.limite_gravedad())
           Si algo de eso falla, se llama a muestra.revertir_a_pendiente()
           y se relanza la excepción original sin envolverla.
        5. Si quedó no conforme -> construye el Reporte con id
           PREFIJO_REPORTE + self._id y lo devuelve.
           Si quedó conforme -> devuelve None.

        POR QUÉ EL ROLLBACK: evaluar() puede fallar con observaciones mal
        formadas, y para entonces la muestra ya está EN_INSPECCION. Sin
        rollback quedaría trabada ahí para siempre: no vuelve a ser
        PENDIENTE, así que no admite otra inspección, y no está cerrada,
        así que el lote entero nunca podría decidirse. El rollback lo
        dispara únicamente la inspección que falló, y solo puede devolver
        la muestra al estado previo: no habilita reabrir una muestra cerrada.

        Una muestra admite una única inspección aceptada. Si se intenta una
        segunda inspección sobre la misma muestra, validar_requisitos()
        la rechaza en el paso 3, porque la muestra ya no está PENDIENTE.
        """
        pass

    def reporte(self) -> Reporte | None:
        """El reporte emitido, o None si la muestra quedó conforme."""
        pass

    def id(self) -> str:
        pass

    def fecha(self) -> date:
        pass

    def muestra(self) -> Muestra:
        pass

    def profesional(self) -> Profesional:
        pass

    def equipo(self) -> Equipo:
        pass

    def procedimiento(self) -> Procedimiento:
        pass


# =====================================================================
# 11. REGISTRO
# =====================================================================
# Garantiza que los identificadores sean únicos dentro de cada categoría.
# Es la única puerta de entrada para dar de alta entidades: sin él, la
# unicidad quedaría a cargo de quien crea los objetos, y ahí es donde se
# rompe. Guarda además las inspecciones y los reportes emitidos.


class Registro:

    def __init__(self):
        self._lotes: dict[str, Lote] = {}
        self._profesionales: dict[str, Profesional] = {}
        self._equipos: dict[str, Equipo] = {}
        self._procedimientos: dict[str, Procedimiento] = {}
        self._inspecciones: list[Inspeccion] = []
        self._reportes: list[Reporte] = []

    # --- altas ------------------------------------------------------

    def registrar_lote(self, lote: Lote) -> None:
        """Id duplicado dentro de la categoría -> DatosInvalidos."""
        pass

    def registrar_profesional(self, profesional: Profesional) -> None:
        pass

    def registrar_equipo(self, equipo: Equipo) -> None:
        pass

    def registrar_procedimiento(self, procedimiento: Procedimiento) -> None:
        pass

    def registrar_inspeccion(self, inspeccion: Inspeccion) -> None:
        """Valida id único e incorpora la inspección a la lista."""
        pass

    def registrar_reporte(self, reporte: Reporte) -> None:
        """Valida id único -> DatosInvalidos. Como el id del reporte deriva
        del id de la inspección, un duplicado acá delata que se emitieron
        dos reportes para la misma inspección."""
        pass

    # --- consultas --------------------------------------------------

    def obtener_lote(self, id: str) -> Lote:
        """Id inexistente -> DatosInvalidos."""
        pass

    def obtener_profesional(self, id: str) -> Profesional:
        pass

    def obtener_equipo(self, id: str) -> Equipo:
        pass

    def obtener_procedimiento(self, id: str) -> Procedimiento:
        pass

    def inspecciones(self) -> list[Inspeccion]:
        """Copia de la lista de inspecciones registradas."""
        pass

    def reportes(self) -> list[Reporte]:
        """Copia de la lista de reportes emitidos."""
        pass
