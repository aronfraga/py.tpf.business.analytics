"""KPIs de calificaciones: promedio general, distribución de notas, condición académica y comparación.

Entrada : data/integrado/{calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).

Las funciones de KPI son puras (reciben y devuelven DataFrames). Para calcular todo de una vez:
    from kpis_calificaciones import calcular_kpis_calificaciones
    kpis = calcular_kpis_calificaciones()
    kpis["promedio_general"]   # DataFrame

Criterio de nota: cada estudiante tiene una nota en porcentaje (0-100) calculada como
    suma(nota_obtenida) / suma(nota_max) * 100
sobre los instrumentos que rindió. Así se respetan los distintos pesos de cada instrumento y las
distintas escalas de cada asignatura, y los datos nuevos (un parcial, un recuperatorio) se suman
solos. Los umbrales de condición también se expresan como porcentaje del total posible.

La justificación y los controles de cada KPI están en calificaciones.ipynb.
"""
from pathlib import Path

import pandas as pd

# src/kpis/kpis_calificaciones.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"

CLAVES = ["materia", "usuario"]

# Condiciones de cada asignatura en puntos: (total posible, mínimo para regular, mínimo para promocionar)
CONDICIONES_PUNTOS = {
    "algebra": (120, 60, 85),
    "probabilidad": (100, 60, 85),
    "algoritmos": (100, 60, 90),
}
CONDICIONES = ["promocionado", "regular", "libre"]

# Los mismos umbrales como porcentaje del total posible
UMBRALES_PCT = {
    materia: {"regular": regular / total * 100, "promocionado": promociona / total * 100}
    for materia, (total, regular, promociona) in CONDICIONES_PUNTOS.items()
}

# Asignaturas cuya nota final es la suma de puntos (las demás promedian sus instrumentos)
ASIGNATURAS_ACUMULATIVAS = ["algebra"]


# ----------------------------------------------------------------------------
# Auxiliares
# ----------------------------------------------------------------------------
def _solo_matriculados(calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Deja únicamente las calificaciones de estudiantes matriculados en esa asignatura."""
    matriculados = cruce.loc[cruce["matriculado"], CLAVES]
    return calificaciones.merge(matriculados, on=CLAVES, how="inner")


def _con_nota_valida(calificaciones: pd.DataFrame) -> pd.DataFrame:
    """Descarta filas sin nota o sin máximo válido (nulo o <= 0)."""
    return calificaciones[calificaciones["nota_max"] > 0].dropna(subset=["nota_obtenida", "nota_max"])


# ----------------------------------------------------------------------------
# KPI 1: promedio general por asignatura
# ----------------------------------------------------------------------------
def nota_por_estudiante(calificaciones: pd.DataFrame) -> pd.DataFrame:
    """Nota (0-100) de cada estudiante en cada asignatura sobre el total de puntos posibles.

    Devuelve: materia, usuario, instrumentos, puntos_obtenidos, puntos_posibles, nota_pct.
    """
    res = (
        _con_nota_valida(calificaciones).groupby(CLAVES)
        .agg(instrumentos=("nota_max", "size"), puntos_obtenidos=("nota_obtenida", "sum"), puntos_posibles=("nota_max", "sum"))
        .reset_index()
    )
    res["nota_pct"] = res["puntos_obtenidos"] / res["puntos_posibles"] * 100
    return res


def promedio_general_por_asignatura(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                                    matriculados: bool = True) -> pd.DataFrame:
    """KPI: promedio general por asignatura, en porcentaje del máximo posible (0-100).

    Devuelve una fila por asignatura: materia, estudiantes, promedio_pct (promedio de la nota
    de cada estudiante, así cada estudiante pesa igual) y mediana_pct.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    return (
        nota_por_estudiante(calificaciones).groupby("materia")["nota_pct"]
        .agg(estudiantes="size", promedio_pct="mean", mediana_pct="median")
        .round(2)
        .reset_index()
    )


def promedio_por_tipo_evaluacion(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                                 matriculados: bool = True) -> pd.DataFrame:
    """Promedio (0-100) por asignatura y tipo de evaluación, con el máximo original del instrumento.

    Devuelve: materia, tipo_evaluacion, estudiantes, nota_max, promedio_pct.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = (
        _con_nota_valida(calificaciones).groupby(["materia", "tipo_evaluacion", "usuario"])
        .agg(obtenidos=("nota_obtenida", "sum"), posibles=("nota_max", "sum"), nota_max=("nota_max", "max"))
        .reset_index()
    )
    por_estudiante["nota_pct"] = por_estudiante["obtenidos"] / por_estudiante["posibles"] * 100
    return (
        por_estudiante.groupby(["materia", "tipo_evaluacion"])
        .agg(estudiantes=("usuario", "size"), nota_max=("nota_max", "max"), promedio_pct=("nota_pct", "mean"))
        .round(2)
        .reset_index()
    )


# ----------------------------------------------------------------------------
# KPI 2: distribución de notas (histograma)
# ----------------------------------------------------------------------------
def distribucion_de_notas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                          ancho_bin: int = 10, matriculados: bool = True) -> pd.DataFrame:
    """KPI: distribución de notas por asignatura, en rangos de `ancho_bin` puntos sobre 100.

    Los rangos son [0, ancho), [ancho, 2*ancho), ..., y el último incluye el 100. Cada estudiante
    cuenta una vez por asignatura. Incluye los rangos vacíos. Es el insumo del histograma de
    Streamlit (`histogram(tabla[tabla["materia"] == m], "rango", "estudiantes", ...)`).

    Devuelve (una fila por asignatura y rango): materia, rango (texto, p. ej. "80-90"), desde,
    hasta, estudiantes, porcentaje (de los estudiantes de la asignatura).
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    por_estudiante = nota_por_estudiante(calificaciones)

    bordes = list(range(0, 100 + ancho_bin, ancho_bin))
    rangos = pd.IntervalIndex.from_breaks(bordes, closed="left")
    # Un 100 exacto va al último rango
    por_estudiante["rango"] = pd.cut(por_estudiante["nota_pct"].clip(upper=bordes[-1] - 1e-9), bins=rangos)

    conteo = (
        por_estudiante.groupby(["materia", "rango"], observed=False).size()
        .rename("estudiantes").reset_index()
    )
    conteo["desde"] = conteo["rango"].map(lambda r: int(r.left))
    conteo["hasta"] = conteo["rango"].map(lambda r: int(r.right))
    conteo["rango"] = conteo["desde"].astype(str) + "-" + conteo["hasta"].astype(str)
    conteo["porcentaje"] = (conteo["estudiantes"] / conteo.groupby("materia")["estudiantes"].transform("sum") * 100).round(2)
    return conteo[["materia", "rango", "desde", "hasta", "estudiantes", "porcentaje"]]


def graficar_histograma(distribucion: pd.DataFrame, ruta: Path | None = None):
    """Dibuja un histograma por asignatura a partir de `distribucion_de_notas` (imagen estática).

    Usa matplotlib, que se importa acá para que el resto del módulo no lo requiera. Si se
    indica `ruta`, guarda la imagen. Devuelve la figura.
    """
    import matplotlib.pyplot as plt

    materias = distribucion["materia"].unique()
    fig, ejes = plt.subplots(1, len(materias), figsize=(5 * len(materias), 4), sharey=True, squeeze=False)
    for eje, materia in zip(ejes[0], materias):
        t = distribucion[distribucion["materia"] == materia]
        barras = eje.bar(t["rango"], t["estudiantes"], color="#1F5C6B", width=0.96)
        eje.bar_label(barras, padding=2, fontsize=8)
        eje.set_title(materia.capitalize())
        eje.set_xlabel("Nota (% del máximo posible)")
        eje.tick_params(axis="x", rotation=45)
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0][0].set_ylabel("Estudiantes")
    fig.suptitle("Distribución de notas por asignatura", x=0.01, ha="left")
    fig.tight_layout()
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# KPI 3: promocionados, regulares y libres
# ----------------------------------------------------------------------------
def condicion_por_estudiante(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                             matriculados: bool = True) -> pd.DataFrame:
    """Condición (promocionado / regular / libre) de cada estudiante según su nota_pct.

    La nota es un porcentaje de lo rendido hasta ahora, así que quien tiene 30 de 30 puntos
    queda promocionado y no libre. Es una clasificación del desempeño actual, no una proyección.

    Devuelve: materia, usuario, instrumentos, puntos_obtenidos, puntos_posibles, nota_pct, condicion.
    """
    if matriculados:
        calificaciones = _solo_matriculados(calificaciones, cruce)
    res = nota_por_estudiante(calificaciones)
    regular = res["materia"].map(lambda m: UMBRALES_PCT[m]["regular"])
    promociona = res["materia"].map(lambda m: UMBRALES_PCT[m]["promocionado"])
    # Pequeña tolerancia para que 85 puntos sobre 120 (70,8333...) no quede afuera por redondeo
    eps = 1e-9
    res["condicion"] = "libre"
    res.loc[res["nota_pct"] + eps >= regular, "condicion"] = "regular"
    res.loc[res["nota_pct"] + eps >= promociona, "condicion"] = "promocionado"
    return res


def condicion_academica(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                        matriculados: bool = True) -> pd.DataFrame:
    """KPI: estudiantes promocionados, regulares y libres por asignatura.

    Devuelve una fila por asignatura y condición (incluye las condiciones sin estudiantes):
    materia, condicion, estudiantes, porcentaje. Sirve directo para el gráfico de dona de Streamlit.
    """
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    conteo = (
        por_estudiante.groupby(["materia", "condicion"]).size().unstack(fill_value=0)
        .reindex(columns=CONDICIONES, fill_value=0)
        .stack().rename("estudiantes").reset_index()
    )
    conteo["porcentaje"] = (conteo["estudiantes"] / conteo.groupby("materia")["estudiantes"].transform("sum") * 100).round(2)
    return conteo


# ----------------------------------------------------------------------------
# KPI 4: comparación entre asignaturas
# ----------------------------------------------------------------------------
def comparar_asignaturas(calificaciones: pd.DataFrame, cruce: pd.DataFrame,
                         matriculados: bool = True) -> pd.DataFrame:
    """KPI: tabla comparativa de resultados por asignatura (todo en % del total posible).

    Reúne los KPI anteriores y agrega dispersión, diferencia contra el promedio general y
    avance de la evaluación. Al comparar hay que recordar que los umbrales para promocionar
    difieren entre asignaturas.

    Devuelve una fila por asignatura: materia, estudiantes, promedio_pct, mediana_pct, desvio_pct,
    dif_vs_general_pp (puntos porcentuales contra el promedio de todos los estudiantes),
    pct_promocionados, pct_regulares, pct_libres y avance_evaluacion_pct (parte del total de
    puntos ya evaluada; solo en asignaturas acumulativas, en las demás queda vacío).
    """
    por_estudiante = condicion_por_estudiante(calificaciones, cruce, matriculados)
    general = por_estudiante["nota_pct"].mean()

    res = por_estudiante.groupby("materia").agg(
        estudiantes=("usuario", "size"),
        promedio_pct=("nota_pct", "mean"),
        mediana_pct=("nota_pct", "median"),
        desvio_pct=("nota_pct", "std"),
        puntos_evaluados=("puntos_posibles", "mean"),
    )
    res["dif_vs_general_pp"] = res["promedio_pct"] - general
    totales = pd.Series({m: CONDICIONES_PUNTOS[m][0] for m in ASIGNATURAS_ACUMULATIVAS})
    res["avance_evaluacion_pct"] = res["puntos_evaluados"] / totales * 100

    condicion = condicion_academica(calificaciones, cruce, matriculados).pivot(
        index="materia", columns="condicion", values="porcentaje"
    )
    res["pct_promocionados"] = condicion["promocionado"]
    res["pct_regulares"] = condicion["regular"]
    res["pct_libres"] = condicion["libre"]

    columnas = ["estudiantes", "promedio_pct", "mediana_pct", "desvio_pct", "dif_vs_general_pp",
                "pct_promocionados", "pct_regulares", "pct_libres", "avance_evaluacion_pct"]
    return res[columnas].round(2).reset_index()


def comparacion_en_formato_largo(comparacion: pd.DataFrame,
                                 indicadores: list[str] | None = None) -> pd.DataFrame:
    """Pasa la tabla comparativa a formato largo (materia, indicador, valor) para graficar.

    Para el gráfico de barras agrupadas de Streamlit:
    `grouped_bar_chart({i: g for i, g in largo.groupby("indicador")}, "materia", "valor", ...)`.
    """
    indicadores = indicadores or ["promedio_pct", "pct_promocionados", "pct_regulares", "pct_libres"]
    return comparacion.melt(id_vars="materia", value_vars=indicadores, var_name="indicador", value_name="valor")


# ----------------------------------------------------------------------------
# Todos los KPI
# ----------------------------------------------------------------------------
def calcular_kpis_calificaciones(datos=None, ancho_bin: int = 10, matriculados: bool = True) -> dict[str, pd.DataFrame]:
    """Lee los datos integrados y devuelve los KPI de calificaciones como DataFrames.

    Claves: promedio_general, promedio_por_tipo, distribucion_notas, condicion_academica, comparacion.
    """
    integrado = (Path(datos) if datos else DATOS_POR_DEFECTO) / "integrado"
    calificaciones = pd.read_parquet(integrado / "calificaciones_integrado.parquet")
    cruce = pd.read_parquet(integrado / "cruce_matriculados_integrado.parquet")
    return {
        "promedio_general": promedio_general_por_asignatura(calificaciones, cruce, matriculados),
        "promedio_por_tipo": promedio_por_tipo_evaluacion(calificaciones, cruce, matriculados),
        "distribucion_notas": distribucion_de_notas(calificaciones, cruce, ancho_bin, matriculados),
        "condicion_academica": condicion_academica(calificaciones, cruce, matriculados),
        "comparacion": comparar_asignaturas(calificaciones, cruce, matriculados),
    }
