---
type: especificacion
status: planeacion
tags: [mars-challenge, frontend, backend, desarrollo, requerimientos]
---


# Fase 4: Empatía

## Momento 1: Apertura (Mapa de Empatía)

**Definición de nuestro "Astronauta/Ingeniero"**
*   **Nombre:** Elena (o representación de un Agente de IA con recursos limitados).
*   **Edad:** 32 años.
*   **Rol:** Arquitecta de Sistemas Multi-Agente / Orquestadora de IA.
*   **Situación Específica:** Está desarrollando un enjambre de agentes (basados en LLMs locales o de bajo costo) que necesitan diseñar ensamblajes complejos (ej. ecosistemas, flujos de trabajo, rutas). Sus agentes sufren de alucinaciones cuando intentan resolver matemáticas complejas y se quedan sin "ventana de contexto" si intentan evaluar miles de combinaciones. Necesita resultados óptimos sin programar motores matemáticos pesados.

### Lienzo del Mapa de Empatía

**1. ¿Qué necesita hacer?**
*   Encontrar la combinación óptima de elementos (ej. combustible, plantas, recursos) respetando múltiples restricciones (presupuesto, compatibilidad).
*   Delegar la carga computacional pesada fuera del LLM.

**2. ¿Qué ve? (Su entorno)**
*   Ve agentes de IA fallando miserablemente al intentar resolver problemas de optimización matemática mediante simples *prompts*.

**3. ¿Qué dice y hace?**
*   **Dice:** "Mis agentes tardan demasiado y consumen muchísimos tokens intentando adivinar la respuesta correcta."
*   **Dice:** "No quiero reinventar una solución exclusiva cada vez que cambio de dominio."
*   **Hace:** Pierde semanas programando scripts puente en Python para conectar la salida de su IA con motores de cálculo personalizados.

**4. ¿Qué oye?**
*   Escucha a sus clientes pedirle sistemas que tomen decisiones "matemáticamente correctas" y no solo "textualmente coherentes".


**5. ¿Qué piensa? (Preocupaciones)**
*   Teme que si su sistema depende solo del razonamiento del LLM, entregará soluciones inválidas (ej. configuraciones ineficientes, gasto excesivo de recursos).
*   Piensa: "¿Cómo conecto un motor evolutivo complejo sin que mi agente tenga que entender cómo funciona por dentro?"

**6. ¿Qué siente?**
*   **Frustración:** Por tener que reescribir código (reinventar la rueda) para cada nuevo dominio que enfrenta.
*   **Estrés:** Por los costos de tokens y tiempos de respuesta de sus agentes actuales.
*   **Alivio potencial:** Al imaginar un sistema *plug-and-play* donde solo declara el problema y recibe la solución.

---

## Momento 2: Síntesis

**Puntuación y Ordenamiento de Ideas (Top 3):**
1. **Delegación Agnóstica:** El usuario no quiere saber de detalles técnicos. Solo quiere entregar un objetivos y restricciones con sus reglas y recibir las mejores soluciones.
2. **Reducción de carga cognitiva/tokens:** Sacar el cálculo multiobjetivo fuera del agente de lenguaje, ahorrando procesamiento crítico.
3.  **Garantía Anti-Regresión:** Confianza total en que si cambia el dominio, el motor seguirá funcionando

**Conclusión de la Empatía (Impacto en la solución original):**
Este mapa confirma que la visión de **PROTEO** es correcta y necesaria. El problema real del usuario no es "cómo diseñar la configuración más óptima", sino **"cómo darle capacidades de optimización matemática avanzada a un agente de lenguaje sin explotar sus recursos"**. 
La solución debe ser una **Capa MCP estricta**: el agente define el "qué" (el dominio declarativo) y PROTEO se encarga del "cómo" (el motor evolutivo).


# Fase 5: Definición y Detalle del Problema

## Revisión post-empatía
Nuestra solución inicial (un framework de optimización evolutiva genérico) sigue siendo válida, pero la fase de empatía afinó el enfoque: la herramienta no debe ser solo una librería de Python, sino un **servidor estandarizado (MCP)**. El problema fundamental no es la optimización en sí, sino la barrera de integración entre los agentes de lenguaje y los motores de cálculo pesado.

## Los 5 Por Qué (Análisis de Causa Raíz)

**1. ¿Por qué los agentes de IA fallan al diseñar configuraciones óptimas o ensamblajes complejos?**
*Porque intentan resolver problemas de optimización matemática combinatoria usando únicamente generación de lenguaje (predicción de tokens).*

**2. ¿Por qué usan únicamente generación de lenguaje para problemas combinatorios?**
*Porque carecen de herramientas externas robustas y nativas a las que puedan delegar las tareas de cálculo pesado y evaluación de restricciones.*

**3. ¿Por qué no se conectan a herramientas de optimización ya existentes?**
*Porque la mayoría de los optimizadores tradicionales están fuertemente acoplados a un dominio específico (ej. logística, diseño de acuarios, finanzas) y no son fáciles de adaptar "al vuelo".*

**4. ¿Por qué están tan acoplados a sus dominios?**
*Porque programar el motor de búsqueda (el algoritmo) mezclado con la semántica del problema (las reglas del negocio) es la forma más común y tradicional de desarrollarlos.*

**5. ¿Por qué esto impide que los agentes resuelvan nuevos problemas dinámicamente?**
*Porque sin una interfaz agnóstica y estandarizada que separe totalmente la definición del dominio de la mecánica de optimización, el agente (o su desarrollador) se ve obligado a reescribir código para cada nuevo reto.*

**Causa Raíz Identificada:**
La incapacidad de los agentes de IA para resolver problemas combinatorios de forma eficiente se debe a la **ausencia de un protocolo estandarizado que desacople la declaración del problema matemático de su motor de resolución evolutiva**.

## Datos Duros que respaldan el problema
*   **Explosión combinatoria frente a límites de contexto:** Seleccionar una combinación óptima de 10 elementos de un catálogo de 100 genera más de $1.7 \times 10^{13}$ combinaciones posibles. Un LLM moderno (con ventanas de contexto de 128k a 200k tokens) no puede evaluar simultáneamente ni el 0.0001% de este espacio mediante *prompts*.
*   **Consumo de recursos:** Tratar de forzar a un LLM a iterar y evaluar restricciones lógicas complejas multiplica el consumo de *tokens de salida* de forma exponencial, aumentando severamente la latencia y los costos operativos del sistema.

## Definición precisa de la Solución (PROTEO)
**¿Qué hace exactamente?** 
Expone un motor de Algoritmo Genético multiobjetivo, maduro y agnóstico al dominio, a través del protocolo estándar MCP (Model Context Protocol). Recibe configuraciones declarativas y devuelve soluciones óptimas.

**¿A quién ayuda?** 
A agentes de IA con recursos limitados (y a sus arquitectos) que necesitan resolver problemas de configuración y ensamblaje multiobjetivo.

**¿En qué momento aplica?** 
Cuando el agente, en medio de su flujo de trabajo u orquestación, se topa con un problema de optimización donde la precisión matemática y las restricciones rígidas superan su capacidad de razonamiento lingüístico.



# Fase 6: Lienzo Canvas

**Descripción de la solución en una frase:**
Un servidor MCP *plug-and-play* que dota a agentes de IA de capacidades avanzadas de optimización genética, permitiéndoles resolver problemas complejos sin consumir su ventana de contexto ni programar algoritmos propios.

## 1. Segmento de Clientes (¿Para quién es?)
*   Arquitectos y desarrolladores de Sistemas Multi-Agente.
*   Equipos de Data Science y automatización de procesos con IA.
*   (Usuario indirecto): Los propios Agentes Autónomos que operan bajo protocolos como MCP.

## 2. Propuesta de Valor (¿Qué problema resuelve y por qué es único?)
*   **Delegación matemática sin fricción:** Permite a los LLMs resolver problemas combinatorios (ensamblajes, ecosistemas, recursos) que superan su límite de tokens y razonamiento.
*   **Agnosticismo de dominio:** Un solo motor sirve para cualquier problema, configurado puramente a través de peticiones.
*   **Garantía Anti-Regresión:** El "cerebro matemático" está fuertemente probado, evitando las "alucinaciones lógicas" típicas de los LLMs.

## 3. Canales (¿Cómo llega a ellos?)
*   Registros oficiales de servidores MCP.
*   Repositorios de código abierto.
*   Comunidades de desarrollo de IA y foros (Discord de LangChain, LlamaIndex, Reddit).

## 4. Relación con Clientes (¿Cómo interactúan?)
*   **Autoservicio automatizado:** La interacción principal es máquina a máquina vía protocolo estandarizado.
*   Comunidad open-source: Relación basada en documentación clara, contribuciones y reporte de fallos.

## 5. Fuentes de Ingreso (¿Cómo se sostiene?)

*   Desarrollo impulsado por la comunidad *open-source* y adoptantes tempranos.


## 6. Recursos Clave (¿Qué necesitamos?)


## 7. Actividades Clave (¿Qué debemos hacer?)


## 8. Socios Clave (¿Quiénes nos ayudan?)
*   Creadores del estándar MCP que impulsan la adopción del protocolo.
*   Creadores de *frameworks* de agentes donde PROTEO puede ser un "Tool" destacado.

## 9. Estructura de Costos (¿Qué requiere inversión?)
*   Tiempo de desarrollo, diseño y mantenimiento arquitectónico.
*   Costos de cómputo para pruebas de regresión automáticas.
*   Alojamiento web para la documentación y dominios.


# Fase 7: Aplicación y Prototipado Rápido

## 1. Definición del Prototipo
*   **Tipo de Prototipo:** Digital (Diagramas de Arquitectura y Mockups de Interacción).
*   **Propósito:** Demostrar gráficamente la simplicidad de la integración. Queremos responder a la pregunta: *¿Cómo interactúa exactamente un Agente de IA con PROTEO sin abrumarse con la complejidad matemática interna?*

## 2. Proceso de Construcción (Iteraciones)
*Aquí documentamos cómo evolucionó la idea visualmente (evidencia del trabajo del equipo).*

*   **Iteración 1 (Boceto inicial - Descartado):** Se planteó una arquitectura donde el Agente enviaba un *prompt* en lenguaje natural y PROTEO lo interpretaba. 
    * *Retroalimentación:* Era demasiado ineficiente, propenso a errores y rompía la filosofía estructurada de los Algoritmos Genéticos.
*   **Iteración 2 (Ajuste estructural):** Se dibujó un modelo donde el agente mandaba scripts de Python para ejecutar en PROTEO. 
    * *Retroalimentación:* Peligro de seguridad (ejecución de código arbitrario) y no cumplía la promesa de "no programar".
*   **Iteración 3 (Prototipo Final):** Se adoptó el **Modelo Declarativo vía MCP**. El prototipo visual ahora consta de un "enchufe" estandarizado. El agente solo envía un archivo de configuración (YAML/JSON) y recibe una tabla de resultados limpia.

## 3. Descripción del Prototipo Final
El prototipo visualmente se compone de tres bloques interactivos que demuestran el flujo de la solución:

1.  **La Petición (El "Enchufe" de Entrada):**
    Un esquema visual (mockup de código) que muestra al Agente generando un archivo declarativo simple. Define: `catalogo_disponible`, `recursos_maximos`, `objetivos` (ej. minimizar costo, maximizar compatibilidad).
2.  **La Caja Negra (El Servidor PROTEO):**
    Una representación de la capa MCP envolviendo al motor. 
    Visualmente se muestra cómo los datos entran al motor sin que el agente tenga que intervenir en el bucle evolutivo.
3.  **El Resultado:**
    La respuesta que el servidor envía de vuelta al Agente. Un objeto JSON limpio con las mejores soluciones para que el Agente las lea y decida cuál usar.

## 4. Evidencia Visual (Archivos Cargados)
*(Nota: En la plataforma real aquí se suben las imágenes. Para el Grafo de Conocimiento, dejamos los espacios referenciados).*

*  Fotografía de los diagramas de flujo iniciales.*
*  El diseño final en mostrando el Agente ↔ Capa MCP ↔ Motor Genético.
*  Captura de cómo se ve el intercambio de datos simplificado, demostrando la viabilidad técnica.
*  Un video corto (grabación de pantalla) explicando el diagrama de flujo en 1 minuto.



# Fase 8: Retorno al Planeta Tierra

## 1. Impacto Local y Global (Contexto Terrestre)
La optimización matemática de recursos suele estar reservada para grandes corporaciones con presupuestos para software industrial y supercomputadoras. **PROTEO democratiza este poder**. 
Al permitir que agentes de IA locales o de bajo costo resuelvan problemas complejos de optimización multiobjetivo a través de un estándar abierto (MCP), cualquier ONG, universidad o pequeña startup puede diseñar soluciones eficientes. Un agente de IA apoyado por PROTEO puede, en segundos, encontrar la forma más óptima de distribuir recursos limitados tras un desastre natural, o diseñar una granja sostenible maximizando la producción y minimizando el uso de agua.

## 2. Vinculación con los Objetivos de Desarrollo Sostenible (ODS)

Hemos seleccionado **3 ODS principales** en los que PROTEO genera un impacto directo:

### ODS 9: Industria, Innovación e Infraestructura
*   **¿En qué aplica?** PROTEO actúa como una infraestructura tecnológica fundamental para la próxima generación de Sistemas Multi-Agente. 
*   **Justificación y Datos:** Al adoptar el Model Context Protocol (MCP), PROTEO fomenta la innovación abierta. Reduce drásticamente la barrera técnica para que investigadores e ingenieros integren "cerebros de cálculo pesado" en sus IAs sin necesidad de reescribir algoritmos complejos desde cero.

### ODS 12: Producción y Consumo Responsables
*   **¿En qué aplica?** Optimización de cadenas de suministro, logística y uso de materiales.
*   **Justificación y Datos:** La optimización genética es la herramienta ideal para la reducción de desperdicios. Los agentes de IA pueden usar PROTEO para resolver problemas de empaquetamiento (*bin packing*), rutas de distribución (*routing*) o asignación de recursos. Al encontrar los "Frentes de Pareto" (el balance perfecto entre costo y utilidad), las industrias pueden consumir menos materia prima y energía garantizando los mismos resultados.

### ODS 15: Vida de Ecosistemas Terrestres
*   **¿En qué aplica?** Diseño automatizado de ecosistemas resilientes (herencia directa de BioNexo).
*   **Justificación y Datos:** Rescatando el "dominio de referencia" del proyecto, equipos de ecologistas pueden usar agentes conectados a PROTEO para diseñar planes de reforestación masiva o policultivos. El motor puede evaluar miles de combinaciones de especies arbóreas o plantas, seleccionando aquellas que maximizan la compatibilidad biológica y la retención de agua en el suelo, ayudando a revertir la degradación de tierras.

## 3. Síntesis del Retorno a la Humanidad
PROTEO no solo hace que los agentes de IA sean más inteligentes; los hace **matemáticamente responsables**. Al evitar que la IA base sus decisiones de recursos críticos en meras "probabilidades de lenguaje" (alucinaciones), y forzarla a usar un motor de evaluación estricto, garantizamos que las soluciones implementadas en el mundo físico sean sostenibles, viables y óptimas para la humanidad.


# Fase 9: Aterrizaje de la Historia

## Estructura de la Presentación (Guion y Narrativa)

### 1. Apertura Impactante (0:00 - 0:45)
*   **Visual:** Pantalla negra con una pregunta en blanco grande: *"¿Confiarías tu vida a un texto que 'suena bien'?"* Luego, el logo de PROTEO.
*   **Guion:** "Imagina que le pides a un Agente de IA que diseñe el sistema de soporte vital de una base en Marte. El agente genera una respuesta brillante, con gramática perfecta y mucha seguridad. Pero hay un problema fatal: la IA se equivocó en el cálculo de las combinaciones de oxígeno y energía. ¿Por qué? Porque los Modelos de Lenguaje están diseñados para predecir palabras, no para resolver matemáticas combinatorias complejas. Nosotros venimos a darle a la IA un cerebro matemático infalible.  Esto es PROTEO."

### 2. Problemática y Datos (0:45 - 1:30)
*   **Visual:** Gráfico que muestra una "Ventana de Contexto (Tokens)" desbordada por una explosión combinatoria. (Ej. $10^{13}$ combinaciones vs 128k tokens).
*   **Guion:** "El problema real hoy es que los desarrolladores obligan a los agentes a calcular usando *prompts*. Seleccionar una configuración óptima de solo 10 elementos entre 100 genera más de 17 billones de combinaciones. Intentar evaluar esto dentro de un LLM consume una cantidad grotesca de tokens, aumenta los costos, dispara la latencia y, lo peor, casi siempre resulta en alucinaciones o errores lógicos insalvables."

### 3. La Solución (1:30 - 2:30)
*   **Visual:** Animación o esquema simple. Un Agente (Cerebro azul) separándose de la Matemática (Engranajes naranjas) mediante un puente llamado "MCP".
*   **Guion:** "La solución no es hacer LLMs más grandes, sino conectarlos a las herramientas correctas. PROTEO es un servidor de optimización genética estandarizado bajo el Model Context Protocol (MCP). Desacoplamos totalmente el 'qué' del 'cómo'. El agente de IA simplemente nos envía una lista de objetivos y restricciones en un archivo de texto, y PROTEO ejecuta un potente algoritmo evolutivo (agnóstico al dominio) en el fondo, devolviéndole las soluciones matemáticas óptimas. Cero alucinaciones, cero programación extra."

### 4. El Prototipo (2:30 - 3:30)
*   **Visual:** Los esquemas digitales y mockups creados en la Fase 7. (la petición de entrada y el JSON de salida con las soluciones óptimas).
*   **Guion:** "Nuestro prototipo digital demuestra esta arquitectura *plug-and-play*. Como ven aquí, la interacción es limpia. El agente no necesita saber detalles profundos. Solo envía una solicitud, objetivos y reglas. PROTEO lo procesa y devuelve una lista de las mejores configuraciones posibles. El agente lee esto y toma su decisión final."

### 5. Viabilidad (3:30 - 4:15)
*   **Visual:** Resumen visual del Canvas (Iconos de Open-Source, Anthropic, Github).
*   **Guion:** "¿Por qué esto puede funcionar y escalar rápidamente? Porque no estamos inventando un estándar cerrado. Estamos montando un motor algorítmico robusto e iterado sobre el protocolo MCP . Nuestro modelo *open-source* atrae a comunidades de desarrolladores de IA (Sistemas Multi-Agente) que buscan desesperadamente delegar cálculos pesados sin pagar licencias de software industrial."

### 6. Retorno a la Humanidad y Cierre (4:15 - 5:00)
*   **Visual:** Logos de los ODS (9, 12, 15) sobre fondos de innovación, industria y ecosistemas.
*   **Guion:** "Pero PROTEO va más allá del mundo del software. Al democratizar la optimización, hacemos que cualquier ONG o startup pueda usar sus agentes de IA para resolver problemas reales en la Tierra. (ODS 9) Infraestructura tecnológica gratuita; (ODS 12) Optimizar logística para reducir desperdicios industriales; y (ODS 15) Diseñar policultivos ecológicos mediante evaluación de compatibilidad de especies.
PROTEO hace que la Inteligencia Artificial deje de adivinar soluciones y empiece a calcular el futuro."

# Fase 10: Preguntas y Respuestas (Evaluación Intermedia)

## 1. ¿Cuál es el problema que están resolviendo y por qué es importante?
**Problema:** Los agentes de Inteligencia Artificial (basados en LLMs) son pésimos resolviendo problemas de optimización combinatoria matemática debido a sus limitaciones de procesamiento y "ventana de contexto". 
**Importancia:** Es crítico porque mientras dependamos de la predicción de texto para calcular el uso de recursos, diseñar ecosistemas o gestionar infraestructuras, las IAs sufrirán de alucinaciones. No podemos confiar decisiones del mundo físico a un sistema que no está matemáticamente fundamentado.

## 2. ¿Cuál es su solución y cómo funciona de manera general?
**Solución:** PROTEO es un servidor de optimización genética estandarizado bajo el protocolo MCP (Model Context Protocol).
**Cómo funciona:** Actúa como un cerebro matemático externo. El Agente de IA se conecta a PROTEO, le envía un archivo simple definiendo sus reglas, restricciones y objetivos. PROTEO procesa esta información usando un potente Algoritmo Genético (agnóstico al dominio) y le devuelve al agente una lista depurada con las soluciones matemáticamente óptimas. 

## 3. ¿Qué hace diferente a su solución? (Valor agregado o innovación)
El **desacoplamiento total y el agnosticismo de dominio**. Los optimizadores tradicionales requieren programar algoritmos a medida para cada problema nuevo (logística, agricultura, finanzas). PROTEO es *plug-and-play*; utiliza un solo motor evolutivo universal. La IA no necesita saber programar genética, solo necesita declarar el problema. Al usar el protocolo MCP, se convierte en una "Herramienta" (Tool) nativa para cualquier agente moderno.

## 4. ¿Por qué su solución es viable? (2–3 razones clave)
1. **Estándar en crecimiento:** Está construido sobre el protocolo MCP, un estándar emergente respaldado fuertemente por líderes de la industria (como Anthropic), lo que garantiza una fácil integración con los ecosistemas de IA actuales.

2. **Escalabilidad Open-Source:** Su distribución de código abierto elimina la barrera económica para desarrolladores e investigadores, fomentando una rápida adopción en la comunidad de sistemas multi-agente.
