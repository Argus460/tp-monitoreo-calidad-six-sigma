import numpy as np

class RepositorioCSV:
    """Clase encargada de cargar los datos del campeonato desde un archivo CSV."""

    @staticmethod
    def cargar_campeonato(ruta_archivo):
        """
        Lee el archivo CSV del campeonato y separa sus datos en tres arrays de NumPy.

        Formato del CSV (la primera fila es el encabezado):
            Jugador,Partida1,Partida2,Partida3,Partida4,Partida5
            Ana,80,95,78,88,90
            Bruno,60,70,65,75,68
            ...

        Parámetros:
            ruta_archivo (str): ruta al archivo CSV.

        Retorna:
            tuple: (jugadores, puntuaciones, partidas)
                - jugadores (np.ndarray de str, forma (n,)):
                    nombres de los n jugadores. Ej: ['Ana' 'Bruno' ...]
                - puntuaciones (np.ndarray de float, forma (n, 5)):
                    cada fila es un jugador y cada columna una partida.
                    Ej: puntuaciones[0, 1] es el puntaje de Ana
                    en la Partida2 (95.0).
                - partidas (np.ndarray de str, forma (5,)):
                    nombres de las partidas. Ej: ['Partida1' ... 'Partida5']
        """
        # "utf-8-sig" evita un carácter invisible (BOM) que agrega Excel al inicio
        data = np.genfromtxt(ruta_archivo, delimiter=",", dtype=str, encoding="utf-8-sig")
        partidas = data[0, 1:]                       # encabezado sin la columna "Jugador"
        jugadores = data[1:, 0]                      # primera columna sin el encabezado
        puntuaciones = data[1:, 1:].astype(float)    # el resto, convertido a números
        return jugadores, puntuaciones, partidas
