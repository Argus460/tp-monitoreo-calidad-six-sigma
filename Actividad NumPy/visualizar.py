import matplotlib.pyplot as plt


class Visualizador:
    """Genera las gráficas del campeonato usando matplotlib."""

    # Segundos que cada gráfica queda en pantalla antes de cerrarse sola
    TIEMPO_EN_PANTALLA = 5

    @staticmethod
    def grafico_promedios(nombres, promedios):
        """
        Gráfica de BARRAS con el promedio de cada jugador.

        Parámetros:
            nombres: nombres de los jugadores.
            promedios: promedio de cada jugador.

        Requisitos:
            - Una barra por jugador.
            - Rotular ambos ejes e incluir un título.
            - La gráfica debe cerrarse sola después de
              Visualizador.TIEMPO_EN_PANTALLA segundos.
        """
        pass

    @staticmethod
    def grafico_torta(nombres, puntuaciones):
        """
        Gráfica de TORTA con la proporción del puntaje total del campeonato
        que aportó cada jugador.

        Parámetros:
            nombres: nombres de los jugadores.
            puntuaciones: puntajes de los jugadores en cada partida.

        Requisitos:
            - Cada porción debe representar el puntaje total del jugador
              en el campeonato, calculado con NumPy.
            - Cada porción debe llevar el nombre del jugador y su porcentaje.
            - Incluir un título.
            - La gráfica debe cerrarse sola después de
              Visualizador.TIEMPO_EN_PANTALLA segundos.
        """
        pass

    @staticmethod
    def grafico_dispersion(nombres, puntuaciones, partidas):
        """
        Gráfica de DISPERSIÓN con todos los puntajes del campeonato:
        en el eje X las partidas y en el eje Y el puntaje obtenido.

        Parámetros:
            nombres: nombres de los jugadores.
            puntuaciones: puntajes de los jugadores en cada partida.
            partidas: nombres de las partidas.

        Requisitos:
            - Los puntos de cada jugador deben distinguirse de los demás.
            - Mostrar una leyenda para identificar a cada jugador.
            - Rotular ambos ejes e incluir un título.
            - La gráfica debe cerrarse sola después de
              Visualizador.TIEMPO_EN_PANTALLA segundos.
        """
        pass

    @staticmethod
    def grafico_lineas(nombres, puntuaciones, partidas):
        """
        Gráfica de LÍNEAS con la evolución de cada jugador a lo largo
        de las partidas del campeonato.

        Parámetros:
            nombres: nombres de los jugadores.
            puntuaciones: puntajes de los jugadores en cada partida.
            partidas: nombres de las partidas.

        Requisitos:
            - Una línea por jugador, con un marcador en cada punto.
            - Mostrar una leyenda para identificar a cada jugador.
            - Rotular ambos ejes e incluir un título.
            - La gráfica debe cerrarse sola después de
              Visualizador.TIEMPO_EN_PANTALLA segundos.
        """
        pass
