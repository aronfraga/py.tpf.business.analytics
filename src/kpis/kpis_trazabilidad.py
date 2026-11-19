"""KPIs de trazabilidad: interacciones por tipo, frecuencia de ingreso, distribución temporal e interacciones por día.

Entrada : data/integrado/trazabilidad_integrado.parquet (generado por integracion.ipynb)
          La carpeta data/ se busca en la raíz del proyecto (dos niveles arriba de src/kpis/).
Salida  : DataFrames de pandas (no se escriben archivos).

Definiciones (ajustables):
  - Interacción : cada fila de trazabilidad (un evento: acceso, clic, navegación).
  - Ingreso     : inicio de una sesión. La trazabilidad no trae un identificador de sesión, así que una
                  sesión nueva empieza con el primer evento de un usuario (en una materia) o con el
                  primer evento después de más de `minutos_inactividad` (30 por defecto) sin actividad.
  - Día activo  : día calendario en el que el usuario tuvo al menos una interacción.
  - Tipo        : clasificación de cada interacción según su sección y acción (ver TIPO_POR_SECCION):
                  navegación (clics de acceso), material de estudio, evaluaciones, foros y mensajería,
                  calificaciones y otros.
"""
import sys
from pathlib import Path

import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[1])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
from constants import (
    ACTION_SOURCE_COLUMN,
    ACTIVE_DAYS_PER_USER_COLUMN,
    ACTIVE_USERS_COLUMN,
    AVERAGE_PER_ACTIVE_USER_AND_DAY_COLUMN,
    CALENDAR_DAYS_COLUMN,
    DAILY_AVERAGE_ACTIVE_DAYS_COLUMN,
    DAILY_AVERAGE_COLUMN,
    DAILY_FREQUENCY,
    DAYS_WITH_ACTIVITY_COLUMN,
    DAY_COLUMN,
    ENROLLED_COLUMN,
    ENROLLMENT_CROSS_FILE,
    ENTRIES_COLUMN,
    ENTRIES_PER_ACTIVE_USER_COLUMN,
    ENTRY_COLUMN,
    EVENT_DATE_COLUMN,
    HOURS_PER_DAY,
    HOURS_PER_TIME_SLOT,
    INACTIVITY_MINUTES,
    INTEGRATED_FOLDER_NAME,
    INTERACTIONS_COLUMN,
    INTERACTIONS_PER_ACTIVE_USER_COLUMN,
    INTERACTION_TYPES,
    NAVIGATION_ACTIONS,
    NO_ACTION_LABEL,
    PERCENTAGE_COLUMN,
    PERCENT_FACTOR,
    PERIOD_COLUMN,
    ROUND_DECIMALS,
    SECTION_COLUMN,
    START_COLUMN,
    SUBJECT_COLUMN,
    TIME_SLOT_COLUMN,
    TIME_SLOT_LABEL_TEMPLATE,
    TIME_SLOT_NUMBER_COLUMN,
    TOTAL_INTERACTIONS_COLUMN,
    TRACEABILITY_FILE,
    TYPE_BY_SECTION,
    TYPE_COLUMN,
    TYPE_NAVIGATION,
    TYPE_OTHERS,
    USER_COLUMN,
    WEEKDAY_COLUMN,
    WEEKDAY_NAMES,
    WEEKDAY_NUMBER_COLUMN,
    WHOLE_PERIOD_COLUMN,
)

DIAS_SEMANA = WEEKDAY_NAMES


# Tipo de interacción: las acciones de acceso son navegación (clics) sin importar la sección; el resto
# se clasifica por sección. Lo que no figura acá cae en OTROS_TIPO.
ACCIONES_NAVEGACION = NAVIGATION_ACTIONS
TIPO_NAVEGACION = TYPE_NAVIGATION
OTROS_TIPO = TYPE_OTHERS
TIPO_POR_SECCION = TYPE_BY_SECTION
TIPOS = INTERACTION_TYPES


# ----------------------------------------------------------------------------
# Carga
# ----------------------------------------------------------------------------
def cargar_trazabilidad(datos, solo_matriculados=False):
    df = pd.read_parquet(datos / INTEGRATED_FOLDER_NAME / TRACEABILITY_FILE,
                         columns=[SUBJECT_COLUMN, USER_COLUMN, EVENT_DATE_COLUMN, SECTION_COLUMN, ACTION_SOURCE_COLUMN])
    if solo_matriculados:
        cruce = pd.read_parquet(datos / INTEGRATED_FOLDER_NAME / ENROLLMENT_CROSS_FILE,
                                columns=[SUBJECT_COLUMN, USER_COLUMN, ENROLLED_COLUMN])
        inscriptos = cruce.loc[cruce[ENROLLED_COLUMN], [SUBJECT_COLUMN, USER_COLUMN]]
        df = df.merge(inscriptos, on=[SUBJECT_COLUMN, USER_COLUMN], how="inner")
    df[DAY_COLUMN] = df[EVENT_DATE_COLUMN].dt.normalize()
    return df


def marcar_ingresos(df, minutos_inactividad=INACTIVITY_MINUTES):
    """Agrega la columna booleana `es_ingreso` (primer evento de cada sesión inferida)."""
    df = df.sort_values([SUBJECT_COLUMN, USER_COLUMN, EVENT_DATE_COLUMN]).reset_index(drop=True)
    pausa = df.groupby([SUBJECT_COLUMN, USER_COLUMN])[EVENT_DATE_COLUMN].diff()
    df[ENTRY_COLUMN] = pausa.isna() | (pausa > pd.Timedelta(minutes=minutos_inactividad))
    return df


# ----------------------------------------------------------------------------
# KPI 1: frecuencia de ingreso semanal / mensual
# ----------------------------------------------------------------------------
def frecuencia_ingreso(df, freq):
    """freq: 'W' (semanas de lunes a domingo) o 'M' (meses calendario). Una fila por materia y período."""
    d = df.assign(**{PERIOD_COLUMN: df[EVENT_DATE_COLUMN].dt.to_period(freq)})
    ingresos = d[d[ENTRY_COLUMN]].groupby([SUBJECT_COLUMN, PERIOD_COLUMN]).size().rename(ENTRIES_COLUMN)
    activos = d.groupby([SUBJECT_COLUMN, PERIOD_COLUMN])[USER_COLUMN].nunique().rename(ACTIVE_USERS_COLUMN)
    dias = (d.groupby([SUBJECT_COLUMN, PERIOD_COLUMN, USER_COLUMN])[DAY_COLUMN].nunique()
              .groupby([SUBJECT_COLUMN, PERIOD_COLUMN]).mean().rename(ACTIVE_DAYS_PER_USER_COLUMN))

    res = pd.concat([ingresos, activos, dias], axis=1).reset_index()
    res[ENTRIES_COLUMN] = res[ENTRIES_COLUMN].fillna(0).astype(int)
    res[ENTRIES_PER_ACTIVE_USER_COLUMN] = (res[ENTRIES_COLUMN] / res[ACTIVE_USERS_COLUMN]).round(ROUND_DECIMALS)
    res[ACTIVE_DAYS_PER_USER_COLUMN] = res[ACTIVE_DAYS_PER_USER_COLUMN].round(ROUND_DECIMALS)

    # Los períodos de los extremos pueden estar cortados por el rango de los datos
    rangos = df.groupby(SUBJECT_COLUMN)[DAY_COLUMN].agg(["min", "max"])
    inicio = res[PERIOD_COLUMN].dt.start_time
    fin = res[PERIOD_COLUMN].dt.end_time.dt.normalize()
    res[WHOLE_PERIOD_COLUMN] = (inicio >= res[SUBJECT_COLUMN].map(rangos["min"])) & (fin <= res[SUBJECT_COLUMN].map(rangos["max"]))
    res.insert(1, START_COLUMN, inicio.dt.date)
    res[PERIOD_COLUMN] = res[PERIOD_COLUMN].astype(str)
    return res


# ----------------------------------------------------------------------------
# KPI 2: interacciones promedio por día
# ----------------------------------------------------------------------------
def interacciones_diarias(df):
    """Serie diaria por materia con todos los días del rango (incluye los días sin actividad)."""
    piezas = []
    for materia, g in df.groupby(SUBJECT_COLUMN):
        diario = g.groupby(DAY_COLUMN).agg(**{INTERACTIONS_COLUMN: (USER_COLUMN, "size"), ACTIVE_USERS_COLUMN: (USER_COLUMN, "nunique")})
        rango = pd.date_range(g[DAY_COLUMN].min(), g[DAY_COLUMN].max(), freq=DAILY_FREQUENCY)
        diario = diario.reindex(rango, fill_value=0).rename_axis(DAY_COLUMN).reset_index()
        diario.insert(0, SUBJECT_COLUMN, materia)
        piezas.append(diario)
    d = pd.concat(piezas, ignore_index=True)
    d[INTERACTIONS_PER_ACTIVE_USER_COLUMN] = (d[INTERACTIONS_COLUMN] / d[ACTIVE_USERS_COLUMN]).where(d[ACTIVE_USERS_COLUMN] > 0).round(ROUND_DECIMALS)
    d[WEEKDAY_COLUMN] = d[DAY_COLUMN].dt.dayofweek.map(DIAS_SEMANA)
    return d


def resumen_interacciones(df, diario):
    """Promedios por materia: por día calendario, por día con actividad y por usuario activo y día."""
    res = diario.groupby(SUBJECT_COLUMN).agg(
        **{TOTAL_INTERACTIONS_COLUMN: (INTERACTIONS_COLUMN, "sum"), CALENDAR_DAYS_COLUMN: (DAY_COLUMN, "size"), DAYS_WITH_ACTIVITY_COLUMN: (INTERACTIONS_COLUMN, lambda s: int((s > 0).sum()))},
    )
    res[DAILY_AVERAGE_COLUMN] = res[TOTAL_INTERACTIONS_COLUMN] / res[CALENDAR_DAYS_COLUMN]
    res[DAILY_AVERAGE_ACTIVE_DAYS_COLUMN] = res[TOTAL_INTERACTIONS_COLUMN] / res[DAYS_WITH_ACTIVITY_COLUMN]
    usuario_dia = df.groupby([SUBJECT_COLUMN, USER_COLUMN, DAY_COLUMN]).size()
    res[AVERAGE_PER_ACTIVE_USER_AND_DAY_COLUMN] = usuario_dia.groupby(SUBJECT_COLUMN).mean()
    return res.round(ROUND_DECIMALS).reset_index()


def interacciones_por_dia_semana(diario):
    """Promedio de interacciones según el día de la semana (lunes a domingo)."""
    orden = list(DIAS_SEMANA.values())
    res = diario.groupby([SUBJECT_COLUMN, WEEKDAY_COLUMN])[INTERACTIONS_COLUMN].mean().round(ROUND_DECIMALS).reset_index()
    res[WEEKDAY_COLUMN] = pd.Categorical(res[WEEKDAY_COLUMN], categories=orden, ordered=True)
    return res.sort_values([SUBJECT_COLUMN, WEEKDAY_COLUMN]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# KPI 3: cantidad de interacciones por tipo
# ----------------------------------------------------------------------------
def clasificar_interacciones(df):
    """Tipo de cada interacción: navegación si la acción es un acceso; si no, según la sección."""
    tipo = df[SECTION_COLUMN].map(TIPO_POR_SECCION).fillna(OTROS_TIPO)
    return tipo.where(~df[ACTION_SOURCE_COLUMN].isin(ACCIONES_NAVEGACION), TIPO_NAVEGACION)


def interacciones_por_tipo(df):
    """Interacciones por materia y tipo (ver TIPO_POR_SECCION). Incluye los tipos sin interacciones.

    Devuelve: materia, tipo, interacciones, porcentaje (sobre el total de la materia).
    """
    res = (df.assign(**{TYPE_COLUMN: clasificar_interacciones(df)}).groupby([SUBJECT_COLUMN, TYPE_COLUMN]).size()
             .unstack(fill_value=0).reindex(columns=TIPOS, fill_value=0)
             .stack().rename(INTERACTIONS_COLUMN).reset_index())
    res[PERCENTAGE_COLUMN] = (res[INTERACTIONS_COLUMN] / res.groupby(SUBJECT_COLUMN)[INTERACTIONS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return res


def interacciones_por_accion(df):
    """Detalle por acción concreta (Ver texto, Descargar, Realizar evaluación...), de mayor a menor.

    Devuelve: materia, accion, interacciones, porcentaje (sobre el total de la materia).
    """
    # Hay eventos sin acción registrada: se agrupan como "(sin acción)" para que los totales cierren
    res = (df.assign(**{ACTION_SOURCE_COLUMN: df[ACTION_SOURCE_COLUMN].fillna(NO_ACTION_LABEL)}).groupby([SUBJECT_COLUMN, ACTION_SOURCE_COLUMN]).size()
             .rename(INTERACTIONS_COLUMN).reset_index())
    res[PERCENTAGE_COLUMN] = (res[INTERACTIONS_COLUMN] / res.groupby(SUBJECT_COLUMN)[INTERACTIONS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return res.sort_values([SUBJECT_COLUMN, INTERACTIONS_COLUMN], ascending=[True, False]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# KPI 4: distribución temporal de la actividad
# ----------------------------------------------------------------------------
def actividad_por_dia_y_franja(df, horas_por_franja=HOURS_PER_TIME_SLOT):
    """Interacciones por materia, día de la semana y franja horaria (insumo del mapa de calor).

    Incluye las combinaciones sin actividad. Las franjas son de `horas_por_franja` horas
    (deben dividir a 24): "00-04 h", "04-08 h", ...

    Devuelve: materia, dia_semana, franja, interacciones, porcentaje (sobre el total de la materia).
    """
    d = df.assign(**{WEEKDAY_NUMBER_COLUMN: df[EVENT_DATE_COLUMN].dt.dayofweek, TIME_SLOT_NUMBER_COLUMN: df[EVENT_DATE_COLUMN].dt.hour // horas_por_franja})
    conteo = d.groupby([SUBJECT_COLUMN, WEEKDAY_NUMBER_COLUMN, TIME_SLOT_NUMBER_COLUMN]).size()
    franjas = range(HOURS_PER_DAY // horas_por_franja)
    completo = pd.MultiIndex.from_product([conteo.index.levels[0], DIAS_SEMANA.keys(), franjas],
                                          names=[SUBJECT_COLUMN, WEEKDAY_NUMBER_COLUMN, TIME_SLOT_NUMBER_COLUMN])
    res = conteo.reindex(completo, fill_value=0).rename(INTERACTIONS_COLUMN).reset_index()
    res[WEEKDAY_COLUMN] = res[WEEKDAY_NUMBER_COLUMN].map(DIAS_SEMANA)
    res[TIME_SLOT_COLUMN] = res[TIME_SLOT_NUMBER_COLUMN].map(lambda i: TIME_SLOT_LABEL_TEMPLATE.format(start=i * horas_por_franja, end=(i + 1) * horas_por_franja))
    res[PERCENTAGE_COLUMN] = (res[INTERACTIONS_COLUMN] / res.groupby(SUBJECT_COLUMN)[INTERACTIONS_COLUMN].transform("sum") * PERCENT_FACTOR).round(ROUND_DECIMALS)
    return res[[SUBJECT_COLUMN, WEEKDAY_COLUMN, TIME_SLOT_COLUMN, INTERACTIONS_COLUMN, PERCENTAGE_COLUMN]]


def matriz_dia_franja(actividad, materia, valor=INTERACTIONS_COLUMN):
    """Matriz día de la semana (filas) x franja horaria (columnas) de una materia, para `heatmap`."""
    t = actividad[actividad[SUBJECT_COLUMN] == materia]
    return t.pivot(index=WEEKDAY_COLUMN, columns=TIME_SLOT_COLUMN, values=valor).reindex(list(DIAS_SEMANA.values()))
