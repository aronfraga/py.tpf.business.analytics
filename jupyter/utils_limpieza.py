"""Funciones de limpieza compartidas por los notebooks de cada asignatura"""
import datetime
import unicodedata

import pandas as pd

PREFIJOS_STAFF = ("STAFF", "DOC")


# ----------------------------------------------------------------------------
# Utilidades generales
# ----------------------------------------------------------------------------
def a_snake_case(columnas):
    """Minúsculas, sin tildes y con "_" en lugar de espacios u otros símbolos."""
    return (columnas.str.strip().str.lower()
            .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
            .str.replace(r"\W+", "_", regex=True))


def sin_tildes(texto):
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii").lower()


def informar_nulos(df, fuente):
    nulos = df.isna().sum()
    nulos = nulos[nulos > 0]
    print(f"  Nulos por columna: {nulos.to_dict() if len(nulos) else 'ninguno'}")


# ----------------------------------------------------------------------------
# Punto 2: estandarización del identificador (ALU_xxxx)
# ----------------------------------------------------------------------------
def estandarizar_usuario(serie, fuente=""):
    """'alu-1001 ', 'ALU 1001', 'ALU_1001' -> 'ALU_1001'.

    Si algún valor no tiene formato ALU_<número>, se frena y se muestran ejemplos.
    """
    s = serie.astype("string").str.strip().str.upper()
    numero = s.str.extract(r"^ALU[\s_\-]*(\d+)$")[0]
    invalidos = s[numero.isna()]
    if len(invalidos):
        raise ValueError(f"{fuente}: {len(invalidos)} identificadores sin formato ALU_xxxx. "
                         f"Ejemplos: {invalidos.unique()[:10].tolist()}")
    return "ALU_" + numero


def filtrar_y_estandarizar_usuarios(df, fuente=""):
    """Descarta staff/docentes y deja el usuario con formato ALU_xxxx."""
    df = df.copy()
    usuario = df["usuario"].astype("string").str.strip().str.upper()
    es_staff = usuario.str.startswith(PREFIJOS_STAFF).fillna(False).astype(bool)
    print(f"{fuente}: staff/docentes excluidos = {int(es_staff.sum())}")
    df = df[~es_staff].copy()
    df["usuario"] = estandarizar_usuario(df["usuario"], fuente)
    return df


def limpiar_reporte(df, fuente=""):
    df.columns = a_snake_case(df.columns)
    df = df.dropna(how="all").dropna(axis=1, how="all").dropna(subset=["usuario", "apellido", "nombre"])
    return filtrar_y_estandarizar_usuarios(df, fuente).reset_index(drop=True)


# ----------------------------------------------------------------------------
# Punto 5: validación de calificaciones
# ----------------------------------------------------------------------------
def validar_notas(df, nombre, notas_max_validas):
    """Descarta notas con nota máxima inesperada o fuera de rango [0, nota_max]."""
    max_invalida = ~df["nota_max"].isin(notas_max_validas)
    fuera_rango = (df["nota_obtenida"] < 0) | (df["nota_obtenida"] > df["nota_max"])
    print(f"{nombre}: nota máxima inesperada = {int(max_invalida.sum())}, "
          f"notas fuera de rango = {int(fuera_rango.sum())}")
    return df[~(max_invalida | fuera_rango)]


# ----------------------------------------------------------------------------
# Punto 6: participación y trazabilidad
# ----------------------------------------------------------------------------
def _convertir(df, col, funcion):
    nulos_antes = df[col].isna().sum()
    df[col] = funcion(df[col])
    nuevos = int(df[col].isna().sum() - nulos_antes)
    if nuevos:
        print(f"  ⚠ {col}: {nuevos} valores no se pudieron convertir (quedan nulos)")


def _a_minutos(valor):
    """'10:07' -> 607.0 (se interpreta HH:MM; con tres partes, HH:MM:SS). Devuelve NaN si no se puede."""
    if pd.isna(valor):
        return float("nan")
    if isinstance(valor, datetime.timedelta):
        return valor.total_seconds() / 60
    if isinstance(valor, datetime.time):
        return valor.hour * 60 + valor.minute + valor.second / 60
    partes = str(valor).strip().split(":")
    try:
        nums = [float(p) for p in partes]
    except ValueError:
        return float("nan")
    if len(nums) == 2:
        return nums[0] * 60 + nums[1]
    if len(nums) == 3:
        return nums[0] * 60 + nums[1] + nums[2] / 60
    return float("nan")


def procesar_participacion(df, fuente="participacion"):
    """Convierte fechas, tiempo y avance; valida consistencia; trata duplicados y nulos."""
    print(f"{fuente}:")
    df = df.copy()
    esperadas = ["fecha_alta", "primera_interaccion", "ultima_interaccion",
                 "tiempo_estimado_de_uso", "avance"]
    faltan = [c for c in esperadas if c not in df.columns]
    if faltan:
        raise KeyError(f"Faltan columnas {faltan}. Columnas disponibles: {df.columns.tolist()}")

    # Fechas (formato dd/mm/aaaa [hh:mm:ss])
    for c in ["fecha_alta", "primera_interaccion", "ultima_interaccion"]:
        if not pd.api.types.is_datetime64_any_dtype(df[c]):
            _convertir(df, c, lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True))

    # Tiempo estimado de uso ("10:07" = 10 h 07 min) -> minutos
    nulos_antes = df["tiempo_estimado_de_uso"].isna().sum()
    df["tiempo_estimado_de_uso_min"] = df["tiempo_estimado_de_uso"].map(_a_minutos)
    nuevos = int(df["tiempo_estimado_de_uso_min"].isna().sum() - nulos_antes)
    if nuevos:
        print(f"  ⚠ tiempo_estimado_de_uso: {nuevos} valores no se pudieron convertir")
    df = df.drop(columns="tiempo_estimado_de_uso")

    # Avance ("86%") -> número 0-100
    df["avance"] = pd.to_numeric(
        df["avance"].astype("string").str.replace("%", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce")

    # Inconsistencias (se marcan, no se eliminan)
    df["fechas_inconsistentes"] = (
        (df["ultima_interaccion"] < df["primera_interaccion"])
        | (df["primera_interaccion"].dt.normalize() < df["fecha_alta"].dt.normalize())
    ).fillna(False)
    numericas = df.select_dtypes("number")
    df["valores_negativos"] = (numericas < 0).any(axis=1)
    df["avance_fuera_de_rango"] = ((df["avance"] < 0) | (df["avance"] > 100)).fillna(False)
    print(f"  Fechas inconsistentes (última < primera, o primera < alta): {int(df['fechas_inconsistentes'].sum())}")
    print(f"  Filas con valores numéricos negativos: {int(df['valores_negativos'].sum())}")
    print(f"  Avance fuera de 0-100: {int(df['avance_fuera_de_rango'].sum())}")
    print(f"  Aulas: {df['aula'].unique().tolist()}")
    print(f"  Perfiles: {df['perfil'].value_counts().to_dict()}")

    # Duplicados: filas idénticas y usuarios repetidos (se conserva el de última interacción más reciente)
    print(f"  Filas duplicadas: {int(df.duplicated().sum())}, usuarios repetidos: {int(df['usuario'].duplicated().sum())}")
    df = (df.drop_duplicates()
            .sort_values("ultima_interaccion")
            .drop_duplicates(subset="usuario", keep="last")
            .sort_index().reset_index(drop=True))

    informar_nulos(df, fuente)  # los nulos de fechas/tiempo se conservan: significan "sin ingreso"
    return df


def procesar_trazabilidad(df, fuente="trazabilidad"):
    """Convierte la fecha, descarta eventos sin fecha válida y duplicados exactos."""
    print(f"{fuente}:")
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    sin_fecha = int(df["fecha"].isna().sum())
    print(f"  Eventos sin fecha válida (descartados): {sin_fecha}")
    df = df.dropna(subset=["fecha"])
    print(f"  Rango de fechas: {df['fecha'].min()} -> {df['fecha'].max()}")
    print(f"  Aulas: {df['aula'].unique().tolist()}")
    print(f"  Perfiles: {df['perfil'].value_counts().to_dict()}")

    # Un evento idéntico en todas las columnas (incluido el segundo) se considera duplicado de exportación
    print(f"  Filas duplicadas (descartadas): {int(df.duplicated().sum())}")
    df = df.drop_duplicates().reset_index(drop=True)

    informar_nulos(df, fuente)
    return df


# ----------------------------------------------------------------------------
# Punto 7: cruce con matriculados
# ----------------------------------------------------------------------------
def cruzar_con_matriculados(df_matriculados, clave_materia, fuentes):
    """Detecta usuarios activos que no figuran como inscriptos.

    fuentes: dict {"trazabilidad": df, "participacion": df, "calificaciones": df}
    Considera "activo" a quien tiene eventos de trazabilidad o calificaciones.
    """
    clave = sin_tildes(clave_materia)
    mat = df_matriculados[df_matriculados["materia"].map(sin_tildes).str.contains(clave)]
    if mat.empty:
        raise ValueError(f"No hay matriculados para '{clave_materia}'. "
                         f"Materias disponibles: {df_matriculados['materia'].unique().tolist()}")
    inscriptos = set(mat["usuario"])
    usuarios_fuente = {n: set(d["usuario"]) for n, d in fuentes.items()}

    todos = sorted(inscriptos.union(*usuarios_fuente.values()))
    cruce = pd.DataFrame({"usuario": todos})
    cruce["matriculado"] = cruce["usuario"].isin(inscriptos)
    for n, u in usuarios_fuente.items():
        cruce[f"en_{n}"] = cruce["usuario"].isin(u)
    cruce = cruce.merge(mat[["usuario", "estado_insc", "instancia"]], on="usuario", how="left")

    activo = cruce["en_trazabilidad"] | cruce["en_calificaciones"]
    es_baja = cruce["estado_insc"].astype("string").str.casefold().eq("baja").fillna(False).astype(bool)
    cruce["activo_no_inscripto"] = ~cruce["matriculado"] & activo
    cruce["activo_con_baja"] = es_baja & activo
    cruce["inscripto_sin_actividad"] = cruce["matriculado"] & ~activo

    print(f"Matriculados ({clave_materia}): {len(inscriptos)}")
    for n, u in usuarios_fuente.items():
        print(f"  {n}: {len(u)} usuarios, {len(u - inscriptos)} no matriculados")
    print(f"Activos no inscriptos: {int(cruce['activo_no_inscripto'].sum())}")
    print(f"Activos con estado Baja: {int(cruce['activo_con_baja'].sum())}")
    print(f"Inscriptos sin actividad: {int(cruce['inscripto_sin_actividad'].sum())}")
    return cruce
