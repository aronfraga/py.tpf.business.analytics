"""KPIs de trazabilidad: frecuencia de ingreso (semanal y mensual) e interacciones promedio por día.

Entrada : data/integrado/trazabilidad_integrado.parquet (generado por integracion.ipynb)
          La carpeta data/ se busca en la raíz del proyecto (dos niveles arriba de src/kpis/).
Salida  : DataFrames de pandas (no se escriben archivos).

Uso:
    from kpis_trazabilidad import calcular_kpis_trazabilidad
    kpis = calcular_kpis_trazabilidad(solo_matriculados=True)
    kpis["frecuencia_ingreso_semanal"]   # DataFrame

Definiciones (ajustables):
  - Interacción : cada fila de trazabilidad (un evento: acceso, clic, navegación).
  - Ingreso     : inicio de una sesión. La trazabilidad no trae un identificador de sesión, así que una
                  sesión nueva empieza con el primer evento de un usuario (en una materia) o con el
                  primer evento después de más de `minutos_inactividad` (30 por defecto) sin actividad.
  - Día activo  : día calendario en el que el usuario tuvo al menos una interacción.
"""
from pathlib import Path

import pandas as pd

DIAS_SEMANA = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}

# src/kpis/kpis_trazabilidad.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"


# ----------------------------------------------------------------------------
# Carga
# ----------------------------------------------------------------------------
def cargar_trazabilidad(datos, solo_matriculados=False):
    df = pd.read_parquet(datos / "integrado" / "trazabilidad_integrado.parquet",
                         columns=["materia", "usuario", "fecha"])
    if solo_matriculados:
        cruce = pd.read_parquet(datos / "integrado" / "cruce_matriculados_integrado.parquet",
                                columns=["materia", "usuario", "matriculado"])
        inscriptos = cruce.loc[cruce["matriculado"], ["materia", "usuario"]]
        df = df.merge(inscriptos, on=["materia", "usuario"], how="inner")
    df["dia"] = df["fecha"].dt.normalize()
    return df


def marcar_ingresos(df, minutos_inactividad=30):
    """Agrega la columna booleana `es_ingreso` (primer evento de cada sesión inferida)."""
    df = df.sort_values(["materia", "usuario", "fecha"]).reset_index(drop=True)
    pausa = df.groupby(["materia", "usuario"])["fecha"].diff()
    df["es_ingreso"] = pausa.isna() | (pausa > pd.Timedelta(minutes=minutos_inactividad))
    return df


# ----------------------------------------------------------------------------
# KPI 1: frecuencia de ingreso semanal / mensual
# ----------------------------------------------------------------------------
def frecuencia_ingreso(df, freq):
    """freq: 'W' (semanas de lunes a domingo) o 'M' (meses calendario). Una fila por materia y período."""
    d = df.assign(periodo=df["fecha"].dt.to_period(freq))
    ingresos = d[d["es_ingreso"]].groupby(["materia", "periodo"]).size().rename("ingresos")
    activos = d.groupby(["materia", "periodo"])["usuario"].nunique().rename("usuarios_activos")
    dias = (d.groupby(["materia", "periodo", "usuario"])["dia"].nunique()
              .groupby(["materia", "periodo"]).mean().rename("dias_activos_por_usuario"))

    res = pd.concat([ingresos, activos, dias], axis=1).reset_index()
    res["ingresos"] = res["ingresos"].fillna(0).astype(int)
    res["ingresos_por_usuario_activo"] = (res["ingresos"] / res["usuarios_activos"]).round(2)
    res["dias_activos_por_usuario"] = res["dias_activos_por_usuario"].round(2)

    # Los períodos de los extremos pueden estar cortados por el rango de los datos
    rangos = df.groupby("materia")["dia"].agg(["min", "max"])
    inicio = res["periodo"].dt.start_time
    fin = res["periodo"].dt.end_time.dt.normalize()
    res["periodo_completo"] = (inicio >= res["materia"].map(rangos["min"])) & (fin <= res["materia"].map(rangos["max"]))
    res.insert(1, "inicio", inicio.dt.date)
    res["periodo"] = res["periodo"].astype(str)
    return res


# ----------------------------------------------------------------------------
# KPI 2: interacciones promedio por día
# ----------------------------------------------------------------------------
def interacciones_diarias(df):
    """Serie diaria por materia con todos los días del rango (incluye los días sin actividad)."""
    piezas = []
    for materia, g in df.groupby("materia"):
        diario = g.groupby("dia").agg(interacciones=("usuario", "size"), usuarios_activos=("usuario", "nunique"))
        rango = pd.date_range(g["dia"].min(), g["dia"].max(), freq="D")
        diario = diario.reindex(rango, fill_value=0).rename_axis("dia").reset_index()
        diario.insert(0, "materia", materia)
        piezas.append(diario)
    d = pd.concat(piezas, ignore_index=True)
    d["interacciones_por_usuario_activo"] = (d["interacciones"] / d["usuarios_activos"]).where(d["usuarios_activos"] > 0).round(2)
    d["dia_semana"] = d["dia"].dt.dayofweek.map(DIAS_SEMANA)
    return d


def resumen_interacciones(df, diario):
    """Promedios por materia: por día calendario, por día con actividad y por usuario activo y día."""
    res = diario.groupby("materia").agg(
        interacciones_totales=("interacciones", "sum"),
        dias_calendario=("dia", "size"),
        dias_con_actividad=("interacciones", lambda s: int((s > 0).sum())),
    )
    res["promedio_diario"] = res["interacciones_totales"] / res["dias_calendario"]
    res["promedio_diario_dias_con_actividad"] = res["interacciones_totales"] / res["dias_con_actividad"]
    usuario_dia = df.groupby(["materia", "usuario", "dia"]).size()
    res["promedio_por_usuario_activo_y_dia"] = usuario_dia.groupby("materia").mean()
    return res.round(2).reset_index()


def interacciones_por_dia_semana(diario):
    """Promedio de interacciones según el día de la semana (lunes a domingo)."""
    orden = list(DIAS_SEMANA.values())
    res = diario.groupby(["materia", "dia_semana"])["interacciones"].mean().round(2).reset_index()
    res["dia_semana"] = pd.Categorical(res["dia_semana"], categories=orden, ordered=True)
    return res.sort_values(["materia", "dia_semana"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# Control: trazabilidad vs. columna `interacciones` del reporte de participación
# ----------------------------------------------------------------------------
def validar_contra_participacion(df, datos):
    part = pd.read_parquet(datos / "integrado" / "participacion_integrado.parquet",
                           columns=["materia", "usuario", "interacciones"])
    traz = df.groupby(["materia", "usuario"]).size().rename("eventos_trazabilidad").reset_index()
    cmp = part.merge(traz, on=["materia", "usuario"], how="left")
    cmp["eventos_trazabilidad"] = cmp["eventos_trazabilidad"].fillna(0).astype(int)
    cmp["diferencia"] = cmp["eventos_trazabilidad"] - cmp["interacciones"]
    return cmp.groupby("materia").agg(
        usuarios=("usuario", "size"),
        coinciden=("diferencia", lambda s: int((s == 0).sum())),
        diferencia_total=("diferencia", "sum"),
        diferencia_maxima=("diferencia", lambda s: int(s.abs().max())),
    ).reset_index()


# ----------------------------------------------------------------------------
def calcular_kpis_trazabilidad(datos=None, solo_matriculados=False, minutos_inactividad=30):
    """Calcula todos los KPIs de trazabilidad y los devuelve como DataFrames.

    Devuelve un dict con las claves: frecuencia_ingreso_semanal, frecuencia_ingreso_mensual,
    interacciones_diarias, interacciones_resumen, interacciones_por_dia_semana.
    """
    datos = Path(datos) if datos else DATOS_POR_DEFECTO
    df = marcar_ingresos(cargar_trazabilidad(datos, solo_matriculados), minutos_inactividad)
    diario = interacciones_diarias(df)
    return {
        "frecuencia_ingreso_semanal": frecuencia_ingreso(df, "W"),
        "frecuencia_ingreso_mensual": frecuencia_ingreso(df, "M"),
        "interacciones_diarias": diario,
        "interacciones_resumen": resumen_interacciones(df, diario),
        "interacciones_por_dia_semana": interacciones_por_dia_semana(diario),
    }

