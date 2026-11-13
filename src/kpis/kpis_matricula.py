"""KPIs de matrícula: estudiantes activos según su matrícula y situación académica.

Entrada : data/integrado/{participacion,calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Para calcular todo de una vez:
    from kpis_matricula import calcular_kpis_matricula
    kpis = calcular_kpis_matricula()
    kpis["activos_por_matricula"]   # DataFrame

Definiciones:
  - Activo      : tuvo al menos una interacción en el aula (`interacciones > 0` en el reporte de
                  participación). Estar listado en el reporte no alcanza: incluye a todo el padrón de la
                  plataforma en cada aula, incluso a quienes nunca entraron.
  - Matriculado : figura en el listado oficial de matriculados de esa asignatura (`matriculado` del cruce).
  - Situación   : baja, no se presentó, o la condición (promocionado, regular, libre) según la nota. Es el
                  desempeño actual, no una proyección de la condición final.

La justificación y los controles de cada KPI están en matricula.ipynb.
"""
from pathlib import Path

import pandas as pd

try:  # como paquete (kpis.kpis_matricula) o como módulo suelto (kpis_matricula)
    from .kpis_calificaciones import condicion_por_estudiante
except ImportError:
    from kpis_calificaciones import condicion_por_estudiante

# src/kpis/kpis_matricula.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"

CLAVES = ["materia", "usuario"]
SITUACIONES = ["promocionado", "regular", "libre", "no se presentó", "baja"]


# ----------------------------------------------------------------------------
# KPI 1: estudiantes activos matriculados y no matriculados (alerta de no inscriptos pero activos)
# ----------------------------------------------------------------------------
def estudiantes_activos(participacion: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Estudiantes activos de cada asignatura y si están matriculados.

    Los no matriculados activos son la alerta: usan el aula sin estar inscriptos.

    Devuelve una fila por estudiante activo y asignatura: materia, usuario, matriculado.
    """
    activos = participacion.loc[participacion["interacciones"] > 0, CLAVES]
    res = activos.merge(cruce[CLAVES + ["matriculado"]], on=CLAVES, how="left")
    res["matriculado"] = res["matriculado"].fillna(False).astype(bool)
    return res.sort_values(CLAVES).reset_index(drop=True)


def resumen_activos_por_matricula(activos: pd.DataFrame) -> pd.DataFrame:
    """KPI: cantidad de estudiantes activos matriculados y no matriculados, por asignatura.

    Devuelve una fila por asignatura: materia, matriculados_activos, no_matriculados_activos.
    """
    return (
        activos.groupby(["materia", "matriculado"]).size().unstack(fill_value=0)
        .reindex(columns=[True, False], fill_value=0)
        .set_axis(["matriculados_activos", "no_matriculados_activos"], axis=1)
        .reset_index()
        .rename_axis(columns=None)
    )


# ----------------------------------------------------------------------------
# KPI 2: situación académica general y por asignatura
# ----------------------------------------------------------------------------
def situacion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Situación académica de cada estudiante matriculado, por asignatura.

    Situaciones (ver SITUACIONES):
      - baja: la inscripción figura con estado Baja; tiene prioridad sobre las demás.
      - no se presentó: matriculado que no rindió ningún instrumento.
      - promocionado, regular, libre: condición según la nota (porcentaje de los puntos rendidos) y los
        umbrales de la asignatura definidos en kpis_calificaciones.py.

    Devuelve una fila por estudiante y asignatura: materia, usuario, situacion.
    """
    matriculados = cruce.loc[cruce["matriculado"], CLAVES + ["estado_insc"]]
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + ["condicion"]]
    res = matriculados.merge(condicion, on=CLAVES, how="left")
    res["situacion"] = res["condicion"].fillna("no se presentó")
    res.loc[res["estado_insc"] == "Baja", "situacion"] = "baja"
    return res[CLAVES + ["situacion"]].sort_values(CLAVES).reset_index(drop=True)


def resumen_situacion_academica(situacion: pd.DataFrame) -> pd.DataFrame:
    """KPI: cantidad y porcentaje de estudiantes por situación académica, por asignatura y en general.

    Devuelve (una fila por asignatura y situación, incluyendo las situaciones sin estudiantes, y una
    asignatura "general" con el total de todos los pares estudiante-asignatura): materia, situacion,
    estudiantes, porcentaje. Sirve directo para el gráfico de dona o de barras de Streamlit.
    """
    conteo = (
        situacion.groupby(["materia", "situacion"]).size().unstack(fill_value=0)
        .reindex(columns=SITUACIONES, fill_value=0)
    )
    conteo.loc["general"] = conteo.sum()
    res = conteo.stack().rename("estudiantes").reset_index()
    res["porcentaje"] = (res["estudiantes"] / res.groupby("materia")["estudiantes"].transform("sum") * 100).round(2)
    return res


def graficar_situacion_academica(resumen: pd.DataFrame, ruta: Path | None = None):
    """Barras horizontales apiladas (100 %) de la situación académica, por asignatura y en general.

    Usa matplotlib, que se importa acá para que el resto del módulo no lo requiera. Si se indica
    `ruta`, guarda la imagen. Devuelve la figura.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    colores = {"promocionado": "#6B8F71", "regular": "#E0A458", "libre": "#B5523B",
               "no se presentó": "#8A9BA8", "baja": "#4A5A64"}
    porcentajes = resumen.pivot(index="materia", columns="situacion", values="porcentaje")[SITUACIONES]
    orden = [m for m in porcentajes.index if m != "general"] + ["general"]
    porcentajes = porcentajes.loc[orden]
    etiquetas = [m.capitalize() for m in porcentajes.index]

    fig, eje = plt.subplots(figsize=(9, 3.6))
    izquierda = np.zeros(len(porcentajes))
    for situacion in SITUACIONES:
        valores = porcentajes[situacion].to_numpy()
        barras = eje.barh(etiquetas, valores, left=izquierda, color=colores[situacion], label=situacion)
        eje.bar_label(barras, labels=[f"{v:.0f} %" if v >= 4 else "" for v in valores], label_type="center",
                      fontsize=9, color="white")
        izquierda += valores
    eje.invert_yaxis()
    eje.set_xlim(0, 100)
    eje.set_xlabel("Porcentaje de matriculados")
    eje.set_title("Situación académica de los matriculados", loc="left")
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=len(SITUACIONES), frameon=False)
    fig.tight_layout()
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# Todos los KPI
# ----------------------------------------------------------------------------
def calcular_kpis_matricula(datos=None) -> dict[str, pd.DataFrame]:
    """Lee los datos integrados y devuelve los KPI de matrícula como DataFrames.

    Claves: estudiantes_activos (detalle; los no matriculados son la alerta), activos_por_matricula,
    situacion_academica (detalle) y situacion_academica_resumen.
    """
    integrado = (Path(datos) if datos else DATOS_POR_DEFECTO) / "integrado"
    participacion = pd.read_parquet(integrado / "participacion_integrado.parquet")
    calificaciones = pd.read_parquet(integrado / "calificaciones_integrado.parquet")
    cruce = pd.read_parquet(integrado / "cruce_matriculados_integrado.parquet")

    activos = estudiantes_activos(participacion, cruce)
    situacion = situacion_academica(calificaciones, cruce)
    return {
        "estudiantes_activos": activos,
        "activos_por_matricula": resumen_activos_por_matricula(activos),
        "situacion_academica": situacion,
        "situacion_academica_resumen": resumen_situacion_academica(situacion),
    }
