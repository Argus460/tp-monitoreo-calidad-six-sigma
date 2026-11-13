import numpy as np

class Jugador:
    """Representa un jugador del campeonato con sus puntuaciones."""

    def __init__(self, nombre, puntuaciones):
        """
        Parámetros:
            nombre: nombre del jugador.
            puntuaciones: puntajes que obtuvo el jugador en cada partida.
        """
        self.nombre = nombre
        self.puntuaciones = puntuaciones

    def get_nombre(self):
        """Retorna el nombre del jugador."""
        return self.nombre

    def promedio(self):
        """
        Retorna el promedio de las puntuaciones del jugador
        en todas las partidas.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
        """
        return np.mean(self.puntuaciones)