# Trabajo Práctico: Sistema de Monitoreo de Calidad Industrial (Six Sigma)

## Situación Hipotética

Imaginemos una empresa de alta tecnología, "QuantumTech Precision", líder en la fabricación de componentes críticos para diversas industrias, incluyendo la automotriz, aeroespacial y médica. La reputación de QuantumTech se basa en la fiabilidad y la calidad intransigente de sus productos. En un entorno donde la más mínima desviación de las especificaciones puede tener consecuencias catastróficas, la empresa ha adoptado un enfoque de control de calidad basado en los principios de Six Sigma, buscando una variabilidad casi nula y una detección proactiva de cualquier anomalía.

El proceso de producción en QuantumTech genera **lotes de componentes**. Cada lote posee un identificador único y una cantidad específica de unidades fabricadas bajo las mismas condiciones. Una vez que un lote está completo, pasa a la fase de inspección.

De cada **lote de componentes**, se extrae un número estadísticamente significativo de **muestras**. Cada muestra representa un subconjunto de componentes individuales del lote y es el objeto de estudio principal para la evaluación de calidad. Estas muestras son asignadas a profesionales de calidad para su evaluación.

La inspección se rige por estrictos **procedimientos de verificación**. Estos procedimientos no son genéricos; están diseñados específicamente para cada tipo de componente o fase de producción. Un procedimiento de verificación detalla qué parámetros deben medirse (ej. dimensiones críticas, peso, resistencia a la tracción, conductividad eléctrica, pureza de materiales, acabado superficial), qué rangos de tolerancia son aceptables y qué **equipos de precisión** deben ser utilizados.

Un **profesional de calidad**, un experto altamente calificado y certificado por la empresa, es el encargado de llevar a cabo las mediciones y verificaciones sobre cada muestra utilizando los equipos apropiados. Durante este proceso, el profesional de calidad registra cualquier desviación de las especificaciones como una **imperfección**. Las imperfecciones tienen diferentes tipos (dimensional, superficial, funcional, etc.) y una **gravedad** asociada que indica su impacto potencial. Una imperfección dimensional, por ejemplo, podría ser un componente con un diámetro fuera de la tolerancia de 0.05 mm, mientras que una imperfección superficial podría ser una micro-fisura.

Si, tras la inspección, una muestra acumula imperfecciones que superan ciertos umbrales de gravedad o si presenta una imperfección clasificada como "Crítica", se emite un **reporte de desviación**. Un reporte de desviación es un registro formal del problema, indicando la muestra afectada, el profesional de calidad que la detectó, las imperfecciones específicas encontradas y una evaluación preliminar del impacto potencial sobre el lote de componentes al que pertenece. Este sistema de reportes de desviación es vital para la trazabilidad, el análisis de causa raíz y la mejora continua, permitiendo a QuantumTech mantener sus estándares de calidad y minimizar el riesgo de productos defectuosos en el mercado.

El sistema que ustedes diseñarán permitirá modelar y gestionar este flujo de trabajo de control de calidad, desde la creación de lotes hasta la detección y registro de desviaciones, facilitando un monitoreo riguroso y una toma de decisiones informada. El objetivo es construir una base sólida que sea extensible, permitiendo incorporar nuevas funcionalidades en el futuro sin la necesidad de un rediseño radical.

## Requerimientos Técnicos Obligatorios

Su diseño y su posterior implementación deben construirse de manera estrictamente **Orientada a Objetos**. Esto implica concebir el sistema como una interacción de componentes que encapsulan tanto sus características como sus comportamientos. Deberán:

-   Modelar el dominio del problema mediante la identificación de los elementos clave y la representación de sus propiedades y acciones.
-   Demostrar la capacidad de estructurar el código de forma jerárquica, permitiendo que elementos especializados compartan funcionalidades generales.
-   Asegurar que diferentes tipos de elementos relacionados puedan ser tratados de manera uniforme, facilitando la flexibilidad y la extensión del sistema.
-   Manejar las situaciones anómalas o las violaciones a las reglas del negocio de una forma controlada y explícita, informando adecuadamente sobre lo ocurrido sin comprometer la estabilidad del sistema.
-   Asegurar la fiabilidad de las distintas partes del sistema, verificando su correcto funcionamiento de manera aislada para garantizar la solidez del conjunto.

## Reglas de Negocio

A continuación, se describen los procesos clave y las condiciones que su sistema debe reflejar y garantizar estrictamente.

1.  Cada partida de producción de componentes debe tener un identificador único y una cantidad definida de piezas. La cantidad de componentes no puede ser un número cero o negativo; el sistema debe señalar esta inconsistencia de forma explícita si se intenta registrar tal cantidad.
2.  Una muestra se clasifica como 'No Conforme' si se detecta en ella al menos una imperfección de 'gravedad' crítica (la máxima) o si la suma total de las gravedades de todas sus imperfecciones excede un cierto límite establecido.
3.  El sistema debe diferenciar entre distintos tipos de imperfecciones, como las que afectan las dimensiones de una pieza y aquellas relacionadas con su superficie. Las imperfecciones dimensionales, por ejemplo, deben poder registrar el valor real medido y el valor que se esperaba, además de una descripción y su nivel de gravedad.
4.  Un equipo de precisión sólo es apto para una inspección si su última calibración fue realizada dentro de los últimos seis meses. Si un profesional de calidad intenta utilizar un equipo cuya calibración ha caducado, el sistema debe impedir la acción y notificar claramente la razón.
5.  Los diversos procedimientos de verificación, como los dimensionales o visuales, deben guiar la evaluación de una muestra por parte de un profesional de calidad y con un equipo específico. Aunque la forma de verificar varía, el sistema debe permitir iniciar la inspección de una muestra de manera uniforme, y cada procedimiento deberá aplicar su lógica particular para identificar y registrar imperfecciones en la muestra.
6.  La gravedad de una imperfección debe estar siempre entre un nivel 'Menor' (1) y 'Crítico' (5). Cualquier intento de registrar una gravedad fuera de este rango válido debe ser rechazado por el sistema, indicando la incorrección.
7.  El estado final de una partida de componentes ('Aprobado' o 'Rechazado') sólo puede definirse una vez que todas las muestras de esa partida han sido completamente inspeccionadas. Si más del 5% de las muestras inspeccionadas resultan 'No Conformes', la partida completa debe ser marcada como 'Rechazada'; en caso contrario, se considera 'Aprobada'.
8.  Cuando se genera un reporte de desviación para una muestra, este registro debe vincularse claramente con la muestra afectada, con el profesional de calidad que identificó el problema y con el listado detallado de las imperfecciones específicas que lo ocasionaron.
9.  Para garantizar la precisión en la evaluación de las partidas, se debe verificar mediante una prueba que, en una partida de 50 muestras, si 3 de ellas son clasificadas como 'No Conformes' (según la condición establecida), el estado final de dicha partida sea 'Rechazado'.
10. Existen diferentes categorías de profesionales de calidad, algunos de ellos con certificaciones especiales para realizar tareas específicas. Ciertos procedimientos de verificación de alta especialización solo pueden ser llevados a cabo por un profesional con la certificación adecuada. Si un profesional sin la certificación requerida intenta ejecutar uno de estos procedimientos, el sistema debe impedírselo y emitir una alerta clara.
11. Una vez que el análisis de una muestra ha concluido y esta ha sido marcada como 'No Conforme', no se pueden añadir nuevas imperfecciones a su registro. Cualquier intento de modificarla en ese estado debe ser rechazado por el sistema.
12. El sistema debe poder calcular y mostrar el número total de imperfecciones de gravedad 'Crítica' (la máxima) que se han detectado en todas las muestras ya inspeccionadas de una determinada partida de componentes.

## Notas
- Se prohíbe el uso de la librería pandas; el objetivo es evaluar el manejo de estructuras nativas (listas, diccionarios) y la lógica de algoritmos manuales.
- Es requisito obligatorio presentar un diagrama de flujo previo a la codificación para organizar la arquitectura lógica y prevenir fallos de diseño.
- Cada implementación debe estar debidamente sustentada; el alumno debe ser capaz de explicar y justificar técnicamente las decisiones tomadas en el código.
- Se recomienda el uso de la librería estándar de Python (como datetime o math) para optimizar tareas específicas y evitar la redacción innecesaria de funciones ya existentes.
