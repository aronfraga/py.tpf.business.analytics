# KPIs pendientes

KPIs que ya están calculados en `src/kpis/` y se usan en los notebooks, pero **ninguna página de la app los muestra**. Para cada uno se indica qué mide, cómo se calcula, qué devuelve, un valor real de ejemplo y dónde mostrarlo.

Todos devuelven una fila por asignatura (columna `materia`), salvo que se indique otra cosa. Los valores de ejemplo salen de los datos actuales.

---

## Participación

### 1. Tiempo promedio en la plataforma
- **Función:** `tiempo_promedio_en_plataforma` (`kpis_participacion.py`)
- **Qué mide:** cuántos minutos usa la plataforma un estudiante, en promedio.
- **Cómo se calcula:** toma el tiempo estimado de uso de cada estudiante matriculado (los que no figuran en el reporte cuentan 0) y calcula el promedio y la mediana por asignatura. Incluye la mediana porque pocos alumnos con uso muy alto inflan el promedio.
- **Devuelve:** `matriculados`, `activos`, `promedio_min_matriculados`, `promedio_min_activos`, `mediana_min_matriculados`.
- **Ejemplo:** Álgebra 229 min de promedio (mediana 217); Algoritmos 206 (171); Probabilidad 406 (370).
- **Dónde:** página General, tarjeta junto a "Promedio de sesiones". Mostrar el promedio y poner la mediana en el detalle de la tarjeta.

### 2. Cobertura de participación
- **Función:** `cobertura_participacion` (`kpis_participacion.py`)
- **Qué mide:** qué porcentaje de los alumnos participó al menos una vez.
- **Cómo se calcula:** alumnos con interacciones mayores a un umbral (0 por defecto) dividido el total de alumnos, por 100. El total incluye a los matriculados y a los no matriculados con actividad. El umbral y la métrica se pueden cambiar (`interacciones`, `tiempo_estimado_de_uso_min`, etc.).
- **Devuelve:** `total_alumnos`, `matriculados`, `no_matriculados_con_actividad`, `con_participacion`, `cobertura_pct`.
- **Ejemplo:** Álgebra 268 de 270 (99,26 %); Algoritmos 276 de 278 (99,28 %); Probabilidad 273 de 276 (98,91 %).
- **Dónde:** página General, tarjeta.
- **Aclaración:** con umbral 0 casi todos participaron, así que el valor casi no varía entre asignaturas. Resulta más informativo con un umbral más alto, por ejemplo más de 100 minutos de uso, y se podría ofrecer con un slider.

---

## Trazabilidad

### 3. Resumen de interacciones
- **Función:** `resumen_interacciones(df, diario)` (`kpis_trazabilidad.py`)
- **Qué mide:** el volumen de actividad promedio de la asignatura.
- **Cómo se calcula:** a partir de la serie diaria de interacciones, saca el total y tres promedios: por día calendario, por día con actividad y por usuario activo y día.
- **Devuelve:** `interacciones_totales`, `dias_calendario`, `dias_con_actividad`, `promedio_diario`, `promedio_diario_dias_con_actividad`, `promedio_por_usuario_activo_y_dia`.
- **Ejemplo:** Álgebra 32.562 interacciones, 402 por día, 9,78 por usuario activo y día; Probabilidad 50.853, 628 por día y 13,21 por usuario.
- **Dónde:** página Participación, fila de tarjetas.
- **Aclaración:** en estos datos hay actividad todos los días (81 de 81), así que el promedio por día y el promedio por día con actividad dan lo mismo.

### 4. Interacciones por día de la semana
- **Función:** `interacciones_por_dia_semana(diario)` (`kpis_trazabilidad.py`)
- **Qué mide:** en qué días de la semana hay más actividad.
- **Cómo se calcula:** promedio de interacciones diarias agrupado por día de la semana, de lunes a domingo.
- **Devuelve:** `materia`, `dia_semana`, `interacciones`.
- **Ejemplo:** en Álgebra el lunes tiene el pico (884 en promedio) y el domingo el mínimo (171).
- **Dónde:** página Participación, gráfico de barras. Complementa el mapa de calor de Trazabilidad, que cruza día y hora.

### 5. Interacciones por acción
- **Función:** `interacciones_por_accion` (`kpis_trazabilidad.py`)
- **Qué mide:** el detalle de qué hacen los estudiantes, a nivel de acción concreta.
- **Cómo se calcula:** cuenta eventos por acción y calcula qué porcentaje del total de la asignatura representa cada una, de mayor a menor.
- **Devuelve:** `accion`, `interacciones`, `porcentaje`.
- **Ejemplo:** en Álgebra, Acceder 14.766 (45,35 %), Ver texto 6.178 (18,97 %), Ver archivo 2.535 (7,79 %), Ver tema 1.865 (5,73 %).
- **Dónde:** página Trazabilidad, debajo de "Interacciones por tipo de acción". Es el mismo dato con más detalle: el gráfico actual agrupa las acciones en seis tipos.

---

## Rendimiento Académico

### 6. Promedio por tipo de evaluación
- **Función:** `promedio_por_tipo_evaluacion` (`kpis_calificaciones.py`)
- **Qué mide:** el desempeño según la categoría de instrumento (autoevaluación, parcial, actividad rápida, etc.).
- **Cómo se calcula:** promedio del porcentaje obtenido sobre el máximo, agrupado por tipo de evaluación.
- **Devuelve:** `tipo_evaluacion`, `estudiantes`, `nota_max` (máximo original del instrumento), `promedio_pct`.
- **Ejemplo:** Álgebra autoevaluación 88,6 % (139 estudiantes) y parcial 80,7 % (126).
- **Dónde:** página Rendimiento Académico. Hoy se muestra el promedio por instrumento individual; este agrupa por categoría y da una vista más resumida.

### 7. Tiempo en la plataforma según condición
- **Función:** `resumen_tiempo_por_condicion` (`kpis_cruces.py`)
- **Qué mide:** si quienes promocionan usan más la plataforma que quienes quedan libres.
- **Cómo se calcula:** minutos de uso, promedio y mediana, agrupados por la condición del alumno (promocionado, regular, libre, no se presentó).
- **Devuelve:** `condicion`, `estudiantes`, `promedio_min`, `mediana_min` (incluye grupos vacíos).
- **Ejemplo:** en Álgebra, promocionado 270 min, regular 172, libre 143, no se presentó 25.
- **Dónde:** página Rendimiento Académico, gráfico de barras junto a la anilla de condiciones, con los mismos colores.

---

## Notas vs Participación

### 8. Nota promedio por tramo de participación
- **Función:** `nota_por_tramo_de_participacion` (`kpis_cruces.py`)
- **Qué mide:** cómo cambia la nota a medida que aumenta el tiempo en la plataforma.
- **Cómo se calcula:** divide a los estudiantes en 4 grupos de igual tamaño según su tiempo (cuartiles; el tramo 1 es el de menor participación) y calcula la nota promedio de cada grupo.
- **Devuelve:** `tramo`, `tiempo_desde_min`, `tiempo_hasta_min`, `estudiantes`, `nota_promedio_pct`.
- **Ejemplo:** en Álgebra la nota sube de 40,5 % (0 a 103 min) a 82,4 %, 84,4 % y 85,1 % en los tramos siguientes.
- **Dónde:** página Notas vs Participación, gráfico de barras debajo de la dispersión. Muestra la relación de forma más clara que los puntos sueltos.

### 9. Prueba de correlación
- **Función:** `prueba_de_correlacion` (`kpis_cruces.py`)
- **Qué mide:** si la relación entre tiempo en plataforma y nota es estadísticamente significativa, y no solo un número.
- **Cómo se calcula:** correlación de Pearson con intervalo de confianza al 95 %, correlación de Spearman y los p-valores de ambas. Marca como significativa la que tiene ambos p-valores menores a 0,05. Con `solo_presentados=True` excluye a quienes no rindieron.
- **Devuelve:** `estudiantes`, `pearson`, `pearson_ic95_inf`, `pearson_ic95_sup`, `pearson_p`, `spearman`, `spearman_p`, `significativa`.
- **Ejemplo:** Álgebra Pearson 0,47 con intervalo de 0,35 a 0,59; Algoritmos 0,45; Probabilidad 0,48.
- **Dónde:** página Notas vs Participación, ampliar la tarjeta de correlación actual agregando el intervalo y la significancia.

### 10. Correlación de indicadores de trazabilidad con la nota
- **Funciones:** `indicadores_de_trazabilidad`, `correlaciones_trazabilidad_nota`, `matriz_correlaciones` e `indicador_mas_relacionado` (`kpis_cruces.py`)
- **Qué mide:** cuál de cinco formas de usar la plataforma se relaciona más con la nota: `dias_activos`, `ingresos`, `semanas_activas`, `interacciones_material` e `interacciones_foros`.
- **Cómo se calcula:** primero arma los cinco indicadores por estudiante. Después calcula la correlación de Spearman de cada uno contra la nota, por asignatura. `matriz_correlaciones` la ordena en una tabla indicador × asignatura, y `indicador_mas_relacionado` elige el de mayor correlación absoluta promedio.
- **Devuelve:** `indicador`, `estudiantes`, `spearman`, `p_valor`, `significativa`.
- **Ejemplo:** el indicador más relacionado es `semanas_activas`. La correlación va de 0,29 (foros en Álgebra) a 0,46 (foros en Algoritmos).
- **Dónde:** página Notas vs Participación, mapa de calor indicador × asignatura con el indicador más relacionado como título. Es el aporte más nuevo de esta lista.

---

## Matrícula y Alertas

### 11. Situación académica
- **Funciones:** `situacion_academica` y `resumen_situacion_academica` (`kpis_matricula.py`)
- **Qué mide:** cómo se reparten los alumnos entre cinco situaciones: promocionado, regular, libre, no se presentó y baja.
- **Cómo se calcula:** cada alumno matriculado recibe una situación. La baja tiene prioridad sobre las demás. "No se presentó" es quien no rindió ningún instrumento. El resto se decide por la nota y los umbrales de cada asignatura. El resumen cuenta y calcula el porcentaje por asignatura e incluye una fila "general" con el total.
- **Devuelve:** `situacion`, `estudiantes`, `porcentaje` (también las situaciones sin estudiantes).
- **Ejemplo (total general):** promocionado 326 (65,3 %), regular 53 (10,6 %), libre 12 (2,4 %), no se presentó 101 (20,2 %), baja 7 (1,4 %).
- **Dónde:** página Matrícula y Alertas, gráfico de barras apiladas o anilla debajo de "Matriculados vs. activos".
- **Aclaración:** la anilla de Rendimiento Académico no incluye "baja" ni "no se presentó". Este KPI sí.

### 12. Comparación entre asignaturas
- **Función:** `comparar_asignaturas` (`kpis_calificaciones.py`)
- **Qué mide:** una tabla resumen para comparar las tres asignaturas.
- **Cómo se calcula:** reúne los KPI de notas y agrega dispersión, diferencia contra el promedio general y avance de la evaluación. Los valores están en porcentaje del total posible. Al comparar hay que recordar que los umbrales para promocionar difieren entre asignaturas.
- **Devuelve:** `estudiantes`, `promedio_pct`, `mediana_pct`, `desvio_pct`, `dif_vs_general_pp` (puntos porcentuales contra el promedio de todos), `pct_promocionados`, `pct_regulares`, `pct_libres`, `avance_evaluacion_pct` (solo en asignaturas acumulativas).
- **Ejemplo:** Álgebra 83,5 % de promedio, desvío 13,8 y 4,2 puntos por debajo del general; Algoritmos 93,5 %, desvío 7,7 y 5,7 puntos por encima.
- **Dónde:** página General, tabla debajo de la distribución de notas.

---

## Qué no llevar a la app

- `graficar_*` (7 funciones de matplotlib en `kpis_calificaciones`, `kpis_cruces` y `kpis_matricula`): son gráficos estáticos para los notebooks. La app ya dibuja con Plotly.
- `comparacion_en_formato_largo` y `validar_contra_participacion`: no se usan ni en la app ni en los notebooks. Evaluar si se eliminan.
- `calcular_kpis_*`: solo agrupan las demás funciones, y la app no las usa.

## Orden sugerido

Primero lo que suma una tarjeta o un gráfico sobre datos ya calculados:
1. Tarjetas de General: tiempo en plataforma (1) y cobertura (2).
2. Detalle por acción en Trazabilidad (5).
3. Situación académica en Matrícula y Alertas (11).
4. Tramo de participación en Notas vs Participación (8).
