import numpy as np
class Partida:
    """Representa una partida del campeonato con los puntajes obtenidos en ella."""

    def __init__(self, nombre, puntuaciones):
        """
        Parámetros:
            nombre: nombre de la partida.
            puntuaciones: puntajes que obtuvieron todos los jugadores en esta partida.
        """
        self.nombre = nombre
        self.puntuaciones = puntuaciones

    def get_nombre(self):
        """Retorna el nombre de la partida."""
        return self.nombre

    def promedio(self):
        """
        Retorna el promedio de los puntajes obtenidos por todos
        los jugadores en esta partida.

        Requisitos:
            - El cálculo debe realizarse con NumPy.
        """
        return np.mean(self.puntuaciones)

