import numpy as np

class Campeonato:
    """Coordina jugadores y partidas, y calcula las estadísticas del campeonato."""

    def __init__(self, nombres_jugadores, puntaje_jugadores, partidas):
        """
        Parámetros:
            nombres_jugadores: nombres de los jugadores.
            puntaje_jugadores: puntajes de los jugadores en cada partida.
            partidas: nombres de las partidas.
        """
        self.puntaje_jugadores = puntaje_jugadores
        self.partidas = partidas
        self.nombres_jugadores = nombres_jugadores

    def promedio_general(self):
        """
        Retorna el promedio de todos los puntajes del campeonato.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
        """
        return np.mean(self.puntaje_jugadores)
        

    def mejor_jugador(self):
        """
        Retorna el nombre del jugador con el promedio más alto
        y el valor de ese promedio.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
            - Retornar ambos valores juntos: nombre y promedio.
        """
        promedios = self.promedios_por_jugador()
        indice_mejor = np.argmax(promedios)
        return self.nombres_jugadores[indice_mejor], promedios[indice_mejor]

    def peor_jugador(self):
        """
        Retorna el nombre del jugador con el promedio más bajo
        y el valor de ese promedio.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
            - Retornar ambos valores juntos: nombre y promedio.
        """
        promedios = self.promedios_por_jugador()
        indice_peor = np.argmin(promedios)
        return self.nombres_jugadores[indice_peor], promedios[indice_peor]

    def promedios_por_jugador(self):
        """
        Retorna el promedio de cada jugador en el campeonato,
        en el mismo orden en que aparecen los nombres.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
        """
        return np.mean(self.puntaje_jugadores, axis=1)

    def promedios_por_partida(self):
        """
        Retorna el promedio de cada partida del campeonato,
        en el mismo orden en que aparecen las partidas.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
        """
        return np.mean(self.puntaje_jugadores, axis=0)

    # ------------------------------------------------------------------
    # INVESTIGACIÓN: dos métodos de NumPy que no se hayan visto en clase
    # ------------------------------------------------------------------
    def estadistica_investigada_1(self):
        """
        Retorna la amplitud (rango) de puntajes de cada jugador,
        en el mismo orden en que aparecen los nombres.
        """
        # np.ptp ("peak to peak") calcula la diferencia entre el valor máximo
        # y el mínimo de un arreglo, en un solo paso (equivale a max - min).
        # Con axis=1 lo calcula por fila, es decir, para cada jugador.
        # Aporta una medida de regularidad: una amplitud chica indica un
        # jugador constante en todas las partidas; una grande, un rendimiento
        # irregular.
        return np.ptp(self.puntaje_jugadores, axis=1)

    def estadistica_investigada_2(self):
        """
        Retorna, para cada jugador, en cuántas partidas superó el promedio
        general del campeonato, en el mismo orden en que aparecen los nombres.
        """
        # np.count_nonzero cuenta los elementos distintos de cero de un arreglo;
        # aplicado a una máscara booleana, cuenta cuántos True hay (True vale 1).
        # Con axis=1 cuenta por fila, es decir, para cada jugador.
        # Aporta en cuántas partidas cada jugador rindió por encima del
        # promedio del campeonato: permite distinguir a quien lo supera de
        # forma sostenida de quien lo hace sólo en partidas aisladas.
        superan = self.puntaje_jugadores > self.promedio_general()
        return np.count_nonzero(superan, axis=1)
