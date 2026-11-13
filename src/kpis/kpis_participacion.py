"""KPIs de participación: sesiones, tiempo en la plataforma, cobertura y estudiantes activos.

Entrada : data/integrado/{trazabilidad,participacion,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Las funciones de KPI son puras (reciben y devuelven DataFrames). Para calcular todo de una vez:
    from kpis_participacion import calcular_kpis_participacion
    kpis = calcular_kpis_participacion()
    kpis["sesiones_promedio"]   # DataFrame

La justificación y los controles de sensibilidad de cada KPI están en participacion.ipynb.
"""
from pathlib import Path

import pandas as pd

# src/kpis/kpis_participacion.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"

CLAVES = ["materia", "usuario"]

# Una sesión termina cuando el estudiante pasa más de este tiempo sin generar eventos.
UMBRAL_SESION = pd.Timedelta(minutes=30)
UMBRAL_PARTICIPACION = 0  # interacciones que hay que superar para contar como participante
DIAS_ACTIVIDAD = 15  # días máximos sin interacción para seguir considerándose activo


# ----------------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------------
def _matriculados(cruce: pd.DataFrame) -> pd.DataFrame:
    return cruce.loc[cruce["matriculado"], CLAVES]


def _universo_de_alumnos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Matriculados más los no matriculados con al menos una interacción, por asignatura.

    El reporte de participación lista a todo el padrón de la plataforma en cada aula, así que
    quien no está matriculado y nunca participó no se cuenta.
    """
    con_actividad = participacion.loc[participacion["interacciones"] > 0, CLAVES]
    return pd.concat([_matriculados(cruce), con_actividad]).drop_duplicates()


# ----------------------------------------------------------------------------
# KPI 1: promedio de sesiones por estudiante
# ----------------------------------------------------------------------------
def sesiones_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    """Cantidad de sesiones de cada estudiante matriculado, por asignatura.

    El log de trazabilidad no trae un identificador de sesión, así que se reconstruye: una
    sesión es una secuencia de eventos de un usuario en una asignatura donde entre eventos
    consecutivos pasan como máximo `umbral`. Los matriculados sin actividad quedan con 0
    sesiones, para que no inflen el promedio quienes nunca ingresaron.

    Devuelve: materia, usuario, sesiones.
    """
    eventos = trazabilidad.sort_values(CLAVES + ["fecha"])
    brecha = eventos.groupby(CLAVES)["fecha"].diff()
    # Un evento abre sesión nueva si es el primero del usuario (NaT) o si superó el umbral.
    eventos = eventos.assign(nueva_sesion=brecha.isna() | (brecha > umbral))
    sesiones = eventos.groupby(CLAVES)["nueva_sesion"].sum().astype(int).rename("sesiones")

    return (
        _matriculados(cruce).merge(sesiones.reset_index(), on=CLAVES, how="left")
        .fillna({"sesiones": 0})
        .astype({"sesiones": int})
    )


def sesiones_promedio_por_estudiante(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                     umbral: pd.Timedelta = UMBRAL_SESION) -> pd.DataFrame:
    """KPI: promedio de sesiones por estudiante, por asignatura.

    Devuelve una fila por asignatura: matriculados, activos, promedio_matriculados (incluye
    inactivos), promedio_activos (solo quienes tuvieron al menos una sesión) y
    mediana_matriculados (robusta a usos extremos).
    """
    por_estudiante = sesiones_por_estudiante(trazabilidad, cruce, umbral)
    activos = por_estudiante[por_estudiante["sesiones"] > 0]
    return pd.DataFrame(
        {
            "matriculados": por_estudiante.groupby("materia")["usuario"].nunique(),
            "activos": activos.groupby("materia")["usuario"].nunique(),
            "promedio_matriculados": por_estudiante.groupby("materia")["sesiones"].mean(),
            "promedio_activos": activos.groupby("materia")["sesiones"].mean(),
            "mediana_matriculados": por_estudiante.groupby("materia")["sesiones"].median(),
        }
    ).round(2).reset_index()


# ----------------------------------------------------------------------------
# KPI 2: tiempo promedio en la plataforma
# ----------------------------------------------------------------------------
def tiempo_por_estudiante(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Minutos de uso estimado de cada estudiante matriculado, por asignatura.

    El reporte de participación tiene una fila por estudiante y asignatura con el tiempo ya
    acumulado (`tiempo_estimado_de_uso_min`). Los matriculados que no figuran en el reporte
    quedan con 0 minutos.

    Devuelve: materia, usuario, tiempo_min.
    """
    tiempo = participacion[CLAVES + ["tiempo_estimado_de_uso_min"]].rename(
        columns={"tiempo_estimado_de_uso_min": "tiempo_min"}
    )
    return _matriculados(cruce).merge(tiempo, on=CLAVES, how="left").fillna({"tiempo_min": 0})


def tiempo_promedio_en_plataforma(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """KPI: tiempo promedio en la plataforma por estudiante, por asignatura (en minutos).

    Devuelve una fila por asignatura: matriculados, activos, promedio_min_matriculados,
    promedio_min_activos y mediana_min_matriculados. La distribución es asimétrica (pocos
    estudiantes con uso muy alto), por eso se incluye la mediana.
    """
    por_estudiante = tiempo_por_estudiante(participacion, cruce)
    activos = por_estudiante[por_estudiante["tiempo_min"] > 0]
    return pd.DataFrame(
        {
            "matriculados": por_estudiante.groupby("materia")["usuario"].nunique(),
            "activos": activos.groupby("materia")["usuario"].nunique(),
            "promedio_min_matriculados": por_estudiante.groupby("materia")["tiempo_min"].mean(),
            "promedio_min_activos": activos.groupby("materia")["tiempo_min"].mean(),
            "mediana_min_matriculados": por_estudiante.groupby("materia")["tiempo_min"].median(),
        }
    ).round(2).reset_index()


# ----------------------------------------------------------------------------
# KPI 3: cobertura de participación
# ----------------------------------------------------------------------------
def cobertura_participacion(participacion: pd.DataFrame, cruce: pd.DataFrame,
                            umbral: float = UMBRAL_PARTICIPACION,
                            columna: str = "interacciones") -> pd.DataFrame:
    """KPI: porcentaje de cobertura de participación, por asignatura.

    Cobertura = alumnos con `columna` > `umbral` / total de alumnos * 100. El total es el
    universo de alumnos (matriculados y no matriculados con actividad) y no depende del
    umbral: solo el numerador cambia. Con umbral=0 mide quién participó al menos una vez.

    Parámetros:
      - umbral: valor que la participación debe superar (estricto).
      - columna: métrica a evaluar ("interacciones", "tiempo_estimado_de_uso_min", "avance", ...).

    Devuelve una fila por asignatura: total_alumnos, matriculados,
    no_matriculados_con_actividad, con_participacion, cobertura_pct.
    """
    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + [columna]], on=CLAVES, how="left"
    ).fillna({columna: 0})
    universo["es_matriculado"] = universo.set_index(CLAVES).index.isin(_matriculados(cruce).set_index(CLAVES).index)
    universo["participa"] = universo[columna] > umbral

    resumen = universo.groupby("materia").agg(
        total_alumnos=("usuario", "nunique"),
        matriculados=("es_matriculado", "sum"),
        con_participacion=("participa", "sum"),
    )
    resumen["no_matriculados_con_actividad"] = resumen["total_alumnos"] - resumen["matriculados"]
    resumen["cobertura_pct"] = (100 * resumen["con_participacion"] / resumen["total_alumnos"]).round(2)
    return resumen[
        ["total_alumnos", "matriculados", "no_matriculados_con_actividad", "con_participacion", "cobertura_pct"]
    ].reset_index()


# ----------------------------------------------------------------------------
# KPI 4: estudiantes activos vs. inactivos
# ----------------------------------------------------------------------------
def estudiantes_activos_vs_inactivos(participacion: pd.DataFrame, cruce: pd.DataFrame,
                                     dias: int = DIAS_ACTIVIDAD,
                                     fecha_corte: pd.Timestamp | None = None) -> pd.DataFrame:
    """KPI: estudiantes activos vs. inactivos, por asignatura.

    Un estudiante es activo si su última interacción ocurrió dentro de los últimos `dias` días
    respecto de la fecha de corte; inactivo si pasaron más de `dias` días o si nunca interactuó.
    A diferencia de la cobertura (si participó alguna vez), mide el estado reciente.

    `fecha_corte` es, por defecto, la última interacción de todo el reporte (la fecha del corte
    de los datos), para que el resultado no dependa de cuándo se ejecute.

    Devuelve una fila por asignatura: total_alumnos, activos, inactivos, pct_activos,
    pct_inactivos, fecha_corte.
    """
    if fecha_corte is None:
        fecha_corte = participacion["ultima_interaccion"].max()

    universo = _universo_de_alumnos(participacion, cruce).merge(
        participacion[CLAVES + ["ultima_interaccion"]], on=CLAVES, how="left"
    )
    dias_sin_interaccion = (fecha_corte - universo["ultima_interaccion"]).dt.total_seconds() / 86400
    # NaN (nunca interactuó) compara como False -> inactivo
    universo["activo"] = dias_sin_interaccion <= dias

    resumen = universo.groupby("materia")["activo"].agg(total_alumnos="size", activos="sum")
    resumen["inactivos"] = resumen["total_alumnos"] - resumen["activos"]
    resumen["pct_activos"] = (100 * resumen["activos"] / resumen["total_alumnos"]).round(2)
    resumen["pct_inactivos"] = (100 - resumen["pct_activos"]).round(2)
    resumen["fecha_corte"] = fecha_corte.normalize()
    return resumen.reset_index()


# ----------------------------------------------------------------------------
# Todos los KPI
# ----------------------------------------------------------------------------
def calcular_kpis_participacion(datos=None, umbral_sesion: pd.Timedelta = UMBRAL_SESION,
                                umbral_participacion: float = UMBRAL_PARTICIPACION,
                                dias_actividad: int = DIAS_ACTIVIDAD) -> dict[str, pd.DataFrame]:
    """Lee los datos integrados y devuelve los KPI de participación como DataFrames.

    Claves: sesiones_promedio, tiempo_promedio, cobertura, activos_vs_inactivos.
    """
    integrado = (Path(datos) if datos else DATOS_POR_DEFECTO) / "integrado"
    trazabilidad = pd.read_parquet(integrado / "trazabilidad_integrado.parquet", columns=CLAVES + ["fecha"])
    participacion = pd.read_parquet(integrado / "participacion_integrado.parquet")
    cruce = pd.read_parquet(integrado / "cruce_matriculados_integrado.parquet")
    return {
        "sesiones_promedio": sesiones_promedio_por_estudiante(trazabilidad, cruce, umbral_sesion),
        "tiempo_promedio": tiempo_promedio_en_plataforma(participacion, cruce),
        "cobertura": cobertura_participacion(participacion, cruce, umbral_participacion),
        "activos_vs_inactivos": estudiantes_activos_vs_inactivos(participacion, cruce, dias_actividad),
    }
