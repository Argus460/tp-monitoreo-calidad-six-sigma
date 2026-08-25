import datetime

class Lote:
    count=1
    lotes_global = []
    def __init__(self, cantidad, estado):
        self.cantidad = cantidad
        self.estado = estado
        self.muestra = []
        self.__id__ = Lote.count
        Lote.count+=1
        Lote.lotes_global.append(self.__id__)

    def agregar_muestra(self, muestra):
        self.muestra.append(muestra)

    def actualizar_estado(self):
        pass

    def get_nro_identificacion(self):
        return self.__id__

class InspeccionInvalidaError:
    pass

class Inspeccion:
    count = 0
    def __init__(self, resultado, equipo, profesional, procedimiento, muestra):
        self.__id__ = Inspeccion.count
        Inspeccion.count += 1
        if muestra in Muestra.mustras_global:
            self.muestra = muestra
        else: raise InspeccionInvalidaError

        if profesional in Profesional.lista_id_profesional:
            self.profesional = profesional
        else: raise InspeccionInvalidaError

        self.fecha = datetime.today

        if resultado == 'conforme' or resultado == 'no conforme':
            self.resultado = resultado
        else: raise InspeccionInvalidaError
        
        if procedimiento in Procedimiento.procedimiento_global:
            self.procedimiento = procedimiento
        else: raise InspeccionInvalidaError

        if equipo not in Equipo.equipos:
            raise InspeccionInvalidaError
        else:
            self.equipo = equipo

    def finalizar_inspeccion(self):
        if self.resultado == 'no conforme':
            reporte = Reporte(
                muestra=self._muestra,
                lote=self._muestra.lote,
                profesional=self._profesional,
                fecha=self._fecha,
                causas=self._muestra.defectos
            )
            self._muestra.asignar_reporte(reporte)

class Reporte:
    def _init_(self, muestra, lote, profesional, fecha: datetime, causas: list):
        self._muestra = muestra
        self._lote = lote
        self._profesional = profesional
        self._fecha = fecha
        self._causas = causas

    @property
    def muestra(self):
        return self._muestra

    @property
    def lote(self):
        return self._lote

    @property
    def profesional(self):
        return self._profesional

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def causas(self) -> tuple:
        return self._causas

class DefectoInvalidoError(ValueError):
    pass

class Defecto:
    def _init_(self, tipo, descripcion, gravedad):
        if not tipo or not tipo.strip():
            raise DefectoInvalidoError("El tipo de defecto no puede estar vacío.")
        if not descripcion or not descripcion.strip():
            raise DefectoInvalidoError("La descripción del defecto no puede estar vacía.")
            
        if not isinstance(gravedad, int) or not (1 <= gravedad <= 5):
            raise DefectoInvalidoError("La gravedad debe ser un número entero entre 1 y 5.")
            
        self._tipo = tipo
        self._descripcion = descripcion
        self._gravedad = gravedad

    @property
    def tipo(self):
        return self._tipo

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def gravedad(self):
        return self._gravedad

    def es_critico(self):
        return self._gravedad == 5

class Equipo:
    count=1
    categorias=[]
    equipos = []
    def _init_(self, nombre, ult_calibracion, categoria):
        self.__id__= Equipo.count
        Equipo.count+=1
        self.nombre = nombre
        if nombre not in Equipo.equipos:
            Equipo.equipos.append(nombre)
        self.ult_calibracion = ult_calibracion
        self.categoria = categoria
        if categoria not in Equipo.categorias:
            self.categorias.append(categoria)
    
    @property
    def categoria(self):
        return self.categoria
    
    @property
    def ult_calibracion(self):
        return self.ult_calibracion 
    
    def modificar_fecha_calibracion(self, nueva_fecha):
        self.ult_calibracion = nueva_fecha

class Profesional:
    lista_id_profesional = []

    counter = 1
    def _init_(self, nombre, certificados):

        if nombre =="":
           raise ValueError("El nombre del profesional no puede estar vacío.")
        if not isinstance(certificados, list):
            raise ValueError("Los certificados deben estar en una lista.")

        self.nombre = nombre
        self.certificados = certificados

        self._id_ = Profesional.counter
        Profesional.counter+=1

        Profesional.lista_id_profesional.append(self._id_)
        
    def agregar_certificado(self, certificado):
        self.certificados.append(certificado)

    def tiene_certificado(self, certificado):
        return certificado in self.certificados

    def get_nombre(self):
        return self.nombre 

    def get_certificados(self):
        return self.certificados

    def get_id(self):
        return self._id_

class Procedimiento:
    procedimiento_global=[] 
    counter=1
    def _init_(self,nombre,certificaciones,criterio,pasos, categoria, gravedad_max:int): 
        try :
            self.nombre=nombre
            self.gravedad=gravedad_max
            self.certificaciones=certificaciones
            self.criterio=criterio
            self.categoria=categoria
            self._id_=Procedimiento.counter
            self.pasos=pasos
            Procedimiento.counter+=1
            Procedimiento.procedimiento_global.append(self.nombre)
            
        #Validaciones de contenido NO VACIO

        except nombre == "":
            raise ValueError("El nombre del procedimiento no puede estar vacío")
        except pasos == []:
            raise ValueError("Los pasos del procedimiento no pueden estar vacíos")    
        except  criterio == []:
            raise ValueError("El criterio del procedimiento no puede estar vacío")

        #Validaciones de tipo de datos 
        except not isinstance(criterio, list):
            raise TypeError("El criterio debe ser una lista")
        except not isinstance(pasos, list):
            raise TypeError("Los pasos deben ser una lista")
        except not isinstance(certificaciones, list):
                    raise TypeError("Las certificaciones deben ser una lista")
        except not isinstance(categoria, list):
            raise TypeError("Los categoria deben ser una lista")
        except not isinstance(gravedad_max, int):
            raise TypeError("La gravedad máxima debe ser un entero")


    def agregar_criterio(self,criterio): 
        self.criterio.append(criterio)
    def agregar_certificacion(self,certificacion): 
        self.certificaciones.append(certificacion)
    def agregar_paso(self,paso, posicion): 
        self.pasos.insert(posicion,paso)
    def agregar_categoria(self,categoria): 
        self.categoria.append(categoria)

    #Metodos para obtener informacion sobre el procedimiento
     
    def get_nombre(self): 
        return self.nombre

    def get_categoria(self): 
        return self.categoria
    
    def get_certificaciones(self): 
        return self.certificaciones
    
    def get_criterio(self): 
        return self.criterio
    
    
    def get_pasos(self): 
        return self.pasos

class Muestra:
    muestras_global=[]
    contador=1
    defecto=[]
    def _init_(self, cantidad, lote_asociado, estado):
        self._id_=Muestra.contador
        Muestra.contador+=1
        Muestra.muestras_global.append(self._id_)
        self.cantidad=cantidad
        if lote_asociado in Lote.lotes_global:
            self.lote_asociado=lote_asociado
        else:
            raise ValueError("Lote no válido")
        self.reporte=None
        self.inspeccion= []
        self.conformidad_resultado= None
        self.estado = estado

    def actualizar_estado(self):
        pass