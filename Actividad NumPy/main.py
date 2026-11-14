import numpy as np
from repositorio import RepositorioCSV
from visualizar import Visualizador
from campeonato import Campeonato
from jugador import Jugador
from partida import Partida

# ---------------------------------------------------------------
# Lectura del archivo
# ---------------------------------------------------------------
nombres_jugadores, puntuaciones_jugadores, partidas = RepositorioCSV.cargar_campeonato('campeones/Campeonato.csv')
print("Nombres de jugadores:", nombres_jugadores)
print("Puntuaciones de jugadores:\n", puntuaciones_jugadores)
print("Partidas:", partidas)

# ---------------------------------------------------------------
# Estadísticas del campeonato
# ---------------------------------------------------------------
campeonato = Campeonato(nombres_jugadores, puntuaciones_jugadores, partidas)

campeon, puntaje_mejor = campeonato.mejor_jugador()
print(f"El mejor jugador es {campeon} con un promedio de {puntaje_mejor}")

nombre_peor, puntaje_peor = campeonato.peor_jugador()
print(f"El peor jugador es {nombre_peor} con un promedio de {puntaje_peor}")

print(f"Promedio del campeonato: {campeonato.promedio_general()}")

print(f"Promedio por partida: {campeonato.promedios_por_partida()}")

# ---------------------------------------------------------------
# Métodos de NumPy investigados
# ---------------------------------------------------------------
print(f"Estadística investigada 1: {campeonato.estadistica_investigada_1()}")
print(f"Estadística investigada 2: {campeonato.estadistica_investigada_2()}")

# ---------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------
Visualizador.grafico_promedios(nombres_jugadores, campeonato.promedios_por_jugador())
Visualizador.grafico_torta(nombres_jugadores, puntuaciones_jugadores)
Visualizador.grafico_dispersion(nombres_jugadores, puntuaciones_jugadores, partidas)
Visualizador.grafico_lineas(nombres_jugadores, puntuaciones_jugadores, partidas)

# ---------------------------------------------------------------
# Crear un jugador a partir de los datos del campeonato
# ---------------------------------------------------------------
nombre_buscado = "Ana"

# TODO: usando NumPy, encontrar la ubicación de nombre_buscado en nombres_jugadores
ubicacion = np.where(nombres_jugadores == nombre_buscado)[0][0]

puntuaciones_buscado = puntuaciones_jugadores[ubicacion]
jugador1 = Jugador(nombre_buscado, puntuaciones_buscado)
print(jugador1.get_nombre())
print(jugador1.promedio())

#--------------------------------------------------------------
# Crear una Partida a partir de los datos de campeonato
#--------------------------------------------------------------
nombre_partida = "Partida1"

ubicacion_partida = np.where(partidas == nombre_partida)[0][0]

puntuaciones_partida = puntuaciones_jugadores[:, ubicacion_partida]

partida1 = Partida(
    nombre_partida,
    puntuaciones_partida
)

print(partida1.get_nombre())
print(partida1.promedio())