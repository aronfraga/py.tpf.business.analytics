"""Cruces analíticos: relación de la participación y la trazabilidad con las notas.

Entrada : data/integrado/{participacion,trazabilidad,calificaciones,cruce_matriculados}_integrado.parquet
          (generados por integracion.ipynb). La carpeta data/ se busca en la raíz del proyecto.
Salida  : DataFrames de pandas (no se escriben archivos).
Requiere: scipy (pruebas de significancia). Está en requirements.txt.

Para calcular todo de una vez:
    from kpis_cruces import calcular_kpis_cruces
    kpis = calcular_kpis_cruces()
    kpis["participacion_vs_notas"]   # DataFrame

Criterios comunes:
  - Universo: estudiantes matriculados, una fila por estudiante y asignatura.
  - Nota (`nota_pct`): porcentaje del total de puntos rendidos (ver kpis_calificaciones.py). A quienes
    no se presentaron a ningún instrumento se les asigna 0 y se los marca con `se_presento = False`.
  - Participación: tiempo acumulado en la plataforma, en minutos (ver kpis_participacion.py).
  - Trazabilidad: indicadores de uso (días activos, ingresos, semanas activas, interacciones con el
    material y en foros). Se excluyen las interacciones de evaluaciones y calificaciones, porque son
    consecuencia de presentarse a evaluar.

La justificación y los controles de cada cruce están en cruce_participacion_notas.ipynb.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:  # como paquete (kpis.kpis_cruces) o como módulo suelto (kpis_cruces)
    from .kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from .kpis_participacion import tiempo_por_estudiante
    from .kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos
except ImportError:
    from kpis_calificaciones import CONDICIONES, condicion_por_estudiante, nota_por_estudiante
    from kpis_participacion import tiempo_por_estudiante
    from kpis_trazabilidad import cargar_trazabilidad, clasificar_interacciones, marcar_ingresos

# src/kpis/kpis_cruces.py -> raíz del proyecto -> data/
DATOS_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"

CLAVES = ["materia", "usuario"]
GRUPOS = CONDICIONES + ["no se presentó"]
INDICADORES = ["dias_activos", "ingresos", "semanas_activas", "interacciones_material", "interacciones_foros"]


# ----------------------------------------------------------------------------
# Cruce 1: participación (tiempo en la plataforma) vs. notas
# ----------------------------------------------------------------------------
def participacion_vs_notas(participacion: pd.DataFrame, calificaciones: pd.DataFrame,
                           cruce: pd.DataFrame) -> pd.DataFrame:
    """Participación y nota de cada estudiante matriculado, por asignatura.

    A quienes no se presentaron a ningún instrumento se les asigna nota 0.

    Devuelve: materia, usuario, tiempo_min (tiempo acumulado en la plataforma, en minutos),
    nota_pct (0-100) y se_presento (False si no rindió ningún instrumento).
    """
    tiempo = tiempo_por_estudiante(participacion, cruce)
    notas = nota_por_estudiante(calificaciones)[CLAVES + ["nota_pct"]]
    res = tiempo.merge(notas, on=CLAVES, how="left")
    res["se_presento"] = res["nota_pct"].notna()
    res["nota_pct"] = res["nota_pct"].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlacion_participacion_nota(tabla: pd.DataFrame) -> pd.DataFrame:
    """Correlación entre tiempo en la plataforma y nota, por asignatura.

    Se calcula con todas las filas de la tabla recibida. Para ver solo a quienes se presentaron,
    se filtra antes: `correlacion_participacion_nota(tabla[tabla["se_presento"]])`.

    Devuelve: materia, estudiantes, pearson, spearman, pendiente_pp_por_hora (puntos porcentuales
    de nota por cada hora adicional, regresión lineal simple).
    """
    filas = []
    for materia, g in tabla.groupby("materia"):
        pendiente = np.polyfit(g["tiempo_min"], g["nota_pct"], 1)[0] * 60
        filas.append({
            "materia": materia,
            "estudiantes": len(g),
            "pearson": g["tiempo_min"].corr(g["nota_pct"]),
            "spearman": g["tiempo_min"].rank().corr(g["nota_pct"].rank()),
            "pendiente_pp_por_hora": pendiente,
        })
    return pd.DataFrame(filas).round(3)


def linea_de_tendencia(tabla: pd.DataFrame) -> pd.DataFrame:
    """Recta de tendencia (regresión lineal) de la nota según el tiempo, por asignatura.

    Devuelve dos puntos por asignatura: materia, tiempo_min, nota_pct. Tiene las mismas columnas
    que la tabla de puntos, para graficar ambas juntas con `scatter_with_trend`. La recta se
    limita al rango válido de la nota (0 a 100): si el ajuste supera 100 antes del tiempo máximo
    observado, el segundo punto se corta donde la recta llega a 100.
    """
    filas = []
    for materia, g in tabla.groupby("materia"):
        pendiente, ordenada = np.polyfit(g["tiempo_min"], g["nota_pct"], 1)
        x0, x1 = g["tiempo_min"].min(), g["tiempo_min"].max()
        if pendiente > 0:
            x1 = min(x1, (100 - ordenada) / pendiente)
        elif pendiente < 0:
            x1 = min(x1, (0 - ordenada) / pendiente)
        for x in (x0, x1):
            filas.append({"materia": materia, "tiempo_min": x, "nota_pct": pendiente * x + ordenada})
    return pd.DataFrame(filas).round(2)


def nota_por_tramo_de_participacion(tabla: pd.DataFrame, tramos: int = 4) -> pd.DataFrame:
    """Nota promedio según el tramo de tiempo en la plataforma, por asignatura.

    Los estudiantes se dividen en `tramos` grupos de igual tamaño según su tiempo (cuartiles por
    defecto; el tramo 1 es el de menor participación).

    Devuelve: materia, tramo, tiempo_desde_min, tiempo_hasta_min, estudiantes, nota_promedio_pct.
    """
    piezas = []
    for materia, g in tabla.groupby("materia"):
        tramo = pd.qcut(g["tiempo_min"], tramos, duplicates="drop")
        res = (
            g.groupby(tramo, observed=True)
            .agg(tiempo_desde_min=("tiempo_min", "min"), tiempo_hasta_min=("tiempo_min", "max"),
                 estudiantes=("usuario", "size"), nota_promedio_pct=("nota_pct", "mean"))
            .reset_index(drop=True)
        )
        res.insert(0, "tramo", range(1, len(res) + 1))
        res.insert(0, "materia", materia)
        piezas.append(res)
    return pd.concat(piezas, ignore_index=True).round(2)


def graficar_dispersion(tabla: pd.DataFrame, tendencia: pd.DataFrame, correlacion: pd.DataFrame,
                        ruta: Path | None = None):
    """Dispersión tiempo en la plataforma vs. nota (imagen estática), un panel por asignatura.

    Usa matplotlib, que se importa acá para que el resto del módulo no lo requiera. Si se indica
    `ruta`, guarda la imagen. Devuelve la figura.
    """
    import matplotlib.pyplot as plt

    materias = tabla["materia"].unique()
    fig, ejes = plt.subplots(1, len(materias), figsize=(5 * len(materias), 4), sharey=True, squeeze=False)
    for eje, materia in zip(ejes[0], materias):
        p = tabla[tabla["materia"] == materia]
        t = tendencia[tendencia["materia"] == materia]
        r = correlacion.loc[correlacion["materia"] == materia, "pearson"].iloc[0]
        for presento, color, etiqueta in ((True, "#1F5C6B", "Se presentó"), (False, "#B5523B", "No se presentó")):
            q = p[p["se_presento"] == presento]
            eje.scatter(q["tiempo_min"] / 60, q["nota_pct"], s=18, alpha=0.6, color=color, label=etiqueta)
        eje.plot(t["tiempo_min"] / 60, t["nota_pct"], "--", color="#E0A458", linewidth=2)
        eje.set_title(f"{materia.capitalize()} (r = {r:.2f}, n = {len(p)})")
        eje.set_xlabel("Tiempo en la plataforma (horas)")
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0][0].set_ylabel("Nota (% del máximo posible)")
    ejes[0][0].set_ylim(-5, 105)
    ejes[0][-1].legend(loc="lower right", frameon=False)
    fig.suptitle("Tiempo en la plataforma vs. nota", x=0.01, ha="left")
    fig.tight_layout()
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# Cruce 2: tiempo de conexión vs. calificación final
# ----------------------------------------------------------------------------
def prueba_de_correlacion(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    """Correlación entre tiempo de conexión y calificación final, con pruebas de significancia.

    Con `solo_presentados=True` se excluye a quienes no rindieron ningún instrumento.

    Devuelve: materia, estudiantes, pearson, pearson_ic95_inf, pearson_ic95_sup, pearson_p,
    spearman, spearman_p y significativa (ambos p-valores < 0,05).
    """
    datos = tabla[tabla["se_presento"]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby("materia"):
        pearson = stats.pearsonr(g["tiempo_min"], g["nota_pct"])
        ic = pearson.confidence_interval(0.95)
        spearman = stats.spearmanr(g["tiempo_min"], g["nota_pct"])
        filas.append({
            "materia": materia, "estudiantes": len(g),
            "pearson": pearson.statistic, "pearson_ic95_inf": ic.low, "pearson_ic95_sup": ic.high,
            "pearson_p": pearson.pvalue,
            "spearman": spearman.statistic, "spearman_p": spearman.pvalue,
        })
    res = pd.DataFrame(filas)
    res["significativa"] = (res["pearson_p"] < 0.05) & (res["spearman_p"] < 0.05)
    return res.round(4)


def tiempo_por_condicion(tabla: pd.DataFrame, calificaciones: pd.DataFrame, cruce: pd.DataFrame) -> pd.DataFrame:
    """Agrega a la tabla por alumno su condición académica (promocionado, regular, libre o no se presentó)."""
    condicion = condicion_por_estudiante(calificaciones, cruce)[CLAVES + ["condicion"]]
    res = tabla.merge(condicion, on=CLAVES, how="left")
    res["condicion"] = res["condicion"].fillna("no se presentó")
    return res


def resumen_tiempo_por_condicion(tabla_condicion: pd.DataFrame) -> pd.DataFrame:
    """Tiempo en la plataforma por asignatura y condición.

    Devuelve: materia, condicion, estudiantes, promedio_min, mediana_min (incluye grupos vacíos).
    """
    res = (
        tabla_condicion.groupby(["materia", "condicion"])["tiempo_min"]
        .agg(estudiantes="size", promedio_min="mean", mediana_min="median")
    )
    completo = pd.MultiIndex.from_product([sorted(tabla_condicion["materia"].unique()), GRUPOS], names=["materia", "condicion"])
    res = res.reindex(completo).reset_index()
    res["estudiantes"] = res["estudiantes"].fillna(0).astype(int)
    return res.round(1)


def graficar_tiempo_por_condicion(tabla_condicion: pd.DataFrame, ruta: Path | None = None):
    """Diagrama de caja del tiempo en la plataforma (horas) según la condición, un panel por asignatura."""
    import matplotlib.pyplot as plt

    materias = tabla_condicion["materia"].unique()
    fig, ejes = plt.subplots(1, len(materias), figsize=(5 * len(materias), 4.2), sharey=True, squeeze=False)
    for eje, materia in zip(ejes[0], materias):
        p = tabla_condicion[tabla_condicion["materia"] == materia]
        grupos = [g for g in GRUPOS if (p["condicion"] == g).any()]
        datos = [p.loc[p["condicion"] == g, "tiempo_min"] / 60 for g in grupos]
        eje.boxplot(datos, tick_labels=[f"{g}\n(n={len(d)})" for g, d in zip(grupos, datos)], patch_artist=True,
                    boxprops={"facecolor": "#8FB8C2"}, medianprops={"color": "#B5523B"})
        eje.set_title(materia.capitalize())
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0][0].set_ylabel("Tiempo en la plataforma (horas)")
    fig.suptitle("Tiempo de conexión según la condición académica", x=0.01, ha="left")
    fig.tight_layout()
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# Cruce 3: trazabilidad vs. rendimiento
# ----------------------------------------------------------------------------
def indicadores_de_trazabilidad(trazabilidad: pd.DataFrame, cruce: pd.DataFrame,
                                minutos_inactividad: int = 30) -> pd.DataFrame:
    """Indicadores de uso de la plataforma de cada estudiante matriculado, por asignatura.

    Devuelve: materia, usuario, dias_activos, ingresos, semanas_activas, interacciones_material,
    interacciones_foros. Quienes no tienen eventos quedan con 0.
    """
    eventos = marcar_ingresos(trazabilidad, minutos_inactividad)
    tipo = clasificar_interacciones(eventos)
    eventos = eventos.assign(
        semana=eventos["fecha"].dt.to_period("W"),
        es_material=tipo == "Material de estudio",
        es_foro=tipo == "Foros y mensajería",
    )
    indicadores = eventos.groupby(CLAVES).agg(
        dias_activos=("dia", "nunique"),
        ingresos=("es_ingreso", "sum"),
        semanas_activas=("semana", "nunique"),
        interacciones_material=("es_material", "sum"),
        interacciones_foros=("es_foro", "sum"),
    ).reset_index()

    matriculados = cruce.loc[cruce["matriculado"], CLAVES]
    res = matriculados.merge(indicadores, on=CLAVES, how="left").fillna(0)
    res[INDICADORES] = res[INDICADORES].astype(int)
    return res


def trazabilidad_vs_notas(trazabilidad: pd.DataFrame, calificaciones: pd.DataFrame,
                          cruce: pd.DataFrame) -> pd.DataFrame:
    """Indicadores de trazabilidad y nota de cada estudiante matriculado, por asignatura.

    Devuelve: materia, usuario, los indicadores de `indicadores_de_trazabilidad`, nota_pct (0-100,
    con 0 para quienes no se presentaron) y se_presento.
    """
    notas = nota_por_estudiante(calificaciones)[CLAVES + ["nota_pct"]]
    res = indicadores_de_trazabilidad(trazabilidad, cruce).merge(notas, on=CLAVES, how="left")
    res["se_presento"] = res["nota_pct"].notna()
    res["nota_pct"] = res["nota_pct"].fillna(0)
    return res.sort_values(CLAVES).reset_index(drop=True)


def correlaciones_trazabilidad_nota(tabla: pd.DataFrame, solo_presentados: bool = False) -> pd.DataFrame:
    """Correlación de Spearman entre cada indicador de trazabilidad y la nota, por asignatura.

    Con `solo_presentados=True` se excluye a quienes no rindieron ningún instrumento.

    Devuelve (una fila por asignatura e indicador): materia, indicador, estudiantes, spearman,
    p_valor y significativa (p_valor < 0,05).
    """
    datos = tabla[tabla["se_presento"]] if solo_presentados else tabla
    filas = []
    for materia, g in datos.groupby("materia"):
        for indicador in INDICADORES:
            r = stats.spearmanr(g[indicador], g["nota_pct"])
            filas.append({"materia": materia, "indicador": indicador, "estudiantes": len(g),
                          "spearman": r.statistic, "p_valor": r.pvalue})
    res = pd.DataFrame(filas)
    res["significativa"] = res["p_valor"] < 0.05
    return res.round({"spearman": 3, "p_valor": 6})


def matriz_correlaciones(correlaciones: pd.DataFrame) -> pd.DataFrame:
    """Matriz indicador (filas) x asignatura (columnas) con la correlación, para `heatmap`."""
    return correlaciones.pivot(index="indicador", columns="materia", values="spearman").reindex(INDICADORES)


def indicador_mas_relacionado(correlaciones: pd.DataFrame) -> str:
    """Indicador con mayor |correlación| promedio entre asignaturas."""
    return correlaciones.assign(abs_r=correlaciones["spearman"].abs()).groupby("indicador")["abs_r"].mean().idxmax()


def graficar_mapa_correlaciones(versiones: dict[str, pd.DataFrame], ruta: Path | None = None):
    """Mapa de calor indicador x asignatura de las correlaciones (imagen estática); una versión por panel."""
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(1, len(versiones), figsize=(6.5 * len(versiones), 4.2), sharey=True, squeeze=False)
    for eje, (titulo, corr) in zip(ejes[0], versiones.items()):
        matriz = matriz_correlaciones(corr)
        significativa = corr.pivot(index="indicador", columns="materia", values="significativa").reindex(INDICADORES)
        imagen = eje.imshow(matriz.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        eje.set_xticks(range(len(matriz.columns)), [m.capitalize() for m in matriz.columns])
        eje.set_yticks(range(len(matriz.index)), matriz.index)
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                marca = "*" if significativa.iloc[i, j] else ""
                eje.text(j, i, f"{matriz.iloc[i, j]:.2f}{marca}", ha="center", va="center", fontsize=10)
        eje.set_title(titulo)
    fig.colorbar(imagen, ax=ejes[0].tolist(), label="Correlación de Spearman con la nota", shrink=0.85)
    fig.suptitle("Trazabilidad vs. nota (* = p < 0,05)", x=0.01, ha="left")
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


def graficar_dispersion_trazabilidad(tabla: pd.DataFrame, indicador: str, ruta: Path | None = None):
    """Dispersión indicador de trazabilidad vs. nota (imagen estática), un panel por asignatura.

    Los indicadores son enteros y los puntos se apilan, por lo que se les agrega un pequeño
    desplazamiento horizontal aleatorio (solo para dibujar; no altera los datos).
    """
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(0)
    materias = tabla["materia"].unique()
    fig, ejes = plt.subplots(1, len(materias), figsize=(5 * len(materias), 4.4), sharey=True, squeeze=False)
    for eje, materia in zip(ejes[0], materias):
        p = tabla[tabla["materia"] == materia]
        for presento, color, etiqueta in ((True, "#1F5C6B", "Se presentó"), (False, "#B5523B", "No se presentó")):
            q = p[p["se_presento"] == presento]
            x = q[indicador] + rng.uniform(-0.25, 0.25, len(q))
            eje.scatter(x, q["nota_pct"], s=18, alpha=0.6, color=color, label=etiqueta)
        eje.set_title(materia.capitalize())
        eje.set_xlabel(indicador.replace("_", " ").capitalize())
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0][0].set_ylabel("Nota (% del máximo posible)")
    ejes[0][0].set_ylim(-5, 105)
    manijas, etiquetas = ejes[0][0].get_legend_handles_labels()
    fig.legend(manijas, etiquetas, loc="lower center", ncol=2, frameon=False)
    fig.suptitle(f"{indicador.replace('_', ' ').capitalize()} vs. nota", x=0.01, ha="left")
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    if ruta is not None:
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# Todos los cruces
# ----------------------------------------------------------------------------
def calcular_kpis_cruces(datos=None) -> dict[str, pd.DataFrame]:
    """Lee los datos integrados y devuelve los cruces analíticos como DataFrames.

    Claves:
      - participacion_vs_notas: tabla por alumno (tiempo y nota); son los puntos del dispersión.
      - correlacion_participacion, tendencia_participacion, tramos_participacion.
      - prueba_correlacion_todos / prueba_correlacion_presentados: pruebas de significancia.
      - tiempo_por_condicion: tiempo en la plataforma según la condición académica.
      - trazabilidad_vs_notas: tabla por alumno (indicadores de trazabilidad y nota).
      - correlaciones_trazabilidad_todos / correlaciones_trazabilidad_presentados.
    """
    datos = Path(datos) if datos else DATOS_POR_DEFECTO
    integrado = datos / "integrado"
    participacion = pd.read_parquet(integrado / "participacion_integrado.parquet")
    calificaciones = pd.read_parquet(integrado / "calificaciones_integrado.parquet")
    cruce = pd.read_parquet(integrado / "cruce_matriculados_integrado.parquet")
    trazabilidad = cargar_trazabilidad(datos, solo_matriculados=True)

    tabla = participacion_vs_notas(participacion, calificaciones, cruce)
    tabla_traz = trazabilidad_vs_notas(trazabilidad, calificaciones, cruce)
    return {
        "participacion_vs_notas": tabla,
        "correlacion_participacion": correlacion_participacion_nota(tabla),
        "tendencia_participacion": linea_de_tendencia(tabla),
        "tramos_participacion": nota_por_tramo_de_participacion(tabla),
        "prueba_correlacion_todos": prueba_de_correlacion(tabla),
        "prueba_correlacion_presentados": prueba_de_correlacion(tabla, solo_presentados=True),
        "tiempo_por_condicion": resumen_tiempo_por_condicion(tiempo_por_condicion(tabla, calificaciones, cruce)),
        "trazabilidad_vs_notas": tabla_traz,
        "correlaciones_trazabilidad_todos": correlaciones_trazabilidad_nota(tabla_traz),
        "correlaciones_trazabilidad_presentados": correlaciones_trazabilidad_nota(tabla_traz, solo_presentados=True),
    }
