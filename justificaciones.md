# Justificación de los KPI y decisiones de diseño

Este documento explica, para cada indicador desarrollado (punto 6.2 del enunciado), **qué mide, por qué se lo eligió y por qué se lo calculó de esa forma**. Los KPI se agrupan como en el enunciado: Participación, Trazabilidad, Calificaciones, Cruces Analíticos y Matrícula. En Matrícula se desarrollaron dos de los tres indicadores del enunciado (ver la sección 5).

Las referencias a datos corresponden al corte del 24/10/2025 (fecha de la última interacción de los reportes).

## Decisiones transversales

Estas decisiones se aplican a todos los KPI y se explican una sola vez.

| Decisión | Motivo |
|---|---|
| **El universo son los estudiantes matriculados** (salvo donde se indica lo contrario). | La matrícula es la fuente oficial de quién cursa. Los reportes de la plataforma listan además a personas no inscriptas, que distorsionarían los promedios. Los no matriculados con actividad se tratan aparte, en el grupo Matrícula (excepto en la cobertura de participación, que los incluye en su universo). |
| **Los matriculados sin actividad cuentan con valor 0** en participación y trazabilidad. | Si solo se promediara a quienes entraron, los promedios quedarían inflados y se ocultaría justamente a quienes no participan. |
| **Los resultados se expresan en porcentajes** y no en puntos absolutos. | Las asignaturas puntúan distinto (Álgebra hasta 120, las otras hasta 100) y se van a cargar más datos a lo largo de la cursada. Con porcentajes, los datos nuevos se suman sin cambiar el cálculo. |
| **Las funciones son puras**: reciben y devuelven DataFrames, sin leer ni escribir archivos. | Se pueden probar, reutilizar y conectar con Streamlit sin efectos secundarios. La lectura de datos se hace en una única función por módulo. |
| **El código vive en módulos `.py` y los notebooks quedan como documentación.** | Streamlit solo importa `.py`. Los notebooks conservan la explicación, los controles y las pruebas de sensibilidad. |
| **Las salidas ya vienen en el formato del gráfico** (por ejemplo, formato largo para barras agrupadas). | Reduce la lógica en la capa de visualización y evita duplicar cálculos. |
| **Se usa la mediana junto al promedio** donde la distribución es asimétrica. | Pocos estudiantes con uso muy alto desplazan el promedio; la mediana representa mejor al estudiante típico. |

**Limitaciones de los datos que afectan a varios KPI**

- **Álgebra tiene datos incompletos.** Solo hay 3 instrumentos cargados (2 autoevaluaciones y el 1° Parcial, 45 de 120 puntos). Faltan el Parcial 2, 3 autoevaluaciones y el recuperatorio. Los resultados de Álgebra reflejan la situación al momento del corte.
- **La trazabilidad no trae identificador de sesión.** Las sesiones se infieren (ver más abajo).
- **Las asociaciones medidas no prueban causalidad.**
- **El campo `matriculado` del cruce incluye a los 7 registros con estado *Baja*** (2 en Álgebra, 2 en Algoritmos y 3 en Probabilidad). Los KPI de participación, trazabilidad, calificaciones y cruces los cuentan como matriculados; solo la situación académica (grupo Matrícula) los distingue como `baja`. El efecto es chico (menos del 2 % de cada asignatura), pero quedaría por decidir si se los excluye del universo.

| Módulo | Contenido |
|---|---|
| [kpis_participacion.py](src/kpis/kpis_participacion.py) | KPI de participación |
| [kpis_trazabilidad.py](src/kpis/kpis_trazabilidad.py) | KPI de trazabilidad |
| [kpis_calificaciones.py](src/kpis/kpis_calificaciones.py) | KPI de calificaciones |
| [kpis_cruces.py](src/kpis/kpis_cruces.py) | Cruces analíticos |
| [kpis_matricula.py](src/kpis/kpis_matricula.py) | KPI de matrícula |

---

## 1. Participación

Documentación ampliada y pruebas de sensibilidad: [participacion.ipynb](src/kpis/participacion.ipynb).

### 1.1 Promedio de sesiones por estudiante

**Qué mide.** Cuántas veces, en promedio, vuelve cada estudiante a la plataforma, por asignatura.

**Justificación.** Mide la **constancia**. El total de interacciones premia a quien hace muchos clics en una sola visita; las sesiones distinguen entre ingresos esporádicos y un hábito sostenido de estudio.

**Decisiones de diseño**
- **Las sesiones se reconstruyen.** El log no trae un identificador de sesión. Una sesión es una secuencia de eventos de un usuario en una asignatura; una pausa mayor a **30 minutos** abre una sesión nueva. El umbral de 30 minutos es una convención habitual en analítica web. Es un parámetro (`UMBRAL_SESION`) y el notebook incluye un análisis de sensibilidad con 15, 30 y 60 minutos.
- **Se cuentan los matriculados sin actividad con 0 sesiones**, para que no inflen el promedio quienes nunca ingresaron.
- **Se informan tres medidas:** promedio sobre todos los matriculados, promedio solo de los activos y mediana. La primera mide la participación de la cohorte; la segunda, la intensidad de quienes sí participan; la tercera es robusta a usos extremos.

**Limitaciones.** El resultado depende del umbral de inactividad elegido.

### 1.2 Tiempo promedio en la plataforma

**Qué mide.** Minutos de uso estimado por estudiante, por asignatura.

**Justificación.** Complementa a las sesiones: dos estudiantes con las mismas sesiones pueden dedicar tiempos muy distintos, y el tiempo acerca la medida a la dedicación real al estudio.

**Decisiones de diseño**
- **Se usa el tiempo ya acumulado del reporte de participación** (`tiempo_estimado_de_uso_min`), que tiene una fila por estudiante y asignatura. No se lo recalcula desde la trazabilidad porque el reporte ya trae esa estimación.
- **Los matriculados que no figuran en el reporte quedan con 0 minutos.**
- **Se incluye la mediana** porque la distribución es asimétrica (pocos estudiantes con uso muy alto).
- **Se separan "matriculados" y "activos"** (tiempo > 0) para distinguir el promedio de la cohorte del promedio de quienes usan la plataforma.

**Limitaciones.** Es una estimación del propio sistema, no tiempo de estudio efectivo.

### 1.3 Porcentaje de cobertura de participación

**Qué mide.** Proporción de alumnos cuya participación supera un umbral, sobre el total de alumnos de la asignatura.

**Justificación.** Responde cuánta parte de la cohorte participa realmente, no solo cuánto participa en promedio.

**Decisiones de diseño**
- **El total (denominador) es la unión de los matriculados y los no matriculados con al menos una interacción.** El reporte de participación lista a todo el padrón de la plataforma en cada aula, por lo que quien no está matriculado y nunca participó no corresponde contarlo. Los no matriculados que sí participaron se incluyen porque cursan de hecho.
- **El umbral es variable** (por defecto 0, es decir, "participó al menos una vez") y **solo cambia el numerador**. El total no depende del umbral, lo que mantiene comparables las coberturas calculadas con distintas exigencias. El notebook muestra la cobertura con umbrales de 0, 50, 100, 250 y 500 interacciones.
- **La métrica evaluada es un parámetro** (`interacciones`, `tiempo_estimado_de_uso_min`, `avance`...), para reutilizar la misma lógica con otras medidas de participación.
- **Se desglosa el resultado** (total, matriculados, no matriculados con actividad, con participación) para que el porcentaje sea trazable.

### 1.4 Estudiantes activos vs. inactivos

**Qué mide.** Cuántos estudiantes están activos y cuántos inactivos, por asignatura.

**Justificación.** La cobertura dice si alguien participó alguna vez; este indicador mide el **estado reciente** y permite detectar a tiempo a quienes se alejaron de la cursada.

**Decisiones de diseño**
- **Activo** es quien tuvo su última interacción dentro de los últimos **N = 15 días**; **inactivo** es quien superó esa ventana o nunca interactuó. N es un parámetro, con análisis de sensibilidad para 5, 7, 15, 30 y 60 días.
- **La fecha de corte es la última interacción registrada en todo el reporte**, y no la fecha del día. Así el resultado es reproducible y no cambia según cuándo se ejecute el análisis.
- **El universo es el mismo que el de la cobertura**, para que ambos indicadores sean consistentes entre sí.
- **Quien nunca interactuó se clasifica como inactivo**, no como dato faltante.

---

## 2. Trazabilidad

Código: [kpis_trazabilidad.py](src/kpis/kpis_trazabilidad.py).

**Definiciones comunes**
- **Interacción:** cada fila del log de trazabilidad (un evento: acceso, clic, vista, descarga).
- **Ingreso:** inicio de una sesión inferida (primer evento de un usuario en una asignatura, o primer evento tras más de 30 minutos sin actividad).
- **Día activo:** día calendario con al menos una interacción del usuario.

### 2.1 Cantidad de interacciones por tipo

**Qué mide.** Cuántas interacciones corresponden a cada tipo de uso (navegación, material, evaluaciones, etc.), por asignatura.

**Justificación.** Muestra **en qué** usan la plataforma los estudiantes, no solo cuánto. Permite ver, por ejemplo, si la actividad es de estudio (material) o solo de navegación.

**Decisiones de diseño**
- **Los 50 tipos de acción del log se agrupan en 6 tipos:** Navegación, Material de estudio, Evaluaciones, Foros y mensajería, Calificaciones y Otros. Tantas categorías serían ilegibles en un gráfico; seis permiten comparar.
- **Las acciones de acceso ("Acceder") se tratan como navegación sin importar la sección**, porque equivalen a los "clics". El resto se clasifica por sección.
- **Las reglas están en un diccionario editable** (`TIPO_POR_SECCION`), de modo que reclasificar una sección es un cambio de una línea.
- **Supuesto a revisar:** la sección "Programa > Temas" se clasificó como Foros y mensajería porque sus acciones son "Agregar intervención" y "Ver participación".
- **Se ofrece también el detalle por acción concreta**, para el gráfico de barras horizontales.
- **Los eventos sin acción registrada se agrupan como "(sin acción)"** en lugar de descartarse, para que los totales coincidan con el log.
- **Se incluyen los tipos sin interacciones** (con 0), para que la tabla sea completa y comparable.

### 2.2 Frecuencia de ingreso semanal y mensual

**Qué mide.** Cuántos ingresos hay por período, cuántos usuarios activos y cuántos días activos por usuario.

**Justificación.** Mide la regularidad con que los estudiantes vuelven, a escala de semana y de mes. Es la contracara temporal de las sesiones.

**Decisiones de diseño**
- **Semanas de lunes a domingo y meses calendario**, los períodos naturales para un calendario académico.
- **Se informan cuatro medidas por período:** ingresos, usuarios activos, ingresos por usuario activo (normaliza por tamaño de cohorte) y días activos por usuario (distingue regularidad de intensidad).
- **Se marca si el período está completo.** Los períodos de los extremos pueden estar cortados por el rango de los datos y no son comparables con los demás; en vez de descartarlos, se los identifica.

### 2.3 Distribución temporal de la actividad

**Qué mide.** Cómo se reparte la actividad por día de la semana y franja horaria.

**Justificación.** Permite saber cuándo estudian los estudiantes (por ejemplo, la concentración de la actividad a la tarde y noche) y sirve de insumo al mapa de calor del dashboard de trazabilidad.

**Decisiones de diseño**
- **Franjas de 4 horas** (6 franjas por día), un nivel de detalle que el mapa de calor muestra con claridad. Es un parámetro (`horas_por_franja`).
- **Se incluyen las combinaciones sin actividad** (con 0), para que la matriz de 7 × 6 esté completa.
- **Se entrega también la matriz lista** (`matriz_dia_franja`) para el componente de mapa de calor.
- **La línea temporal reutiliza la serie diaria** del KPI 2.4, sin duplicar el cálculo.

**Limitaciones.** Los valores son totales y no promedios, por lo que los días de la semana que aparecen más veces en el rango de fechas pesan algo más.

### 2.4 Interacciones promedio por día

**Qué mide.** Cuántas interacciones hay por día, por asignatura.

**Justificación.** Resume el nivel de actividad diaria de cada asignatura y permite ver su evolución.

**Decisiones de diseño**
- **La serie diaria incluye los días sin actividad** (con 0). Si se omitieran, el promedio diario quedaría inflado.
- **Se informan tres promedios**, cada uno responde una pregunta distinta: por día calendario (carga general), por día con actividad (intensidad cuando hay uso) y por usuario activo y día (intensidad individual).
- **Se agrega el promedio por día de la semana**, que alimenta el análisis de patrones semanales.

### Control de consistencia

`validar_contra_participacion` compara los eventos de trazabilidad de cada estudiante con la columna `interacciones` del reporte de participación. Sirve para verificar que ambas fuentes cuentan lo mismo.

---

## 3. Calificaciones

Documentación ampliada: [calificaciones.ipynb](src/kpis/calificaciones.ipynb).

### Criterio común: la nota como porcentaje

Todos los KPI de calificaciones usan la nota de cada estudiante expresada así:

> `nota_pct = suma(nota_obtenida) / suma(nota_max) × 100`

calculada sobre los instrumentos que el estudiante rindió.

**Por qué este criterio**
- **Las asignaturas no usan la misma escala.** En Álgebra las autoevaluaciones valen 10 y el parcial 25; en Probabilidad y Algoritmos cada instrumento vale 100. Promediar notas crudas mezclaría escalas.
- **Los instrumentos no pesan lo mismo.** Se descartó promediar los porcentajes de cada instrumento, porque asignaría el mismo peso a una autoevaluación de 10 puntos que a un parcial de 25. Dividir la suma de puntos obtenidos por la suma de puntos posibles **mantiene el peso relativo** de cada instrumento.
- **Respeta la regla de cada asignatura.** En Álgebra la nota es acumulativa; en las otras dos es el promedio de instrumentos del mismo valor, donde ambos cálculos coinciden.
- **Quien no rindió algo no se penaliza en este cálculo.** Solo cuentan los puntos que tuvo oportunidad de obtener. Esto permite incorporar datos nuevos sin rehacer nada.

### 3.1 Promedio general por asignatura

**Qué mide.** La nota promedio de cada asignatura, de 0 a 100.

**Justificación.** Es el indicador básico de rendimiento y permite ubicar a cada asignatura en una escala común.

**Decisiones de diseño**
- **El promedio se calcula en dos pasos:** primero la nota de cada estudiante y luego el promedio entre estudiantes. Así cada estudiante pesa igual y quien rindió más instrumentos no pesa más.
- **Se informan promedio y mediana**, y el número de estudiantes evaluados.
- **Solo se consideran matriculados** (parámetro `matriculados`).
- **Se agrega el detalle por tipo de evaluación**, para ver qué instrumentos explican el resultado de cada asignatura.
- **Se excluyen las filas sin nota o sin máximo válido** (nulo o ≤ 0), y un control verifica que no queden valores fuera de 0-100 y que el cálculo coincida con la columna `porcentaje` ya presente en los datos.

### 3.2 Distribución de notas (histograma)

**Qué mide.** Cuántos estudiantes hay en cada rango de nota.

**Justificación.** El promedio oculta la forma de la distribución. El histograma muestra si las notas están concentradas, dispersas o repartidas en dos grupos.

**Decisiones de diseño**
- **Rangos de 10 puntos sobre 100** (parámetro `ancho_bin`), comparables entre asignaturas al usar la nota en porcentaje. El último rango incluye el 100.
- **Cada estudiante cuenta una vez por asignatura**, con su nota final. Si se contara cada calificación, los estudiantes con más instrumentos pesarían más.
- **Se incluyen los rangos vacíos** y se calcula el porcentaje sobre el total de la asignatura.
- **La salida es una tabla en formato largo** (una fila por asignatura y rango), insumo directo del histograma de Streamlit. Además se genera una imagen estática.

### 3.3 Porcentaje de estudiantes promocionados, regulares y libres

**Qué mide.** Cuántos estudiantes están en cada condición académica, por asignatura.

**Justificación.** Traduce las notas a la categoría que importa institucionalmente.

**Decisiones de diseño**
- **Los umbrales del enunciado, dados en puntos, se convierten a porcentaje del total posible:**

| Asignatura | Total | Regular desde | Promociona desde |
|---|---|---|---|
| Álgebra | 120 | 60 pts (50 %) | 85 pts (70,83 %) |
| Probabilidad y Estadística | 100 | 60 pts (60 %) | 85 pts (85 %) |
| Algoritmos y Estructuras de Datos | 100 | 60 pts (60 %) | 90 pts (90 %) |

- **La condición se calcula sobre el porcentaje de lo rendido hasta ahora.** Un estudiante con 95 % sobre los puntos rendidos (por ejemplo, 30 de 30) queda promocionado y no libre. Comparar los puntos absolutos con el umbral clasificaría como libre a quien todavía no tuvo oportunidad de sumar. El resultado es el **desempeño actual, no una proyección** de la condición final.
- **Se aplica una tolerancia numérica mínima** para que 85 puntos sobre 120 (70,8333...) no quede fuera del umbral por redondeo.
- **Los umbrales están definidos por asignatura en un diccionario** (`CONDICIONES_PUNTOS`), de modo que agregar una asignatura o cambiar una regla es un cambio de datos y no de código.
- **La salida incluye las condiciones sin estudiantes** y está lista para el gráfico de dona.

### 3.4 Comparación de resultados entre asignaturas

**Qué mide.** Una vista conjunta de los resultados de las tres asignaturas.

**Justificación.** El enunciado pide comparar asignaturas. No es una métrica nueva: es una **vista que reúne los KPI anteriores** y agrega las medidas que solo tienen sentido al comparar.

**Decisiones de diseño**
- **No se inventa un indicador distinto.** La tabla reutiliza los KPI 3.1 y 3.3 y agrega tres medidas:
  - **Dispersión** (desvío estándar de la nota): dos asignaturas con el mismo promedio pueden tener estudiantes muy parejos o muy dispares.
  - **Diferencia contra el promedio general**, en puntos porcentuales.
  - **Avance de la evaluación**: qué parte del total de puntos ya está evaluada.
- **El avance solo se calcula para asignaturas acumulativas** (hoy, Álgebra). En Probabilidad y Algoritmos la nota es un promedio y no hay un total que completar; calcularlo daría valores sin sentido (por ejemplo, más de 100 %). La lista de asignaturas acumulativas es editable.
- **Salida en formato largo** para el gráfico de barras agrupadas.

**Limitaciones.** Los umbrales para promocionar difieren entre asignaturas, así que "más promocionados" no equivale a "mejor rendimiento". Álgebra, con datos parciales, es menos comparable.

---

## 4. Cruces analíticos

Código: [kpis_cruces.py](src/kpis/kpis_cruces.py). Documentación ampliada y resultados: [cruce_participacion_notas.ipynb](src/kpis/cruce_participacion_notas.ipynb).

### Criterios comunes

- **Una fila por estudiante matriculado y asignatura**, con la participación o la trazabilidad y la nota (`nota_pct`, la del grupo Calificaciones).
- **A quienes no se presentaron a ningún instrumento se les asigna nota 0**, y una columna `se_presento` permite separarlos. No es lo mismo no haber rendido que haber sacado 0, por eso se conserva la marca.
- **Doble lectura de cada correlación.** Se calcula con todos los matriculados y solo con quienes se presentaron. Responden preguntas distintas:
  - *Todos:* ¿participar más se asocia a presentarse y obtener resultados?
  - *Solo presentados:* entre quienes rindieron, ¿más participación se asocia a mejor nota?
- **Se usa la correlación de Spearman además de la de Pearson.** Los indicadores de uso tienen distribuciones muy asimétricas; Spearman, que trabaja con el orden y no con los valores, es más robusta.
- **Significancia:** se marca como significativa la correlación con p < 0,05. Con unos 165 estudiantes por asignatura, las correlaciones débiles no son confiables. Las pruebas usan `scipy`.

### 4.1 Relación entre participación y notas

**Qué mide.** Cuánto se relaciona el tiempo en la plataforma con la nota.

**Justificación.** Responde la pregunta de fondo del trabajo: si participar más se traduce en mejor rendimiento.

**Decisiones de diseño**
- **La participación es el tiempo promedio en la plataforma** (KPI 1.2) y la nota es la del KPI 3.1, de modo que el cruce reutiliza los indicadores ya definidos.
- **Se incluye a quienes no se presentaron, con nota 0.** El resultado cambia mucho según este criterio: entre quienes se presentaron no hay relación apreciable (correlación cercana a 0), pero al incluir a los no presentados aparece una correlación moderada de unos 0,45 a 0,48, porque quienes no rindieron usan la plataforma mucho menos. Se adoptó el criterio de incluirlos, y el notebook muestra ambas versiones para que se vea de dónde viene el efecto.
- **Además de la correlación se informa la pendiente** en puntos porcentuales por hora adicional, más fácil de interpretar.
- **Se ofrece la nota promedio por tramos (cuartiles) de participación.** Con una nube de puntos tan dispersa, esta vista muestra la tendencia con más claridad y revela que la relación tiene forma de escalón: los de menor participación concentran a los que no se presentaron.
- **La línea de tendencia se limita al rango válido de la nota (0 a 100).** El ajuste lineal sobre notas agrupadas en 0 y en 80-100 superaba el 100 %, algo imposible para una nota.

**Limitaciones.** La correlación moderada se debe en buena parte a la mezcla de dos grupos (presentados y no presentados), no a una relación gradual dentro del grupo que rindió.

### 4.2 Correlación entre tiempo de conexión y calificación final

**Qué mide.** Lo mismo que el cruce anterior, pero con pruebas estadísticas formales, y el tiempo según la condición académica final.

**Justificación.** Formaliza la relación con evidencia estadística y la conecta con la categoría que importa: promocionado, regular o libre.

**Decisiones de diseño**
- **La calificación final es `nota_pct`.** Es la mejor aproximación con los datos disponibles y se acerca a la nota definitiva a medida que se carguen más instrumentos, sin cambiar el cálculo.
- **Se informan Pearson con intervalo de confianza del 95 % y Spearman, ambos con p-valor.** El intervalo muestra la precisión de la estimación, no solo si es distinta de cero. Se considera significativa cuando ambos p-valores son menores a 0,05.
- **Se compara el tiempo de cada condición** (promocionado, regular, libre) con el de quienes no se presentaron, que se muestran **como grupo aparte** para no mezclarlos con quienes se presentaron y quedaron libres.
- **Se representa con diagramas de caja**, que muestran la mediana y la dispersión de cada grupo.

**Limitaciones.** Los grupos "libre" son muy chicos (de 1 a 7 estudiantes), por lo que sus cifras son poco confiables.

### 4.3 Relación entre trazabilidad y rendimiento

**Qué mide.** Qué comportamientos de uso de la plataforma se asocian más a la nota.

**Justificación.** Complementa al cruce de participación: allí se mide cuánto tiempo pasa el estudiante; acá, **de qué manera** usa la plataforma.

**Decisiones de diseño**
- **Cinco indicadores por estudiante**, que cubren dimensiones distintas:

| Indicador | Qué mide |
|---|---|
| `dias_activos` | En cuántos días distintos tuvo actividad |
| `ingresos` | Cuántas veces volvió |
| `semanas_activas` | Constancia a lo largo del cuatrimestre |
| `interacciones_material` | Estudio efectivo con el material |
| `interacciones_foros` | Participación social |

- **Se excluyen las interacciones de evaluaciones y calificaciones.** Entrar a "Realizar evaluación" es consecuencia de presentarse, por lo que correlacionaría con la nota de forma casi automática y no aportaría información.
- **Tampoco se usa el total de interacciones**, que es casi redundante con el tiempo en la plataforma ya usado en el cruce 4.1.
- **Se muestran las dos versiones** (todos y solo presentados), porque el resultado cambia por completo entre una y otra. Con todos los matriculados, las correlaciones son moderadas y significativas; entre quienes se presentaron, ninguna lo es.
- **El resultado se presenta como una matriz** de indicadores por asignatura (mapa de calor), que permite comparar de un vistazo qué comportamiento se relaciona más con la nota en cada asignatura.
- **Se agrega la dispersión del indicador más relacionado**, elegido por mayor correlación promedio.

**Interpretación.** Estos indicadores sirven como **señal de riesgo de abandono** (quien no entra con constancia tampoco se presenta a evaluar) y no como predictor del rendimiento entre quienes rinden.

---

## 5. Matrícula

Código: [kpis_matricula.py](src/kpis/kpis_matricula.py). Documentación ampliada: [matricula.ipynb](src/kpis/matricula.ipynb).

**Indicadores incluidos.** Se desarrollaron dos de los tres que menciona el enunciado: la alerta de estudiantes no inscriptos pero activos y el gráfico de situación académica. El tercero, el mapa de estudiantes inscriptos pero sin participación, se evaluó y se dejó fuera de la entrega: alcanzaba a muy pocos estudiantes (7 casos, 5 estudiantes distintos, menos del 2 % de los matriculados de cada asignatura) y no justificaba un indicador propio.

**Definiciones comunes**
- **Activo:** estudiante con al menos una interacción en el aula (`interacciones > 0` en el reporte de participación).
- **Matriculado:** figura en el listado oficial de matriculados de esa asignatura (campo `matriculado` del cruce).

### 5.1 Estudiantes activos: matriculados y no matriculados (alerta de no inscriptos pero activos)

**Qué mide.** Cuántos estudiantes activos de cada asignatura están matriculados y cuántos no. Los no matriculados activos son la alerta: usan el aula sin figurar como inscriptos.

**Justificación.** La matrícula es la fuente oficial de quién cursa. Un estudiante que usa el aula sin estar inscripto es un caso que requiere revisión administrativa (inscripción pendiente, acceso por otra vía o inscripción dada de baja), y además queda fuera de los demás KPI, que trabajan solo con matriculados.

**Decisiones de diseño**
- **Activo es quien tuvo interacciones, y no quien figura en el reporte.** El reporte de participación lista a todo el padrón de la plataforma en cada aula (319 personas por asignatura), incluso a quienes nunca entraron. Si se contara la mera presencia en el reporte, casi todo el padrón aparecería como "activo".
- **La salida es deliberadamente simple:** dos conteos por asignatura (matriculados activos y no matriculados activos) y el listado de los no matriculados. Se evaluó una versión con niveles de gravedad de la alerta y detalle por estudiante (sesiones, tiempo, evaluaciones rendidas, etc.) y se la descartó: el enunciado pide una alerta, y los conteos más el listado alcanzan para actuar sin sobrecargar el indicador.
- **Control contra la integración:** las cantidades se verifican contra el resumen que genera el proceso de integración (`resumen_integracion`), de modo que ambos cálculos se validan entre sí.

**Lectura del resultado.** Cerca del 40 % de los usuarios activos de cada aula no figura en la matrícula (105 no matriculados activos frente a 163 matriculados activos en Álgebra, 111 frente a 165 en Algoritmos y 109 frente a 164 en Probabilidad). Es una proporción alta que justifica el indicador como alerta.

**Limitaciones.** El indicador detecta el caso pero no su causa. Además, el campo `matriculado` incluye a los registros con estado *Baja* (ver las limitaciones generales), por lo que quienes dieron de baja su inscripción y siguen activos se cuentan como matriculados.

### 5.2 Situación académica general y por asignatura

**Qué mide.** Cómo se distribuyen los estudiantes matriculados según su situación académica, en cada asignatura y en el conjunto de todas.

**Justificación.** Es la mirada de matrícula sobre el rendimiento. El KPI de promocionados, regulares y libres (3.3) solo clasifica a quienes ya rindieron; este gráfico cubre **toda** la matrícula, e incorpora a quienes todavía no se presentaron y a quienes dieron de baja. Muestra de un vistazo cuánta gente está en cada situación.

**Decisiones de diseño**
- **Cinco situaciones:** promocionado, regular, libre, no se presentó y baja. Las tres primeras reutilizan la condición del KPI 3.3 (mismos umbrales, expresados en porcentaje del total posible), para que ambos indicadores sean coherentes entre sí.
- **"No se presentó" se separa de "libre".** Quien no rindió ningún instrumento no tiene un desempeño bajo: no tiene desempeño medido todavía. Mezclarlos clasificaría como libres a estudiantes que simplemente no tuvieron oportunidad de sumar puntos.
- **"Baja" tiene prioridad sobre las demás situaciones.** Un estudiante que dio de baja su inscripción no debe clasificarse por sus notas.
- **La situación es el desempeño actual, no una proyección** de la condición final. A medida que se carguen más instrumentos, los estudiantes pasarán de "no se presentó" a las demás situaciones sin cambiar el cálculo.
- **El resultado general suma todos los pares estudiante-asignatura.** Un estudiante que cursa varias asignaturas cuenta una vez en cada una, lo que mantiene el total consistente con los matriculados de cada asignatura (control incluido en el notebook).
- **La salida es una tabla en formato largo** (asignatura, situación, estudiantes, porcentaje) con una fila "general" e incluyendo las situaciones sin estudiantes, lista para un gráfico de dona o de barras de Streamlit. Además se genera una imagen de barras horizontales al 100 %, que permite comparar asignaturas en la misma escala.

**Limitaciones.** Álgebra tiene datos incompletos (ver las limitaciones generales), y el alto porcentaje de "no se presentó" en Algoritmos (35 %, frente a 13 % en las otras dos) puede deberse en parte a instrumentos todavía no cargados o no rendidos.
