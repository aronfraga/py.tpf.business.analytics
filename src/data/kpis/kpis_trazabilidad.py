from pathlib import Path
import sys
import pandas as pd
_SRC_PATH = str(Path(__file__).resolve().parents[2])
if _SRC_PATH not in sys.path:
    sys.path.append(_SRC_PATH)
import constants as const

DIAS_SEMANA = const.WEEKDAY_NAMES

ACCIONES_NAVEGACION = const.NAVIGATION_ACTIONS
TIPO_NAVEGACION = const.TYPE_NAVIGATION
OTROS_TIPO = const.TYPE_OTHERS
TIPO_POR_SECCION = const.TYPE_BY_SECTION
TIPOS = const.INTERACTION_TYPES


def cargar_trazabilidad(datos, solo_matriculados=False):
    df = pd.read_parquet(datos / const.INTEGRATED_FOLDER_NAME / const.TRACEABILITY_FILE,
                         columns=[const.SUBJECT_COLUMN, const.USER_COLUMN, const.EVENT_DATE_COLUMN, const.SECTION_COLUMN, const.ACTION_SOURCE_COLUMN])
    if solo_matriculados:
        cruce = pd.read_parquet(datos / const.INTEGRATED_FOLDER_NAME / const.ENROLLMENT_CROSS_FILE,
                                columns=[const.SUBJECT_COLUMN, const.USER_COLUMN, const.ENROLLED_COLUMN])
        inscriptos = cruce.loc[cruce[const.ENROLLED_COLUMN], [const.SUBJECT_COLUMN, const.USER_COLUMN]]
        df = df.merge(inscriptos, on=[const.SUBJECT_COLUMN, const.USER_COLUMN], how="inner")
    df[const.DAY_COLUMN] = df[const.EVENT_DATE_COLUMN].dt.normalize()
    return df

def marcar_ingresos(df, minutos_inactividad=const.INACTIVITY_MINUTES):
    df = df.sort_values([const.SUBJECT_COLUMN, const.USER_COLUMN, const.EVENT_DATE_COLUMN]).reset_index(drop=True)
    pausa = df.groupby([const.SUBJECT_COLUMN, const.USER_COLUMN])[const.EVENT_DATE_COLUMN].diff()
    df[const.ENTRY_COLUMN] = pausa.isna() | (pausa > pd.Timedelta(minutes=minutos_inactividad))
    return df

def frecuencia_ingreso(df, freq):
    d = df.assign(**{const.PERIOD_COLUMN: df[const.EVENT_DATE_COLUMN].dt.to_period(freq)})
    ingresos = d[d[const.ENTRY_COLUMN]].groupby([const.SUBJECT_COLUMN, const.PERIOD_COLUMN]).size().rename(
        const.ENTRIES_COLUMN)
    activos = d.groupby([const.SUBJECT_COLUMN, const.PERIOD_COLUMN])[const.USER_COLUMN].nunique().rename(
        const.ACTIVE_USERS_COLUMN)
    dias = (d.groupby([const.SUBJECT_COLUMN, const.PERIOD_COLUMN, const.USER_COLUMN])[const.DAY_COLUMN].nunique()
              .groupby([const.SUBJECT_COLUMN, const.PERIOD_COLUMN]).mean().rename(const.ACTIVE_DAYS_PER_USER_COLUMN))

    res = pd.concat([ingresos, activos, dias], axis=1).reset_index()
    res[const.ENTRIES_COLUMN] = res[const.ENTRIES_COLUMN].fillna(0).astype(int)
    res[const.ENTRIES_PER_ACTIVE_USER_COLUMN] = (res[const.ENTRIES_COLUMN] / res[const.ACTIVE_USERS_COLUMN]).round(
        const.ROUND_DECIMALS)
    res[const.ACTIVE_DAYS_PER_USER_COLUMN] = res[const.ACTIVE_DAYS_PER_USER_COLUMN].round(const.ROUND_DECIMALS)

    rangos = df.groupby(const.SUBJECT_COLUMN)[const.DAY_COLUMN].agg(["min", "max"])
    inicio = res[const.PERIOD_COLUMN].dt.start_time
    fin = res[const.PERIOD_COLUMN].dt.end_time.dt.normalize()
    res[const.WHOLE_PERIOD_COLUMN] = (inicio >= res[const.SUBJECT_COLUMN].map(rangos["min"])) & (fin <= res[const.SUBJECT_COLUMN].map(
        rangos["max"]))
    res.insert(1, const.START_COLUMN, inicio.dt.date)
    res[const.PERIOD_COLUMN] = res[const.PERIOD_COLUMN].astype(str)
    return res

def interacciones_diarias(df):
    piezas = []
    for materia, g in df.groupby(const.SUBJECT_COLUMN):
        diario = g.groupby(const.DAY_COLUMN).agg(
            **{const.INTERACTIONS_COLUMN: (const.USER_COLUMN, "size"), const.ACTIVE_USERS_COLUMN: (const.USER_COLUMN, "nunique")})
        rango = pd.date_range(g[const.DAY_COLUMN].min(), g[const.DAY_COLUMN].max(), freq=const.DAILY_FREQUENCY)
        diario = diario.reindex(rango, fill_value=0).rename_axis(const.DAY_COLUMN).reset_index()
        diario.insert(0, const.SUBJECT_COLUMN, materia)
        piezas.append(diario)
    d = pd.concat(piezas, ignore_index=True)
    d[const.INTERACTIONS_PER_ACTIVE_USER_COLUMN] = (d[const.INTERACTIONS_COLUMN] / d[const.ACTIVE_USERS_COLUMN]).where(d[const.ACTIVE_USERS_COLUMN] > 0).round(const.ROUND_DECIMALS)
    d[const.WEEKDAY_COLUMN] = d[const.DAY_COLUMN].dt.dayofweek.map(DIAS_SEMANA)
    return d

def resumen_interacciones(df, diario):
    res = diario.groupby(const.SUBJECT_COLUMN).agg(
        **{const.TOTAL_INTERACTIONS_COLUMN: (const.INTERACTIONS_COLUMN, "sum"), const.CALENDAR_DAYS_COLUMN: (const.DAY_COLUMN, "size"), const.DAYS_WITH_ACTIVITY_COLUMN: (const.INTERACTIONS_COLUMN, lambda s: int((s > 0).sum()))},
    )
    res[const.DAILY_AVERAGE_COLUMN] = res[const.TOTAL_INTERACTIONS_COLUMN] / res[const.CALENDAR_DAYS_COLUMN]
    res[const.DAILY_AVERAGE_ACTIVE_DAYS_COLUMN] = res[const.TOTAL_INTERACTIONS_COLUMN] / res[const.DAYS_WITH_ACTIVITY_COLUMN]
    usuario_dia = df.groupby([const.SUBJECT_COLUMN, const.USER_COLUMN, const.DAY_COLUMN]).size()
    res[const.AVERAGE_PER_ACTIVE_USER_AND_DAY_COLUMN] = usuario_dia.groupby(const.SUBJECT_COLUMN).mean()
    return res.round(const.ROUND_DECIMALS).reset_index()

def interacciones_por_dia_semana(diario):
    orden = list(DIAS_SEMANA.values())
    res = diario.groupby([const.SUBJECT_COLUMN, const.WEEKDAY_COLUMN])[const.INTERACTIONS_COLUMN].mean().round(const.ROUND_DECIMALS).reset_index()
    res[const.WEEKDAY_COLUMN] = pd.Categorical(res[const.WEEKDAY_COLUMN], categories=orden, ordered=True)
    return res.sort_values([const.SUBJECT_COLUMN, const.WEEKDAY_COLUMN]).reset_index(drop=True)

def clasificar_interacciones(df):
    tipo = df[const.SECTION_COLUMN].map(TIPO_POR_SECCION).fillna(OTROS_TIPO)
    return tipo.where(~df[const.ACTION_SOURCE_COLUMN].isin(ACCIONES_NAVEGACION), TIPO_NAVEGACION)

def interacciones_por_tipo(df):
    res = (df.assign(**{const.TYPE_COLUMN: clasificar_interacciones(df)}).groupby([const.SUBJECT_COLUMN, const.TYPE_COLUMN]).size()
             .unstack(fill_value=0).reindex(columns=TIPOS, fill_value=0)
             .stack().rename(const.INTERACTIONS_COLUMN).reset_index())
    res[const.PERCENTAGE_COLUMN] = (res[const.INTERACTIONS_COLUMN] / res.groupby(const.SUBJECT_COLUMN)[const.INTERACTIONS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return res

def interacciones_por_accion(df):
    res = (df.assign(**{const.ACTION_SOURCE_COLUMN: df[const.ACTION_SOURCE_COLUMN].fillna(const.NO_ACTION_LABEL)}).groupby([const.SUBJECT_COLUMN, const.ACTION_SOURCE_COLUMN]).size()
             .rename(const.INTERACTIONS_COLUMN).reset_index())
    res[const.PERCENTAGE_COLUMN] = (res[const.INTERACTIONS_COLUMN] / res.groupby(const.SUBJECT_COLUMN)[const.INTERACTIONS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return res.sort_values([const.SUBJECT_COLUMN, const.INTERACTIONS_COLUMN], ascending=[True, False]).reset_index(
        drop=True)

def actividad_por_dia_y_franja(df, horas_por_franja=const.HOURS_PER_TIME_SLOT):
    d = df.assign(**{const.WEEKDAY_NUMBER_COLUMN: df[const.EVENT_DATE_COLUMN].dt.dayofweek, const.TIME_SLOT_NUMBER_COLUMN: df[const.EVENT_DATE_COLUMN].dt.hour // horas_por_franja})
    conteo = d.groupby([const.SUBJECT_COLUMN, const.WEEKDAY_NUMBER_COLUMN, const.TIME_SLOT_NUMBER_COLUMN]).size()
    franjas = range(const.HOURS_PER_DAY // horas_por_franja)
    completo = pd.MultiIndex.from_product([conteo.index.levels[0], DIAS_SEMANA.keys(), franjas],
                                          names=[const.SUBJECT_COLUMN, const.WEEKDAY_NUMBER_COLUMN, const.TIME_SLOT_NUMBER_COLUMN])
    res = conteo.reindex(completo, fill_value=0).rename(const.INTERACTIONS_COLUMN).reset_index()
    res[const.WEEKDAY_COLUMN] = res[const.WEEKDAY_NUMBER_COLUMN].map(DIAS_SEMANA)
    res[const.TIME_SLOT_COLUMN] = res[const.TIME_SLOT_NUMBER_COLUMN].map(
        lambda i: const.TIME_SLOT_LABEL_TEMPLATE.format(start=i * horas_por_franja, end=(i + 1) * horas_por_franja))
    res[const.PERCENTAGE_COLUMN] = (res[const.INTERACTIONS_COLUMN] / res.groupby(const.SUBJECT_COLUMN)[const.INTERACTIONS_COLUMN].transform("sum") * const.PERCENT_FACTOR).round(const.ROUND_DECIMALS)
    return res[[const.SUBJECT_COLUMN, const.WEEKDAY_COLUMN, const.TIME_SLOT_COLUMN, const.INTERACTIONS_COLUMN, const.PERCENTAGE_COLUMN]]

def matriz_dia_franja(actividad, materia, valor=const.INTERACTIONS_COLUMN):
    t = actividad[actividad[const.SUBJECT_COLUMN] == materia]
    return t.pivot(index=const.WEEKDAY_COLUMN, columns=const.TIME_SLOT_COLUMN, values=valor).reindex(
        list(DIAS_SEMANA.values()))
