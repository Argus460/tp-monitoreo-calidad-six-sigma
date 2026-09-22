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
    2. Validaciones
    3. Estados (enums)
    4. Defecto y sus subclases
    5. Certificacion y Profesional
    6. Equipo
    7. Procedimiento y sus subclases
    8. Muestra
    9. Lote
    10. Reporte
   11. Inspeccion
   12. Registro
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from datetime import datetime
from datetime import timedelta
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
    """Texto vacío, id duplicado o inexistente, cantidad no positiva,
    gravedad fuera de rango, fecha que no es date, datos de observación
    incoherentes con el procedimiento, muestras que exceden la cantidad
    fabricada del lote, consultas sobre un lote sin muestras."""
    pass


class EquipoNoApto(ErrorCalidad):
    """Categoría de equipo incompatible o calibración vencida."""
    pass


class CertificacionFaltante(ErrorCalidad):
    """El profesional no posee la certificación exigida, o la tiene vencida."""
    pass


class TransicionIlegal(ErrorCalidad):
    """Operación no permitida en el estado actual: cerrar una muestra ya
    cerrada, registrar defectos fuera de EN_INSPECCION, reinspeccionar,
    mover una muestra a otro lote, agregar muestras a un lote decidido,
    decidir un lote incompleto o ya decidido."""
    pass

# =====================================================================
# 2. VALIDACIONES
# =====================================================================
# Chequeos de datos de entrada que se repiten en varias clases. Son
# staticmethods porque no dependen de ningún objeto: reciben el valor y
# el nombre del campo (solo para armar el mensaje), no devuelven nada si
# el dato está bien y lanzan DatosInvalidos si está mal.
#
# Detalle que importa para los tests: en Python bool es subclase de int,
# así que True pasaría como entero 1. Por eso se excluye explícitamente.


class Validar:

    @staticmethod
    def texto_no_vacio(valor, campo: str) -> None:
        """Un str con al menos un carácter que no sea espacio."""
        if not isinstance(valor, str) or valor.strip() == "":
            raise DatosInvalidos(
                f"'{campo}' debe ser un texto no vacío (recibido: {valor!r}).")

    @staticmethod
    def entero_positivo(valor, campo: str) -> None:
        """Un int estrictamente mayor que 0. No acepta float ni bool."""
        if not Validar._es_entero(valor) or valor <= 0:
            raise DatosInvalidos(
                f"'{campo}' debe ser un entero positivo (recibido: {valor!r}).")

    @staticmethod
    def entero_en_rango(valor, minimo: int, maximo: int, campo: str) -> None:
        """Un int entre minimo y maximo, ambos inclusive."""
        if not Validar._es_entero(valor) or not (minimo <= valor <= maximo):
            raise DatosInvalidos(
                f"'{campo}' debe ser un entero entre {minimo} y {maximo} "
                f"(recibido: {valor!r}).")

    @staticmethod
    def numero_positivo(valor, campo: str) -> None:
        """Un int o float estrictamente mayor que 0. No acepta bool.
        Se escribe 'not valor > 0' y no 'valor <= 0' para que un NaN
        también sea rechazado (cualquier comparación con NaN da False)."""
        if (isinstance(valor, bool) or not isinstance(valor, (int, float))
                or not valor > 0):
            raise DatosInvalidos(
                f"'{campo}' debe ser un número positivo (recibido: {valor!r}).")

    @staticmethod
    def fecha(valor, campo: str) -> None:
        """Un date. Se rechaza datetime a propósito: aunque es subclase de
        date, comparar un datetime con un date lanza TypeError, y todo el
        diseño trabaja con date."""
        if isinstance(valor, datetime) or not isinstance(valor, date):
            raise DatosInvalidos(
                f"'{campo}' debe ser un date (recibido: {valor!r}).")

    @staticmethod
    def _es_entero(valor) -> bool:
        return isinstance(valor, int) and not isinstance(valor, bool)



# =====================================================================
# 3. ESTADOS
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
# 4. DEFECTOS
# =====================================================================
# CLASE INMUTABLE: nace completa en el __init__, no tiene setters, sus
# atributos son privados y se leen por getters.
#
# Es UNA SOLA clase concreta. Los datos específicos de cada observación
# (valor_medido_mm y tolerancia_mm en uno dimensional, zona_afectada y
# patron en uno visual) llegan por **datos_observacion y se guardan en un
# diccionario. Cada procedimiento pasa solo los campos que le corresponden,
# sin forzar parámetros vacíos en los demás.
#
# La gravedad llega ya calculada: la calcula el procedimiento, que es
# quien tiene el criterio (regla 7). Defecto solo garantiza que esté en
# rango (regla 3).
#
# POR QUÉ NO HAY SUBCLASES DE DEFECTO: como la gravedad la calcula el
# procedimiento, un defecto dimensional y uno visual solo se diferencian
# en qué campos guardan, y eso es exactamente lo que resuelve **kwargs.
# La jerarquía de herencia del TP vive en Procedimiento, que es donde hay
# comportamiento realmente distinto.


class Defecto:
    """Una desviación observada: tipo, descripción, gravedad y los datos
    propios de la observación que la produjo."""

    GRAVEDAD_MINIMA = 1
    GRAVEDAD_MAXIMA = 5
    GRAVEDAD_CRITICA = 5

    def __init__(self, tipo: str, descripcion: str, gravedad: int, **datos_observacion):
        Validar.texto_no_vacio(tipo, "tipo")
        Validar.texto_no_vacio(descripcion, "descripcion")
        Validar.entero_en_rango(gravedad, Defecto.GRAVEDAD_MINIMA,
                                Defecto.GRAVEDAD_MAXIMA, "gravedad")        
        if tipo == 'dimensional' or tipo == 'visual':
            self._tipo = tipo
        else:
            raise DatosInvalidos('el tipo debe ser dimensional o visual')        
        self._descripcion = descripcion
        self._gravedad = gravedad
        # dict() crea una copia: nadie de afuera conserva una referencia
        # al diccionario interno.
        self._datos_observacion = dict(datos_observacion)

    def get_gravedad(self) -> int:
        return self._gravedad

    def es_critico(self) -> bool:
        if self._gravedad == Defecto.GRAVEDAD_MAXIMA:
            return True

    def get_tipo(self) -> str:
        return self._tipo

    def get_descripcion(self) -> str:
        return self._descripcion

    def datos_observacion(self) -> dict:
        return self._datos_observacion.copy()

    def __str__(self) -> str:
        return f'tipo:{self._tipo} - descripcion:{self._descripcion} - gravedad:{self._gravedad}'


# =====================================================================
# 5. CERTIFICACION Y PROFESIONAL
# =====================================================================
# Certificacion guarda solo nombre y vencimiento. No lleva fecha de
# emisión porque la regla 5 del enunciado no la usa: define la vigencia
# como "inclusiva en la fecha de inspección", o sea un único borde.

class Certificacion:
    """Una habilitación con fecha de vencimiento. CLASE INMUTABLE."""

    def __init__(self, nombre: str, vencimiento: date):
        Validar.texto_no_vacio(nombre, "nombre de la certificación")
        Validar.fecha(vencimiento, "vencimiento")        
        self._nombre = nombre
        self._vencimiento = vencimiento

    def esta_vigente(self, fecha: date) -> bool:
        """Vigente de forma inclusiva: fecha <= vencimiento.
        El día exacto del vencimiento todavía cuenta como vigente."""
        if fecha <= self._vencimiento:
            return True
        return False

    def get_nombre(self) -> str:
        return self._nombre

    def get_vencimiento(self) -> date:
        return self._vencimiento



class Profesional:
    """Quien ejecuta una inspección. Responsable de su identidad y de sus
    certificaciones vigentes. No cambia tolerancias durante una ejecución."""

    contador = 0
    
    def __init__(self, nombre: str):
        Validar.texto_no_vacio(nombre, "nombre del profesional")
        self._id = 'Prof' + str(Profesional.contador)
        Profesional.contador += 1
        self._nombre = nombre
        self._certificaciones: dict[str, Certificacion] = {}

    def agregar_certificacion(self, cert: Certificacion) -> None:
        """Indexada por nombre. Agregar dos veces el mismo nombre reemplaza
        la anterior: representa una renovación, no un duplicado."""
        if not isinstance(cert, Certificacion):
            raise DatosInvalidos("El objeto ingresado no es una Certificacion.")
        self._certificaciones[cert.get_nombre()] = cert

    def tiene_certificacion_vigente(self, nombre: str, fecha: date) -> bool:
        """Dos cosas a la vez: que la tenga y que no esté vencida a esa fecha."""
        cert = self._certificaciones.get(nombre)
        if cert is None:
            return False
        return cert.esta_vigente(fecha)

    def get_id(self) -> str:
        return self._id

    def get_nombre(self) -> str:
        return self._nombre


# =====================================================================
# 6. EQUIPO
# =====================================================================
# Responsable de su identidad, su categoría y su última calibración.
# NO decide la conformidad de una muestra y NO realiza mediciones: la
# adquisición de mediciones está fuera de alcance del TP.


class Equipo:

    DIAS_VIGENCIA_CALIBRACION = 182  # los "seis meses" del enunciado
    contador = 0

    def __init__(self, categoria: str, fecha_calibracion: date):
        Validar.texto_no_vacio(categoria, "categoria del equipo")
        Validar.fecha(fecha_calibracion, "fecha_calibracion")
        self._id = 'Equip' + str(Equipo.contador)
        Equipo.contador += 1
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    def calibracion_vigente(self, fecha_inspeccion: date) -> bool:
        """Inclusive en ambos bordes:
        fecha_inspeccion - 182 días <= fecha_calibracion <= fecha_inspeccion

        El borde superior también importa: una calibración con fecha futura
        no es válida."""
        return fecha_inspeccion - timedelta(days=self.DIAS_VIGENCIA_CALIBRACION) <= self._fecha_calibracion <= fecha_inspeccion

    def es_apto(self, categoria_requerida: str, fecha_inspeccion: date) -> bool:
        """Categoría coincidente Y calibración vigente."""
        return self._categoria == categoria_requerida and self.calibracion_vigente(fecha_inspeccion)

    def get_id(self) -> str:
        return self._id

    def get_categoria(self) -> str:
        return self._categoria

    def get_fecha_calibracion(self) -> date:
        return self._fecha_calibracion



# =====================================================================
# 7. PROCEDIMIENTOS
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
# CAMPOS_OBSERVACION declara qué datos propios lleva cada defecto que el
# procedimiento produce. La muestra los usa para rechazar datos
# incoherentes (regla 3) sin necesidad de conocer al procedimiento.
#
# Un procedimiento NO aprueba el lote por sí solo.



class Procedimiento(ABC):
    """Define sus requisitos (equipo y certificación), su límite de gravedad
    acumulada, y su criterio para convertir observaciones en defectos."""

    CAMPOS_OBSERVACION: tuple[str] = tuple()
    contador = 0

    def __init__(self, limite_gravedad: int,
                 categoria_equipo: str, certificacion: str | None):
        Validar.entero_positivo(limite_gravedad, "limite_gravedad")
        Validar.texto_no_vacio(categoria_equipo, "categoria_equipo")
        if certificacion is not None:
            Validar.texto_no_vacio(certificacion, "certificacion")        
        self._id = 'Proced' + str(Procedimiento.contador)
        Procedimiento.contador += 1
        self._limite_gravedad = limite_gravedad
        self._categoria_equipo = categoria_equipo
        self._certificacion = certificacion

    @abstractmethod
    def evaluar(self, observaciones) -> list[dict]:
        """Convierte las observaciones crudas en cero o más HALLAZGOS,
        según el criterio propio de cada procedimiento.

        Cada hallazgo es un diccionario listo para desempaquetar en
        muestra.registrar_defecto(**hallazgo): lleva las claves 'tipo'
        (siempre el TIPO_DEFECTO del procedimiento), 'descripcion' y
        'gravedad', más exactamente los CAMPOS_OBSERVACION del procedimiento.

        Si las observaciones vienen mal formadas, lanza DatosInvalidos.
        No modifica nada fuera de sí mismo."""
        pass

    def campos_observacion(self) -> tuple[str]:
        """Los campos propios de sus defectos."""
        return self.CAMPOS_OBSERVACION
        pass

    def get_limite_gravedad(self) -> int:
        return self._limite_gravedad
        

    def get_categoria_equipo(self) -> str:
        return self._categoria_equipo   
    
    def get_certificacion_requerida(self) -> str | None:
        if self._certificacion is None:
            return None
        else: 
            return self._certificacion

    def get_id(self) -> str:
        return self._id
    


class ProcedimientoDimensional(Procedimiento):
    """Compara mediciones contra un valor nominal y su tolerancia."""

    TIPO_DEFECTO = "dimensional"
    CAMPOS_OBSERVACION = ("valor_medido_mm", "nominal_mm", "tolerancia_mm")

    def __init__(self, limite_gravedad: int, categoria_equipo: str,
                 certificacion: str | None,
                 nominal_mm: float, tolerancia_mm: float):
        
        Validar.numero_positivo(nominal_mm, "nominal_mm")
        Validar.numero_positivo(tolerancia_mm, "tolerancia_mm")        

        super().__init__(limite_gravedad, categoria_equipo, certificacion)
        self._nominal_mm = nominal_mm
        self._tolerancia_mm = tolerancia_mm
    def evaluar(self, mediciones: list[float]) -> list[dict]: 
        try:
            if not isinstance(mediciones, (list)):
                raise DatosInvalidos(
                    f"'mediciones' debe ser una lista de números "
                    f"(recibido: {mediciones!r}).")
            for m in mediciones:
                if not isinstance(m, (int, float)) or isinstance(m, bool):
                    raise DatosInvalidos(
                        f"Cada medición debe ser un número (recibido: {m!r}).")
            hallazgos = []
            for m in mediciones: 
                desvio = round(abs(m - self._nominal_mm), 6)
                tolerancia = round(self._tolerancia_mm, 6)
                if desvio > tolerancia: 
                    gravedad = max(1, min(5, math.ceil(round(desvio / tolerancia, 6))))
                    hallazgo = {
                        "tipo": self.TIPO_DEFECTO,
                        "descripcion": f"Medición {m} fuera de tolerancia",
                        "gravedad": gravedad,
                        "valor_medido_mm": m,
                        "nominal_mm": self._nominal_mm,
                        "tolerancia_mm": self._tolerancia_mm
                    }
                    hallazgos.append(hallazgo)
            return hallazgos
        except Exception as e:
            raise DatosInvalidos(
                f"Error al evaluar mediciones: {e}") from e
            
                

    def get_nominal_mm(self) -> float:
        return self._nominal_mm

    def get_tolerancia_mm(self) -> float:
        return self._tolerancia_mm


class ProcedimientoVisual(Procedimiento):
    """Clasifica hallazgos visuales según la zona en que aparecen.

    Fija la gravedad base que van a tener todos sus defectos no críticos:
    es el procedimiento el que decide cuánto pesa un hallazgo visual."""

    TIPO_DEFECTO = "visual"
    CAMPOS_OBSERVACION = ("zona_afectada", "patron")

    def __init__(self, limite_gravedad: int, categoria_equipo: str,
                 certificacion: str | None,
                 zonas_criticas: tuple[str], gravedad_base: int = 2):
        if not isinstance(zonas_criticas, tuple):
            raise DatosInvalidos(
                f"'zonas_criticas' debe ser una tupla de textos "
                f"(recibido: {zonas_criticas!r}).")
        for zona in zonas_criticas:
            Validar.texto_no_vacio(zona, "zona crítica")
        # Hasta 4: el 5 queda reservado para las zonas críticas.
        Validar.entero_en_rango(gravedad_base, Defecto.GRAVEDAD_MINIMA,
                                Defecto.GRAVEDAD_CRITICA - 1, "gravedad_base")
        super().__init__(limite_gravedad, categoria_equipo, certificacion)
        self._zonas_criticas = tuple(zonas_criticas)
        self._gravedad_base = gravedad_base

    def evaluar(self, hallazgos: list[dict]) -> list[dict]:
        if not isinstance(hallazgos,list): 
            raise DatosInvalidos(
                f"'hallazgos' debe ser una lista de diccionarios "
                f"(recibido: {hallazgos!r}).")
        resultado=[]
        for hallazgo in hallazgos:
            if not isinstance(hallazgo, dict):
                raise DatosInvalidos(
                    f"Cada hallazgo debe ser un diccionario "
                    f"(recibido: {hallazgo!r}).")
            if "zona_afectada" not in hallazgo or "patron" not in hallazgo:
                raise DatosInvalidos(
                    f"Cada hallazgo debe contener las claves 'zona_afectada' y 'patron' "
                    f"(recibido: {hallazgo!r}).")#Revisa que CONTENGA las CLAVES
            Validar.texto_no_vacio(hallazgo["zona_afectada"], "zona_afectada")
            Validar.texto_no_vacio(hallazgo["patron"], "patron")
            if hallazgo["zona_afectada"] in self._zonas_criticas:
                gravedad = Defecto.GRAVEDAD_CRITICA   
            else:
                gravedad = self._gravedad_base
            resultado.append(
                {
                "tipo": self.TIPO_DEFECTO,
                "descripcion": f"Hallazgo visual en zona {hallazgo['zona_afectada']}",
                "gravedad": gravedad,
                "zona_afectada": hallazgo["zona_afectada"],
                "patron": hallazgo["patron"]
                    })
        return resultado


# =====================================================================
# 8. MUESTRA
# =====================================================================
# Responsable de sus defectos, su estado y su resultado de conformidad.
#
# Punto clave del diseño: los defectos entran de a uno por
# registrar_defecto(), pero SOLO mientras la muestra está EN_INSPECCION y
# SOLO con los campos de observación del procedimiento en curso. Después
# del cierre, el estado final bloquea cualquier alta (TransicionIlegal) y
# los defectos solo se leen como tupla.
#
# La muestra NO conoce a su Procedimiento: recibe el límite de gravedad y
# los campos de observación como datos. Eso es lo que la desacopla de un
# tipo de procedimiento.
#
# QUIÉN LLAMA A LAS TRANSICIONES: marcar_en_inspeccion(),
# registrar_defecto(), cerrar() y revertir_a_pendiente() son públicas
# porque Python no tiene visibilidad de paquete, pero su único llamador
# legítimo es Inspeccion.ejecutar(). La encapsulación real la dan las
# precondiciones: cada una verifica el estado de partida y lanza
# TransicionIlegal si no corresponde, así que ninguna secuencia inválida
# puede dejar la muestra en un estado incoherente.
#
# LÍMITE CONOCIDO: lo que las precondiciones no pueden garantizar es que
# se hayan validado profesional y equipo, ni que se emita el reporte. Eso
# lo garantiza solo el camino Inspeccion.ejecutar(). Llamar a las
# transiciones a mano desde afuera es usar mal la clase, y así queda
# documentado.

class Muestra:

    contador = 0

    def __init__(self, unidades: int):
        Validar.entero_positivo(unidades, "unidades")
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
        # FALTA FUNCIÓN -> TransicionIlegal si self._lote ya no es None
        pass

    def lote(self) -> Lote | None:
        pass

    # --- transiciones -----------------------------------------------

    def marcar_en_inspeccion(self, campos_observacion: tuple[str]) -> None:
        """Solo desde PENDIENTE. Si no, TransicionIlegal.
        
        Guarda los campos de observación del procedimiento en curso: son
        los que registrar_defecto() exige. Quedan fijos hasta el cierre,
        así los requisitos no cambian durante la ejecución (regla 6).
        Único llamador legítimo: Inspeccion.ejecutar().
        """
        # FALTA FUNCIÓN -> TransicionIlegal si el estado no es PENDIENTE
        pass

    def registrar_defecto(self, tipo: str, descripcion: str, gravedad: int,
                          **datos_observacion) -> None:
        """Registra un defecto en la muestra incluyendo los datos
        específicos de la observación.

        Cada procedimiento genera observaciones con campos distintos: uno
        dimensional registra valor_medido_mm, nominal_mm y tolerancia_mm;
        uno visual registra zona_afectada y patron. Con **kwargs cada
        procedimiento pasa solo los atributos que le corresponden.

        Validaciones, en este orden y ANTES de tocar _defectos:
        1. La muestra está EN_INSPECCION -> si no, TransicionIlegal.
           Cubre "no registrar defectos ajenos a la inspección en curso"
           (regla 7) y "no agregar defectos a una muestra cerrada" (regla 9).
        2. Los campos recibidos son exactamente los del procedimiento en
           curso, ni uno más ni uno menos -> si no, DatosInvalidos (regla 3).
        3. tipo, descripcion y gravedad son válidos -> si no, DatosInvalidos.
           Esta la hace el __init__ de Defecto.

        Único llamador legítimo: Inspeccion.ejecutar(), que desempaqueta
        cada hallazgo de evaluar() con muestra.registrar_defecto(**hallazgo).
        """
        # 1. Estado
        if self._estado is not EstadoMuestra.EN_INSPECCION:
            raise TransicionIlegal(
                f"La muestra {self._id} está en estado "
                f"{self._estado.value}: solo admite defectos EN_INSPECCION.")

        # 2. Coherencia de los datos con el procedimiento en curso
        recibidos = tuple(datos_observacion)
        if recibidos != self._campos_observacion:
            faltan = sorted(self._campos_observacion - recibidos)
            sobran = sorted(recibidos - self._campos_observacion)
            raise DatosInvalidos(
                f"Datos de observación incoherentes con el procedimiento "
                f"en curso (faltan: {faltan}, sobran: {sobran}).")

        # 3. Construcción: Defecto valida tipo, descripcion y gravedad
        defecto = Defecto(tipo, descripcion, gravedad, **datos_observacion)

        # Recién ahora, con todo validado, se toca la colección interna.
        self._defectos.append(defecto)

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
        # FALTA FUNCIÓN -> TransicionIlegal si el estado no es EN_INSPECCION
        pass

    def cerrar(self, limite: int) -> EstadoMuestra:
        """Aplica el criterio de conformidad sobre los defectos registrados:
        NO_CONFORME si hay al menos un defecto de gravedad 5, o si la suma
        de gravedades es estrictamente mayor que 'limite'. Si no, CONFORME.

        Solo desde EN_INSPECCION. Ambos estados son finales; un segundo
        llamado lanza TransicionIlegal sin tocar el resultado ni los
        defectos existentes.

        Único llamador legítimo: Inspeccion.ejecutar()."""
        # FALTA FUNCIÓN -> TransicionIlegal si el estado no es EN_INSPECCION
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
# 9. LOTE
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
        Validar.entero_positivo(cantidad_fabricada, "cantidad_fabricada")
        self._id = 'Lot' + str(Lote.contador)
        Lote.contador += 1
        self._cantidad_fabricada = cantidad_fabricada
        self._muestras: dict[str, Muestra] = {}
        self._estado = EstadoLote.ABIERTO

    # --- alta de muestras -------------------------------------------

    def agregar_muestra(self, muestra: Muestra) -> None:
        """Valida las cuatro condiciones ANTES de tocar el diccionario interno:

        1. que el lote siga ABIERTO -> TransicionIlegal. Agregar una muestra
           pendiente a un lote ya decidido contradiría una decisión final.
        2. que la muestra no pertenezca ya a un lote (muestra.lote() is None)
           -> TransicionIlegal
        3. que su id no se repita dentro de este lote -> DatosInvalidos.
           Con ids autoincrementales es defensiva: el caso "misma muestra
           dos veces" ya lo corta la condición 2.
        4. que la suma de unidades no supere cantidad_fabricada
           -> DatosInvalidos

        Recién si las cuatro pasan, la incorpora al diccionario y llama a
        muestra.asignar_lote(self). Validar primero es lo que garantiza que
        un rechazo no deje la muestra a medio agregar en el lote equivocado."""
        # FALTA FUNCIÓN -> TransicionIlegal (1, 2) y DatosInvalidos (3, 4)
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
        """Validaciones, en este orden:
        1. Lote ya decidido -> TransicionIlegal (la decisión es final)
        2. Lote sin muestras -> DatosInvalidos (misma regla que
           porcentaje_no_conformes())
        3. Alguna muestra sin cerrar -> TransicionIlegal

        RECHAZADO si el porcentaje no conforme es estrictamente mayor que
        5 %; con exactamente 5 % queda APROBADO."""
        # FALTA FUNCIÓN -> TransicionIlegal (1, 3) y DatosInvalidos (2)
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
# 10. REPORTE
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
        Validar.fecha(fecha, "fecha del reporte")
        # Una muestra no conforme siempre tiene al menos un defecto (un
        # crítico, o una suma mayor que un límite positivo). Un reporte
        # sin causas sería incoherente.
        if not isinstance(defectos, tuple) or not defectos:
            raise DatosInvalidos(
                "Un reporte necesita una tupla con al menos un defecto.")
        # FALTA FUNCIÓN -> DatosInvalidos si muestra.lote() no es 'lote'
        # o si la muestra no es no conforme
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
# 11. INSPECCION
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

    def __init__(self, muestra: Muestra, profesional: Profesional,
                 equipo: Equipo, procedimiento: Procedimiento, fecha: date):
        Validar.fecha(fecha, "fecha de inspección")
        Inspeccion.contador += 1     
        if muestra.lote() == None:
            raise DatosInvalidos('La muestra no tiene un lote asignado')
        else:
            self._muestra = muestra        
        self._id = 'Insp' + str(Inspeccion.contador)
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._ejecutada = False
        self._reporte: Reporte | None = None



    def validar_requisitos(self) -> None:
        if self._procedimiento._certificacion != None and (self._profesional.tiene_certificacion_vigente(self._procedimiento._certificacion) == False or self._procedimiento._certificacion not in self._profesional._certificaciones):
            raise CertificacionFaltante('El profesional no tiene la certificacion requerida')
        elif self._equipo.es_apto(self._procedimiento._categoria_equipo, self._fecha) == False:
            raise EquipoNoApto('EL equipo no es apto para realizar la inspeccion')
        elif self._muestra._estado != 'PENDIENTE':
            raise TransicionIlegal('La puestra ya fue cerrada')
        else:
            print('Requiitos validados')
        
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
        
        if self._ejecutada == True:
            raise TransicionIlegal('La inspeccion ya fue ejecutada')
        else:
            self.validar_requisitos()

        self._muestra.marcar_en_inspeccion(self._procedimiento.campos_observacion())

        try:
            hallazgos = self._procedimiento.evaluar(observaciones)
            for hallazgo in hallazgos:
                self._muestra.registrar_defecto(**hallazgo)
            self._muestra.cerrar(self._procedimiento.limite_gravedad())
        except Exception:
            self._muestra.revertir_a_pendiente()
            raise

        self._ejecutada = True
        
        if self._muestra.estado == 'NO_CONFORME':
            self._reporte = Reporte(self._muestra, self._muestra._lote, self._profesional, self._fecha, hallazgos)
            return self._reporte
        else:
            return None

        """Secuencia completa:

        1. Si esta inspección ya se ejecutó -> TransicionIlegal
        2. validar_requisitos()
        3. muestra.marcar_en_inspeccion(procedimiento.campos_observacion())
        4. Dentro de un try:
                hallazgos = procedimiento.evaluar(observaciones)
                for hallazgo in hallazgos:
                    muestra.registrar_defecto(**hallazgo)
                muestra.cerrar(procedimiento.limite_gravedad())
           Si algo de eso falla, se llama a muestra.revertir_a_pendiente()
           y se relanza la excepción original sin envolverla.
        5. Marca _ejecutada = True. Solo se marca si todo salió bien: una
           ejecución que falló y se revirtió puede reintentarse con la
           misma inspección y observaciones corregidas.
        6. Si quedó no conforme -> construye el Reporte con id
           PREFIJO_REPORTE + self._id y lo devuelve.
           Si quedó conforme -> devuelve None.

        POR QUÉ EL REPORTE VA FUERA DEL try: cuando se construye, la
        muestra ya está cerrada y no se puede revertir. Entonces el Reporte
        no puede fallar, porque una muestra no conforme sin reporte rompe
        la regla 10. Por eso todo lo que Reporte valida está garantizado
        antes: la fecha y el lote de la muestra los chequea el __init__ de
        Inspeccion, y una muestra no conforme siempre tiene defectos.   
        
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

    def get_reporte(self) -> Reporte | None:
        if self._reporte == None:
            return None
        else:
            return self._reporte

    def get_id(self) -> str:
        return self._id

    def get_fecha(self) -> date:
        return self._fecha

    def get_muestra(self) -> Muestra:
        return self._muestra

    def get_profesional(self) -> Profesional:
        return self._profesional

    def get_equipo(self) -> Equipo:
        return self._equipo

    def procedimiento(self) -> Procedimiento:
        return self._procedimiento


# =====================================================================
# 12. REGISTRO
# =====================================================================
# Garantiza que los identificadores sean únicos dentro de cada categoría.
# Es la única puerta de entrada para dar de alta entidades.
#
# Con ids autoincrementales, dos objetos distintos ya nacen con ids
# distintos. El Registro sigue siendo la barrera para lo que el contador
# no cubre: registrar dos veces el mismo objeto, o ids repetidos si un
# test reinicia un contador.
#
# Todas las categorías, incluidas inspecciones y reportes, son
# diccionarios indexados por id: la unicidad se chequea con 'in' en vez
# de recorrer una lista, y obtener por id es directo.


class Registro:

    def __init__(self):
        self._lotes: dict[str, Lote] = {}
        self._profesionales: dict[str, Profesional] = {}
        self._equipos: dict[str, Equipo] = {}
        self._procedimientos: dict[str, Procedimiento] = {}
        self._inspecciones: dict[str, Inspeccion] = {}
        self._reportes: dict[str, Reporte] = {}

    # --- altas ------------------------------------------------------
    # FALTA FUNCIÓN (todas las altas) -> DatosInvalidos si el id ya existe
    # en su categoría.

    def registrar_lote(self, lote: Lote) -> None:
        pass

    def registrar_profesional(self, profesional: Profesional) -> None:
        pass

    def registrar_equipo(self, equipo: Equipo) -> None:
        pass

    def registrar_procedimiento(self, procedimiento: Procedimiento) -> None:
        pass

    def registrar_inspeccion(self, inspeccion: Inspeccion) -> None:
        pass

    def registrar_reporte(self, reporte: Reporte) -> None:
        """Como el id del reporte deriva del id de la inspección, un
        duplicado acá delata que se emitieron dos reportes para la misma
        inspección."""
        pass

    # --- consultas --------------------------------------------------
    # FALTA FUNCIÓN (todos los obtener_*) -> DatosInvalidos si el id no existe.


    def obtener_lote(self, id: str) -> Lote:
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
