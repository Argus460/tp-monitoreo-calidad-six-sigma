import matplotlib.pyplot as plt
import numpy as np


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

        plt.figure(figsize=(10, 6))
        plt.bar(nombres, promedios, color='cornflowerblue', edgecolor='black', alpha=0.85)
        plt.title('Promedio de cada jugador')
        plt.xlabel('Jugadores')
        plt.ylabel('Promedio')
        
        plt.show(block=False) 
        plt.pause(Visualizador.TIEMPO_EN_PANTALLA) 
        plt.close()


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
        

        # Se elige una paleta de colores fija para el grafico
        cmap = plt.get_cmap('Set3')

        # Generamos una variable con los colores dinámicos para cada jugador
        colores_dinamicos = cmap(np.linspace(0, 1, len(nombres)))

        # Pasamos la variable generada al parámetro colors de plt.pie()
        totales = np.sum(puntuaciones, axis=1)
        plt.pie(totales, labels=nombres, 
        autopct='%1.1f%%', startangle=90,
        colors=colores_dinamicos)
        plt.title('Proporción del puntaje total por jugador')
        plt.axis('equal')
        plt.show(block=False) 
        plt.pause(Visualizador.TIEMPO_EN_PANTALLA) 
        plt.close()



        

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
                
        plt.figure(figsize=(10, 6))

                # Iteramos sobre cada jugador usando su índice
        for i in range(len(nombres)):
                    # plt.scatter dibuja los puntos.
                    # X = partidas, Y = puntuaciones del jugador i, label = nombre del jugador i
            plt.scatter(partidas, puntuaciones[i], label=nombres[i])

                # Título y rótulos de los ejes
        plt.title('Puntajes de los jugadores a lo largo del campeonato')
        plt.xlabel('Partidas')
        plt.ylabel('Puntaje Obtenido')

                # Se invoca a la leyenda (usa los 'label' que definimos en el scatter)
        plt.legend()

                # Secuencia de auto-cierre que vimos antes
        plt.show(block=False)
        plt.pause(Visualizador.TIEMPO_EN_PANTALLA)
        plt.close()

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
    
        plt.figure(figsize=(10, 6))

        # Iteramos sobre cada jugador usando su índice
        for i in range(len(nombres)):
            # plt.plot dibuja la línea.
            # X = partidas, Y = puntuaciones del jugador i, label = nombre del jugador i
            plt.plot(partidas, puntuaciones[i], marker='o', label=nombres[i])

        # Título y rótulos de los ejes
        plt.title('Evolución de los puntajes de los jugadores a lo largo del campeonato')
        plt.xlabel('Partidas')
        plt.ylabel('Puntaje Obtenido')

        # Se invoca a la leyenda (usa los 'label' que definimos en el plot)
        plt.legend()

        # Secuencia de auto-cierre que vimos antes
        plt.show(block=False)
        plt.pause(Visualizador.TIEMPO_EN_PANTALLA)
        plt.close()     
