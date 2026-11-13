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
        Calcula una estadística del campeonato usando un método de NumPy
        que no se haya visto en clase. El nombre de este método puede
        cambiarse por uno que describa lo que calcula.

        Requisitos:
            - Usar un método de NumPy no visto en clase.
            - Retornar el resultado obtenido.
            - Explicar en un comentario qué hace el método de NumPy elegido
              y qué información aporta sobre el campeonato.
        """
        pass

    def estadistica_investigada_2(self):
        """
        Calcula una estadística del campeonato usando otro método de NumPy,
        distinto del anterior, que no se haya visto en clase. El nombre de
        este método puede cambiarse por uno que describa lo que calcula.

        Requisitos:
            - Usar un método de NumPy no visto en clase y distinto
              del usado en estadistica_investigada_1.
            - Retornar el resultado obtenido.
            - Explicar en un comentario qué hace el método de NumPy elegido
              y qué información aporta sobre el campeonato.
        """
        pass
