**Universidad de Palermo**  
**BUSINESS INTELLIGENCE & ANALYTICS**

# Trabajo Final Integrador

## **1\. Contextualización**

En el marco de la asignatura *Business Intelligence & Analytics*, se propone un **Trabajo Final Integrador (TFI)** orientado al desarrollo de una **herramienta de análisis y seguimiento académico** a partir de datos reales (mockeados) provenientes de un **LMS (Learning Management System)** institucional.

Este proyecto busca consolidar los conocimientos adquiridos en el curso, aplicando herramientas de análisis de datos, modelado, visualización y diseño de dashboards interactivos. A partir de los datos suministrados, los estudiantes deberán **analizar la participación, trazabilidad y rendimiento académico** de estudiantes de una carrera universitaria, generando reportes visuales e indicadores clave (KPI) de utilidad institucional.

## **2\. Objetivo General**

Desarrollar una **herramienta integral de análisis de desempeño académico** que permita obtener métricas relevantes y dashboards interactivos enfocados en la participación, trazabilidad y calificaciones de estudiantes, así como su relación con la matrícula y el estado de actividad.

## **3\. Objetivos Específicos**

1. Integrar distintas fuentes de datos del LMS (participación, trazabilidad, calificaciones y matrícula).  
2. Realizar un proceso de limpieza, transformación y modelado de los datos.  
3. Diseñar indicadores (KPI) que permitan monitorear el rendimiento académico y la actividad estudiantil.  
4. Desarrollar dashboards interactivos en Streamlit, Power BI, Tableau o herramientas equivalentes.  
5. Implementar reportes individuales y generales que faciliten la toma de decisiones pedagógicas.  
6. Establecer criterios visuales de alerta (por ejemplo, semáforos de rendimiento o inactividad).

## **4\. Descripción de los Datos**

En la carpeta entregada se incluyen varias subcarpetas correspondientes a las asignaturas:

* **Álgebra**  
* **Algoritmos y Estructuras de Datos**  
* **Probabilidad y Estadística**

Cada una contiene los siguientes tipos de archivos:

1. **`reporte_trazabilidad_...`**  
    Contiene el detalle de interacciones de cada usuario: accesos, clics, navegación, tiempos de conexión, materiales visualizados, etc.

2. **`reporte_participacion_...`**  
    Incluye información agregada sobre participación, fechas de primer y último ingreso, tiempo total en la plataforma, cobertura y engagement.

3. **`calificaciones_alumnos_...`**  
    Archivos por cada instrumento de evaluación (parciales, autoevaluaciones, recuperatorios, etc.), con calificaciones por estudiante.

4. **Carpeta `matriculados`**  
    Contiene un archivo por asignatura con los datos de estudiantes **inscriptos oficialmente**. Servirá para contrastar con los registros de participación y detectar casos de estudiantes **no inscriptos pero activos en la cursada**.

## **5\. Esquema Académico por Asignatura**

Cada asignatura presenta un sistema de evaluación distinto:

### **a) Álgebra**

* Parcial 1: 25 puntos  
* Parcial 2: 25 puntos  
* Autoevaluaciones: 10 puntos c/u (son 5\)  
* Recuperatorio: 20 puntos  
* Total máximo: 120 puntos

**Condiciones:**

* Libre: \< 60 puntos  
* Regular: ≥ 60 y \< 85 puntos  
* Promociona: ≥ 85 puntos

👉 *Sistema acumulativo de puntos.*

### **b) Probabilidad y Estadística**

* Cada instrumento vale 100 puntos.  
* El resultado final \= **promedio** de todos los instrumentos.

**Condiciones:**

* Libre: \< 60 puntos  
* Regular: ≥ 60 y \< 85 puntos  
* Promociona: ≥ 85 puntos

### **c) Algoritmos y Estructuras de Datos**

* Solo cuenta con **autoevaluaciones de 100 puntos**.  
* Se obtiene el promedio general.

**Condiciones:**

* Promociona: ≥ 90 puntos  
* Regular: ≥ 60 y \< 90 puntos  
* Libre: \< 60 puntos

## **6\. Requerimientos del Proyecto**

Los estudiantes deberán desarrollar una **herramienta de Business Intelligence** que contenga al menos los siguientes componentes:

### **6.1. Procesamiento de Datos**

* Integración de los archivos de todas las asignaturas.  
* Limpieza, transformación y unificación de fuentes.  
* Estandarización de identificadores (por ejemplo, ID de estudiante).  
* Identificación y tratamiento de duplicados, valores nulos y registros inconsistentes.

### **6.2. KPI a Desarrollar**

Se espera que el trabajo contenga una **selección y justificación de KPI relevantes**, tales como:

**Participación**

* Promedio de sesiones por estudiante.  
* Tiempo promedio en la plataforma.  
* Porcentaje de cobertura de participación.  
* Estudiantes activos vs. inactivos.

**Trazabilidad**

* Cantidad de interacciones por tipo (clicks, materiales, exámenes).  
* Frecuencia de ingreso semanal/mensual.  
* Distribución temporal de actividad.  
* Interacciones promedio por día.

**Calificaciones**

* Promedio general por asignatura.  
* Distribución de notas (histograma).  
* Porcentaje de estudiantes promocionados, regulares y libres.  
* Comparación de resultados entre asignaturas.


**Cruces Analíticos**

* Relación entre participación y notas.  
* Relación entre trazabilidad y rendimiento.  
* Correlación entre tiempo de conexión y calificación final.

**Matrícula**

* Alerta de **estudiantes no inscriptos pero activos.**  
* Mapa de **estudiantes inscriptos pero sin participación.**  
* Gráfico de “situación académica” general y por asignatura.

## **7\. Dashboards Esperados**

El entregable deberá incluir al menos los siguientes dashboards:

### **1️⃣ Dashboard General**

* Resumen consolidado de indicadores por asignatura.  
* Porcentaje de estudiantes activos vs. inactivos.  
* Rendimiento promedio y distribución de calificaciones.  
* Tendencias generales de participación.

### **2️⃣ Dashboard de Participación**

* Actividad por fecha, asignatura y estudiante.  
* Evolución de accesos.  
* Filtros por rango temporal y asignatura.

### **3️⃣ Dashboard de Trazabilidad**

* Interacciones detalladas (clicks, vistas, actividades).  
* Mapa de calor o línea temporal de actividad.

### **4️⃣ Dashboard de Rendimiento Académico**

* Comparación de calificaciones entre instrumentos.  
* Distribución de notas y estados (libre, regular, promocionado).

### **5️⃣ Dashboard de Relación Notas vs Participación**

* Análisis cruzado de engagement y rendimiento.  
* Gráficos de dispersión o correlación.  
* Identificación de patrones o grupos de riesgo.

### **6️⃣ Dashboard Individual**

* Selección de un estudiante (o grupo).  
* Vista personalizada de su participación, notas y trazabilidad.  
* Sistema de alerta tipo “semáforo” (verde \= promociona, amarillo \= regular, rojo \= libre).

### **7️⃣ Dashboard de Matrícula y Alertas**

* Comparación entre estudiantes matriculados y activos.  
* Detección de casos no matriculados pero cursando.  
* Alertas automáticas por asignatura.

## **8\. Entregables**

1. **Informe técnico** (Word o PDF) con:  
   * Descripción del proceso de análisis y limpieza de datos.  
   * Justificación de los KPI seleccionados.  
   * Explicación de los dashboards diseñados.  
   * Interpretación de resultados y conclusiones.  
2. **Dashboard interactivo** con todas las vistas descritas.  
3. **Defensa oral (opcional)** explicando el análisis y los resultados obtenidos si llegaran a terminarlo.

## **9\. Evaluación y Regularización**

Para **regularizar la asignatura**, los estudiantes deberán:

* Presentar **avances significativos** en el desarrollo de los dashboards e indicadores.  
* Entregar **al menos 3 dashboards funcionales** y un informe de avance con KPI calculados.

Para **rendir el final de la asignatura**, deberán:

* Presentar el **TFI completo y funcional**.  
* Justificar los indicadores con base en análisis de datos y buenas prácticas de BI.  
* Defender el proyecto en la mesa de final correspondiente.

**Posibilidad de promoción:** quienes, al finalizar la cursada, hayan completado la totalidad del TFI podrán realizar su defensa en esa misma instancia. **Si aprueban el proyecto y su defensa, la asignatura quedará finalizada y promocionada.** En la instancia de final, únicamente deberán volver a subir el proyecto en el espacio correspondiente para cumplir con la actividad de entrega, sin necesidad de realizar una nueva defensa. 

## **10\. Criterios de Evaluación**

| Criterio | Descripción | Ponderación |
| ----- | ----- | ----- |
| **Integración de datos** | Correcta unión, limpieza y modelado de las fuentes. | 20% |
| **Diseño de KPI** | Relevancia y coherencia de las métricas propuestas. | 20% |
| **Visualización y diseño** | Claridad, interactividad y estética del dashboard. | 20% |
| **Interpretación de resultados** | Análisis crítico, identificación de patrones y conclusiones. | 20% |
| **Comunicación y defensa** | Claridad en la exposición y argumentación técnica. | 20% |

## **11\. Consideraciones Finales**

Este trabajo tiene como finalidad **articular los conocimientos teóricos y prácticos** adquiridos durante la cursada, aplicándolos a un caso concreto de análisis educativo mediante herramientas de Business Intelligence.

El desarrollo deberá reflejar la capacidad del estudiante para **planificar, integrar, analizar y comunicar información compleja** de forma visual, dinámica y orientada a la toma de decisiones.

