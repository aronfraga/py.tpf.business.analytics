"""Constantes de todo el proyecto (app Streamlit, capa de datos y KPIs).

Regla: la capa de datos (src/data) y los KPIs (src/kpis) no definen textos, nombres de columnas,
rutas, colores, umbrales ni parámetros de forma suelta; todo se declara acá, con nombre
específico y tipo, y se importa. Las pantallas (src/ui) y app.py conservan sus propios textos.

Secciones:
   1. Rutas y archivos
   2. Caché y mensajes de carga
   3. Asignaturas
   4. Fechas y rangos
   5. Columnas de los datos integrados y de los KPIs
   6. Valores de condición académica y de trazabilidad
   7. Claves de los resultados de los KPIs
   8. Parámetros de los KPIs
   9. Columnas y claves de las tablas que entrega la capa de datos
  10. Textos que arma la capa de datos (tarjetas, alertas, rangos, etiquetas)
  11. Textos y colores de los gráficos estáticos (matplotlib) de los KPIs
"""
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pandas as pd

# =============================================================================
# 1. RUTAS Y ARCHIVOS
# =============================================================================
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_FOLDER_NAME: str = "data"
INTEGRATED_FOLDER_NAME: str = "integrado"
DATA_PATH: Path = PROJECT_ROOT / DATA_FOLDER_NAME
INTEGRATED_PATH: Path = DATA_PATH / INTEGRATED_FOLDER_NAME

PARTICIPATION_FILE: str = "participacion_integrado.parquet"
GRADES_FILE: str = "calificaciones_integrado.parquet"
ENROLLMENT_CROSS_FILE: str = "cruce_matriculados_integrado.parquet"
ENROLLMENT_LIST_FILE: str = "matriculados_integrado.parquet"
TRACEABILITY_FILE: str = "trazabilidad_integrado.parquet"


# =============================================================================
# 2. CACHÉ Y MENSAJES DE CARGA
# =============================================================================
CACHE_TTL_SECONDS: int = 300

SPINNER_LOAD_PARTICIPATION: str = "Cargando participación..."
SPINNER_LOAD_GRADES: str = "Cargando calificaciones..."
SPINNER_LOAD_ENROLLMENT_CROSS: str = "Cargando cruce de matriculados..."
SPINNER_LOAD_ENROLLMENT_LIST: str = "Cargando lista de matriculados..."
SPINNER_LOAD_TRACEABILITY_ALL: str = "Cargando trazabilidad (todos)..."
SPINNER_LOAD_TRACEABILITY_ENROLLED: str = "Cargando trazabilidad (matriculados)..."
SPINNER_BUILD_GENERAL: str = "Calculando indicadores generales..."
SPINNER_BUILD_ACTIVE_INACTIVE: str = "Calculando activos e inactivos..."
SPINNER_BUILD_PARTICIPATION: str = "Calculando participación..."
SPINNER_BUILD_STUDENT_ACTIVITY: str = "Calculando actividad del estudiante..."
SPINNER_BUILD_PERFORMANCE: str = "Calculando rendimiento académico..."
SPINNER_BUILD_TRACEABILITY: str = "Calculando trazabilidad..."
SPINNER_BUILD_ENROLLMENT: str = "Calculando matrícula y alertas..."
SPINNER_BUILD_CORRELATION: str = "Calculando correlaciones..."
SPINNER_BUILD_INDIVIDUAL: str = "Calculando datos individuales..."

# =============================================================================
# 3. ASIGNATURAS
# =============================================================================
ALGEBRA: str = "Álgebra"
ALGORITHMS: str = "Algoritmos y Estructuras de Datos"
PROBABILITY: str = "Probabilidad y Estadística"
SUBJECTS: List[str] = [ALGEBRA, ALGORITHMS, PROBABILITY]

ALGEBRA_KEY: str = "algebra"
ALGORITHMS_KEY: str = "algoritmos"
PROBABILITY_KEY: str = "probabilidad"

SUBJECT_ALL: str = "Todas las asignaturas"
ALL_KEY: str = "todas"
SUBJECT_OPTIONS: List[str] = [SUBJECT_ALL] + SUBJECTS
SUBJECT_KEYS: Dict[str, str] = {
    ALGEBRA: ALGEBRA_KEY,
    ALGORITHMS: ALGORITHMS_KEY,
    PROBABILITY: PROBABILITY_KEY,
    SUBJECT_ALL: ALL_KEY,
}

# Asignaturas cuya nota final es la suma de puntos (las demás promedian sus instrumentos)
CUMULATIVE_SUBJECT_KEYS: List[str] = [ALGEBRA_KEY]

# =============================================================================
# 4. FECHAS Y RANGOS
# =============================================================================
ANCHOR_DATE: pd.Timestamp = pd.Timestamp("2025-10-24")
DATA_START_DATE: pd.Timestamp = pd.Timestamp("2025-08-05")
DATE_FORMAT: str = "%Y-%m-%d"
DAILY_FREQUENCY: str = "D"
WEEKLY_FREQUENCY: str = "W"

RANGE_ALL: str = "Todo el período"
RANGE_4_WEEKS: str = "Últimas 4 semanas"
RANGE_2_WEEKS: str = "Últimas 2 semanas"
DATE_RANGES: List[str] = [RANGE_ALL, RANGE_4_WEEKS, RANGE_2_WEEKS]
DAYS_4_WEEKS: int = 28
DAYS_2_WEEKS: int = 14
RANGE_DAYS: Dict[str, int] = {
    RANGE_4_WEEKS: DAYS_4_WEEKS,
    RANGE_2_WEEKS: DAYS_2_WEEKS,
}

WEEKDAY_MONDAY: str = "lunes"
WEEKDAY_TUESDAY: str = "martes"
WEEKDAY_WEDNESDAY: str = "miércoles"
WEEKDAY_THURSDAY: str = "jueves"
WEEKDAY_FRIDAY: str = "viernes"
WEEKDAY_SATURDAY: str = "sábado"
WEEKDAY_SUNDAY: str = "domingo"
WEEKDAY_NAMES: Dict[int, str] = {
    0: WEEKDAY_MONDAY,
    1: WEEKDAY_TUESDAY,
    2: WEEKDAY_WEDNESDAY,
    3: WEEKDAY_THURSDAY,
    4: WEEKDAY_FRIDAY,
    5: WEEKDAY_SATURDAY,
    6: WEEKDAY_SUNDAY,
}
WEEKDAY_SHORT_LABELS: Dict[str, str] = {
    WEEKDAY_MONDAY: "Lun",
    WEEKDAY_TUESDAY: "Mar",
    WEEKDAY_WEDNESDAY: "Mié",
    WEEKDAY_THURSDAY: "Jue",
    WEEKDAY_FRIDAY: "Vie",
    WEEKDAY_SATURDAY: "Sáb",
    WEEKDAY_SUNDAY: "Dom",
}

# =============================================================================
# 5. COLUMNAS DE LOS DATOS INTEGRADOS Y DE LOS KPIs
# =============================================================================
# --- Identidad del estudiante
SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
ENROLLED_COLUMN: str = "matriculado"
LAST_NAME_COLUMN: str = "apellido"
FIRST_NAME_COLUMN: str = "nombre"
KEY_COLUMNS: List[str] = [SUBJECT_COLUMN, USER_COLUMN]

# --- Fechas y períodos
EVENT_DATE_COLUMN: str = "fecha"
DAY_COLUMN: str = "dia"
WEEKDAY_COLUMN: str = "dia_semana"
WEEKDAY_NUMBER_COLUMN: str = "dia_num"
PERIOD_COLUMN: str = "periodo"
TIME_SLOT_COLUMN: str = "franja"
TIME_SLOT_NUMBER_COLUMN: str = "franja_num"
CUTOFF_DATE_COLUMN: str = "fecha_corte"
WEEK_SOURCE_COLUMN: str = "semana"
START_COLUMN: str = "inicio"
ENROLLMENT_DATE_COLUMN: str = "fecha_inscripcion"
LAST_INTERACTION_COLUMN: str = "ultima_interaccion"

# --- Trazabilidad
SECTION_COLUMN: str = "seccion"
ACTION_SOURCE_COLUMN: str = "accion"
TYPE_COLUMN: str = "tipo"
ENTRY_COLUMN: str = "es_ingreso"
INTERACTIONS_COLUMN: str = "interacciones"
ENTRIES_COLUMN: str = "ingresos"
ACTIVE_USERS_COLUMN: str = "usuarios_activos"
ACTIVE_DAYS_PER_USER_COLUMN: str = "dias_activos_por_usuario"
ENTRIES_PER_ACTIVE_USER_COLUMN: str = "ingresos_por_usuario_activo"
INTERACTIONS_PER_ACTIVE_USER_COLUMN: str = "interacciones_por_usuario_activo"
WHOLE_PERIOD_COLUMN: str = "periodo_completo"
TOTAL_INTERACTIONS_COLUMN: str = "interacciones_totales"
CALENDAR_DAYS_COLUMN: str = "dias_calendario"
DAYS_WITH_ACTIVITY_COLUMN: str = "dias_con_actividad"
DAILY_AVERAGE_COLUMN: str = "promedio_diario"
DAILY_AVERAGE_ACTIVE_DAYS_COLUMN: str = "promedio_diario_dias_con_actividad"
AVERAGE_PER_ACTIVE_USER_AND_DAY_COLUMN: str = "promedio_por_usuario_activo_y_dia"
IS_FORUM_COLUMN: str = "es_foro"
IS_MATERIAL_COLUMN: str = "es_material"
NO_ACTION_LABEL: str = "(sin acción)"

# --- Participación
PARTICIPATES_COLUMN: str = "participa"
IS_ENROLLED_COLUMN: str = "es_matriculado"
ACTIVE_COLUMN: str = "activo"
NEW_SESSION_COLUMN: str = "nueva_sesion"
SESSIONS_SOURCE_COLUMN: str = "sesiones"
ACTIVE_COUNT_COLUMN: str = "activos"
INACTIVE_COUNT_COLUMN: str = "inactivos"
ACTIVE_PERCENT_COLUMN: str = "pct_activos"
INACTIVE_PERCENT_COLUMN: str = "pct_inactivos"
TOTAL_STUDENTS_COLUMN: str = "total_alumnos"
ENROLLED_COUNT_COLUMN: str = "matriculados"
NOT_ENROLLED_WITH_ACTIVITY_COLUMN: str = "no_matriculados_con_actividad"
WITH_PARTICIPATION_COLUMN: str = "con_participacion"
COVERAGE_PERCENT_COLUMN: str = "cobertura_pct"
ESTIMATED_USAGE_MINUTES_COLUMN: str = "tiempo_estimado_de_uso_min"
TIME_MINUTES_COLUMN: str = "tiempo_min"
AVERAGE_ENROLLED_COLUMN: str = "promedio_matriculados"
AVERAGE_ACTIVE_COLUMN: str = "promedio_activos"
MEDIAN_ENROLLED_COLUMN: str = "mediana_matriculados"
AVERAGE_MINUTES_COLUMN: str = "promedio_min"
MEDIAN_MINUTES_COLUMN: str = "mediana_min"
AVERAGE_MINUTES_ENROLLED_COLUMN: str = "promedio_min_matriculados"
AVERAGE_MINUTES_ACTIVE_COLUMN: str = "promedio_min_activos"
MEDIAN_MINUTES_ENROLLED_COLUMN: str = "mediana_min_matriculados"

# --- Calificaciones
INSTRUMENT_SOURCE_COLUMN: str = "instrumento"
FILE_ID_COLUMN: str = "id_archivo"
OBTAINED_COLUMN: str = "nota_obtenida"
MAXIMUM_COLUMN: str = "nota_max"
GRADE_PERCENT_COLUMN: str = "nota_pct"
EVALUATION_TYPE_COLUMN: str = "tipo_evaluacion"
INSTRUMENT_COUNT_COLUMN: str = "instrumentos"
POINTS_OBTAINED_COLUMN: str = "puntos_obtenidos"
POINTS_POSSIBLE_COLUMN: str = "puntos_posibles"
POINTS_EVALUATED_COLUMN: str = "puntos_evaluados"
OBTAINED_SUM_COLUMN: str = "obtenidos"
POSSIBLE_SUM_COLUMN: str = "posibles"
STUDENTS_COLUMN: str = "estudiantes"
AVERAGE_PERCENT_COLUMN: str = "promedio_pct"
MEDIAN_PERCENT_COLUMN: str = "mediana_pct"
STD_PERCENT_COLUMN: str = "desvio_pct"
DIFF_VS_GENERAL_COLUMN: str = "dif_vs_general_pp"
PROMOTED_PERCENT_COLUMN: str = "pct_promocionados"
REGULAR_PERCENT_COLUMN: str = "pct_regulares"
FREE_PERCENT_COLUMN: str = "pct_libres"
EVALUATION_PROGRESS_COLUMN: str = "avance_evaluacion_pct"
RANGE_SOURCE_COLUMN: str = "rango"
DISTRIBUTION_FROM_COLUMN: str = "desde"
DISTRIBUTION_TO_COLUMN: str = "hasta"
PERCENTAGE_COLUMN: str = "porcentaje"
CONDITION_COLUMN: str = "condicion"
INDICATOR_COLUMN: str = "indicador"

# --- Matrícula y alertas
ENROLLED_ACTIVE_COLUMN: str = "matriculados_activos"
NOT_ENROLLED_ACTIVE_COLUMN: str = "no_matriculados_activos"
FLAG_NOT_ENROLLED_ACTIVE: str = "activo_no_inscripto"
FLAG_ACTIVE_WITH_DROP: str = "activo_con_baja"
FLAG_ENROLLED_WITHOUT_ACTIVITY: str = "inscripto_sin_actividad"
ENROLLMENT_STATE_COLUMN: str = "estado_insc"
SITUATION_COLUMN: str = "situacion"

# --- Cruces analíticos
PRESENTED_COLUMN: str = "se_presento"
ACTIVE_DAYS_COLUMN: str = "dias_activos"
ACTIVE_WEEKS_COLUMN: str = "semanas_activas"
MATERIAL_INTERACTIONS_COLUMN: str = "interacciones_material"
FORUM_INTERACTIONS_COLUMN: str = "interacciones_foros"
SIGNIFICANT_COLUMN: str = "significativa"
PEARSON_COLUMN: str = "pearson"
SPEARMAN_COLUMN: str = "spearman"
P_VALUE_COLUMN: str = "p_valor"
PEARSON_P_COLUMN: str = "pearson_p"
SPEARMAN_P_COLUMN: str = "spearman_p"
PEARSON_CI_LOW_COLUMN: str = "pearson_ic95_inf"
PEARSON_CI_HIGH_COLUMN: str = "pearson_ic95_sup"
SLOPE_COLUMN: str = "pendiente_pp_por_hora"
BRACKET_COLUMN: str = "tramo"
ABSOLUTE_R_COLUMN: str = "abs_r"
TIME_FROM_MINUTES_COLUMN: str = "tiempo_desde_min"
TIME_TO_MINUTES_COLUMN: str = "tiempo_hasta_min"
AVERAGE_GRADE_PERCENT_COLUMN: str = "nota_promedio_pct"
GROUP_SOURCE_COLUMN: str = "grupo"

# =============================================================================
# 6. VALORES DE CONDICIÓN ACADÉMICA Y DE TRAZABILIDAD
# =============================================================================
CONDITION_PROMOTED: str = "promocionado"
CONDITION_REGULAR: str = "regular"
CONDITION_FREE: str = "libre"
CONDITION_NOT_PRESENTED: str = "no se presentó"
CONDITION_DROPPED: str = "baja"
SITUATION_GENERAL: str = "general"
ENROLLMENT_STATE_DROPPED: str = "Baja"
CONDITIONS: List[str] = [CONDITION_PROMOTED, CONDITION_REGULAR, CONDITION_FREE]
GROUPS: List[str] = CONDITIONS + [CONDITION_NOT_PRESENTED]
INDICATORS: List[str] = [ACTIVE_DAYS_COLUMN, ENTRIES_COLUMN, ACTIVE_WEEKS_COLUMN, MATERIAL_INTERACTIONS_COLUMN, FORUM_INTERACTIONS_COLUMN]
SITUATIONS: List[str] = [CONDITION_PROMOTED, CONDITION_REGULAR, CONDITION_FREE, CONDITION_NOT_PRESENTED, CONDITION_DROPPED]

TYPE_NAVIGATION: str = "Navegación"
TYPE_STUDY_MATERIAL: str = "Material de estudio"
TYPE_EVALUATIONS: str = "Evaluaciones"
TYPE_FORUMS: str = "Foros y mensajería"
TYPE_GRADES: str = "Calificaciones"
TYPE_OTHERS: str = "Otros"
INTERACTION_TYPES: List[str] = [TYPE_NAVIGATION, TYPE_STUDY_MATERIAL, TYPE_EVALUATIONS, TYPE_FORUMS, TYPE_GRADES, TYPE_OTHERS]

# Las acciones de acceso son navegación (clics) sin importar la sección
NAVIGATION_ACTIONS: Set[str] = {"Acceder", "Acceder actividad"}

SECTION_PROGRAM_TEXTS: str = "Programa > Textos"
SECTION_PROGRAM_MATERIAL: str = "Programa > Material de estudio"
SECTION_FILES: str = "Archivos"
SECTION_PROGRAM_EVALUATIONS: str = "Programa > Evaluaciones"
SECTION_FORUMS: str = "Foros"
SECTION_PROGRAM_TOPICS: str = "Programa > Temas"
SECTION_WEBMAIL: str = "Webmail"
SECTION_MESSAGING: str = "Mensajeria"
SECTION_CONTACTS: str = "Contactos"
TYPE_BY_SECTION: Dict[str, str] = {
    SECTION_PROGRAM_TEXTS: TYPE_STUDY_MATERIAL,
    SECTION_PROGRAM_MATERIAL: TYPE_STUDY_MATERIAL,
    SECTION_FILES: TYPE_STUDY_MATERIAL,
    SECTION_PROGRAM_EVALUATIONS: TYPE_EVALUATIONS,
    TYPE_GRADES: TYPE_GRADES,
    SECTION_FORUMS: TYPE_FORUMS,
    SECTION_PROGRAM_TOPICS: TYPE_FORUMS,
    SECTION_WEBMAIL: TYPE_FORUMS,
    SECTION_MESSAGING: TYPE_FORUMS,
    SECTION_CONTACTS: TYPE_FORUMS,
}

# =============================================================================
# 7. CLAVES DE LOS RESULTADOS DE LOS KPIs
# =============================================================================

# =============================================================================
# 8. PARÁMETROS DE LOS KPIs
# =============================================================================
# Puntos de cada asignatura: (total posible, mínimo para regularizar, mínimo para promocionar)
ALGEBRA_TOTAL_POINTS: int = 120
ALGEBRA_REGULAR_POINTS: int = 60
ALGEBRA_PROMOTION_POINTS: int = 85
PROBABILITY_TOTAL_POINTS: int = 100
PROBABILITY_REGULAR_POINTS: int = 60
PROBABILITY_PROMOTION_POINTS: int = 85
ALGORITHMS_TOTAL_POINTS: int = 100
ALGORITHMS_REGULAR_POINTS: int = 60
ALGORITHMS_PROMOTION_POINTS: int = 90
CONDITION_POINTS: Dict[str, Tuple[int, int, int]] = {
    ALGEBRA_KEY: (ALGEBRA_TOTAL_POINTS, ALGEBRA_REGULAR_POINTS, ALGEBRA_PROMOTION_POINTS),
    PROBABILITY_KEY: (PROBABILITY_TOTAL_POINTS, PROBABILITY_REGULAR_POINTS, PROBABILITY_PROMOTION_POINTS),
    ALGORITHMS_KEY: (ALGORITHMS_TOTAL_POINTS, ALGORITHMS_REGULAR_POINTS, ALGORITHMS_PROMOTION_POINTS),
}

PERCENT_FACTOR: float = 100.0
SCALE_DIVISOR: int = 10
SECONDS_PER_DAY: float = 86400.0
MINUTES_PER_HOUR: int = 60
HOURS_PER_DAY: int = 24
HOURS_PER_TIME_SLOT: int = 4
PARTICIPATION_BRACKET_COUNT: int = 4
ROUND_DECIMALS: int = 2
GRADE_TOLERANCE: float = 1e-9

INACTIVITY_MINUTES: int = 30
SESSION_GAP: pd.Timedelta = pd.Timedelta(minutes=INACTIVITY_MINUTES)
PARTICIPATION_THRESHOLD: int = 0
ACTIVITY_DAYS_LIMIT: int = 15
DEFAULT_INACTIVITY_DAYS: int = ACTIVITY_DAYS_LIMIT
DEFAULT_GRADE_BIN_WIDTH: int = 10
GRADE_SCALE_MAX: int = 100
DISTRIBUTION_BIN_WIDTH: int = 20
HISTOGRAM_BIN_WIDTH: int = 10
SIGNIFICANCE_LEVEL: float = 0.05
CONFIDENCE_LEVEL: float = 0.95

# Límites para describir la intensidad de una correlación
NO_ASSOCIATION_LIMIT: float = 0.1
WEAK_LIMIT: float = 0.3
MODERATE_LIMIT: float = 0.5

# Decimales por tipo de nota
SCATTER_GRADE_DECIMALS: int = 2
INDIVIDUAL_GRADE_DECIMALS: int = 1
RISK_GRADE_DECIMALS: int = 1
AVERAGE_DECIMALS: int = 1
CORRELATION_DECIMALS: int = 3
CORRELATION_TEST_DECIMALS: int = 4
SPEARMAN_DECIMALS: int = 3
P_VALUE_DECIMALS: int = 6

# =============================================================================
# 9. COLUMNAS Y CLAVES DE LAS TABLAS QUE ENTREGA LA CAPA DE DATOS
# =============================================================================
# --- Columnas de las tablas (nombres en inglés que leen los gráficos y las tablas)
COUNT_COLUMN: str = "count"
STATUS_COLUMN: str = "status"
RANGE_COLUMN: str = "range"
WEEK_COLUMN: str = "week"
SESSIONS_COLUMN: str = "sessions"
ACTION_COLUMN: str = "action"
DATE_COLUMN: str = "date"
TIMELINE_COLUMN: str = "interactions"
INSTRUMENT_COLUMN: str = "instrument"
GRADE_COLUMN: str = "grade"
AVERAGE_COLUMN: str = "average"
SUBJECT_NAME_COLUMN: str = "subject"
GROUP_COLUMN: str = "group"
TIME_COLUMN: str = "time_min"
ACCESSES_COLUMN: str = "accesses"
ACTIVITIES_COLUMN: str = "activities"
PERFORMANCE_PERCENT_COLUMN: str = "percent"
USER_TABLE_COLUMN: str = "user"
STUDENT_TABLE_COLUMN: str = "student"
RISK_TABLE_COLUMN: str = "risk"
LAST_ACTIVITY_TABLE_COLUMN: str = "last_activity"
ENROLLMENT_DATE_TABLE_COLUMN: str = "enrollment_date"
LAST_ACCESS_TABLE_COLUMN: str = "last_access"
ALERT_TABLE_COLUMN: str = "alert"
DETAIL_KEY: str = "detail"
TITLE_KEY: str = "title"
VALUE_KEY: str = "value"

# --- Claves de los diccionarios que devuelven los build_all() de cada pantalla
CARDS_KEY: str = "cards"
DISTRIBUTION_KEY: str = "distribution"
TREND_KEY: str = "trend"
CONTEXT_KEY: str = "context"
CONTEXT_ENROLLED_PARTICIPATION_KEY: str = "enrolled_participation"
CONTEXT_ENROLLMENT_CROSS_KEY: str = "enrollment_cross"
CONTEXT_GRADES_TABLE_KEY: str = "grades_table"
CONTEXT_SESSIONS_TABLE_KEY: str = "sessions_table"
NOT_ENROLLED_KEY: str = "not_enrolled"
NO_PARTICIPATION_KEY: str = "no_participation"
ALERTS_KEY: str = "alerts"
INSTRUMENTS_KEY: str = "instruments"
HISTOGRAM_KEY: str = "histogram"
BY_ACTION_KEY: str = "by_action"
HEATMAP_KEY: str = "heatmap"
TIMELINE_KEY: str = "timeline"
SCATTER_KEY: str = "scatter"
CARD_KEY: str = "card"
ACTIVITY_KEY: str = "activity"
CATALOG_KEY: str = "catalog"
GRADES_KEY: str = "grades"
PARTICIPATION_KEY: str = "participation"
TRACEABILITY_KEY: str = "traceability"
TRAFFIC_LIGHTS_KEY: str = "traffic_lights"
PARTICIPATION_SERIES_KEY: str = "participation_series"
NO_GRADES_KEY: str = "no_grades"

# =============================================================================
# 10. TEXTOS QUE ARMA LA CAPA DE DATOS (TARJETAS, ALERTAS, RANGOS, ETIQUETAS)
# =============================================================================
# --- Formatos
ONE_DECIMAL_FORMAT: str = ".1f"
INTEGER_FORMAT: str = ".0f"
TIME_SLOT_LABEL_TEMPLATE: str = "{start:02d}-{end:02d} h"
VALUE_FORMAT: str = ".2f"
ZERO_PERCENT_TEXT: str = "0.0"
STUDENT_ALL: str = "Todos los estudiantes"

# --- Plantillas de texto (se completan con str.format)
RANGE_LABEL_TEMPLATE: str = "{start}-{end}"
WEEK_PREFIX: str = "Sem"
WEEK_LABEL_TEMPLATE: str = "{prefix} {number}"
FULL_NAME_TEMPLATE: str = "{last_name}, {first_name}"
STUDENT_LABEL_TEMPLATE: str = "{user} – {full_name}"
TRAFFIC_LIGHT_PERCENT_TEMPLATE: str = "{text} · {percent}%"
ACTIVE_PERCENT_DETAIL_TEMPLATE: str = "{percent}% de la matrícula"
ACTIVE_OF_ENROLLED_DETAIL_TEMPLATE: str = "{percent}% de los matriculados"
ASSOCIATION_DETAIL_TEMPLATE: str = "Asociación {direction} {strength}"
INACTIVE_REASON_TEMPLATE: str = "Sin actividad hace más de {days} días"
ALERT_DROP_DETAIL_TEMPLATE: str = "Inscripción en estado Baja con {interactions} interacciones; última actividad {last_text}"
ALERT_NOT_ENROLLED_DETAIL_TEMPLATE: str = "No figura en la matrícula; {sessions} sesiones, última actividad {last_text}"

# --- Etiquetas de estado
ENROLLED_LABEL: str = "Matriculados"
ACTIVE_LABEL: str = "Activos"
ENROLLED_WITH_ACTIVITY_LABEL: str = "Con alguna actividad"
INACTIVE_LABEL: str = "Inactivos"
NEVER_LABEL: str = "Nunca"
NOT_PRESENTED_LABEL: str = "No se presentó"
NOT_ENROLLED_LABEL: str = "No inscripto"
CONDITION_LABEL_PROMOTED: str = "Promociona"
CONDITION_LABEL_REGULAR: str = "Regular"
CONDITION_LABEL_FREE: str = "Libre"
CONDITION_LABELS: Dict[str, str] = {
    CONDITION_PROMOTED: CONDITION_LABEL_PROMOTED,
    CONDITION_REGULAR: CONDITION_LABEL_REGULAR,
    CONDITION_FREE: CONDITION_LABEL_FREE,
}
STATUS_ORDER: List[str] = [CONDITION_FREE, CONDITION_REGULAR, CONDITION_PROMOTED]

# --- Tarjetas de la pantalla General
CARD_ENROLLED_DETAIL: str = "Estudiantes inscriptos"
CARD_AVERAGE_GRADE_TITLE: str = "Promedio de notas"
CARD_GRADE_SCALE_DETAIL: str = "Escala de 0 a 10"
CARD_AVERAGE_SESSIONS_TITLE: str = "Promedio de sesiones"
CARD_PER_ACTIVE_STUDENT_DETAIL: str = "Por estudiante activo"

# --- Tarjetas de la pantalla Matrícula y alertas
CARD_OFFICIAL_ENROLLMENTS_DETAIL: str = "Inscripciones oficiales"
NOT_ENROLLED_ACTIVE_TITLE: str = "No inscriptos con alguna actividad"
CARD_NO_ENROLLMENT_DETAIL: str = "Usuarios sin matrícula"
ENROLLED_NO_PARTICIPATION_TITLE: str = "Inscriptos sin participación"
CARD_NEVER_ENTERED_DETAIL: str = "Nunca ingresaron"
ALERTS_LABEL: str = "Alertas"
CARD_ALERTS_DETAIL: str = "Inscripciones a revisar"

# --- Alertas
ALERT_ACTIVE_WITH_DROP: str = "Matriculados dados de baja"
ALERT_NO_ENTRIES: str = "Sin ingresos"
ALERT_NOT_ENROLLED_ACTIVE: str = "No inscripto con alguna actividad"
ALERT_NO_ENTRIES_DETAIL: str = "Inscripción sin ningún ingreso"

# --- Motivos de riesgo y descripción de la correlación
NEVER_ENTERED_REASON: str = "Nunca ingresó"
REASON_SEPARATOR: str = "; "
STRENGTH_VERY_WEAK: str = "muy débil"
STRENGTH_WEAK: str = "débil"
STRENGTH_MODERATE: str = "moderada"
STRENGTH_STRONG: str = "fuerte"
DIRECTION_POSITIVE: str = "positiva"
DIRECTION_NEGATIVE: str = "negativa"
CORRELATION_CARD_TITLE: str = "Correlación tiempo–nota (Pearson)"

# --- Etiquetas de las tablas de la UI (columna -> título visible)
NOT_ENROLLED_ACTIVE_LABELS: Dict[str, str] = {
    USER_TABLE_COLUMN: "Usuario",
    SESSIONS_COLUMN: "Sesiones",
    LAST_ACTIVITY_TABLE_COLUMN: "Última actividad",
}
ENROLLED_NO_PARTICIPATION_LABELS: Dict[str, str] = {
    STUDENT_TABLE_COLUMN: "Estudiante",
    SUBJECT_NAME_COLUMN: "Asignatura",
    ENROLLMENT_DATE_TABLE_COLUMN: "Fecha de inscripción",
    LAST_ACCESS_TABLE_COLUMN: "Último acceso",
}
ALERTS_LABELS: Dict[str, str] = {
    STUDENT_TABLE_COLUMN: "Estudiante",
    ALERT_TABLE_COLUMN: "Alerta",
    DETAIL_KEY: "Detalle",
}
RISK_LABELS: Dict[str, str] = {
    STUDENT_TABLE_COLUMN: "Estudiante",
    RISK_TABLE_COLUMN: "Motivo",
    SESSIONS_COLUMN: "Sesiones",
    GRADE_COLUMN: "Nota",
    LAST_ACTIVITY_TABLE_COLUMN: "Última actividad",
}
GRADES_LABELS: Dict[str, str] = {INSTRUMENT_COLUMN: "Instrumento", GRADE_COLUMN: "Nota"}

# --- Semáforo del estudiante
TRAFFIC_GREEN: str = "green"
TRAFFIC_YELLOW: str = "yellow"
TRAFFIC_RED: str = "red"
TRAFFIC_GRAY: str = "gray"
CONDITION_TRAFFIC_COLORS: Dict[str, str] = {
    CONDITION_PROMOTED: TRAFFIC_GREEN,
    CONDITION_REGULAR: TRAFFIC_YELLOW,
    CONDITION_FREE: TRAFFIC_RED,
}

# =============================================================================
# 11. TEXTOS Y COLORES DE LOS GRÁFICOS ESTÁTICOS (MATPLOTLIB) DE LOS KPIs
# =============================================================================
