from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from data.real_common import (
    SUBJECT_KEYS,
    SUBJECTS,
    load_enrolled_traceability,
    load_enrollment_cross,
    load_grades,
    load_participation,
)
from kpis.kpis_calificaciones import condicion_por_estudiante
from kpis.kpis_trazabilidad import frecuencia_ingreso

SUBJECT_COLUMN: str = "materia"
USER_COLUMN: str = "usuario"
ENROLLED_COLUMN: str = "matriculado"
LAST_NAME_COLUMN: str = "apellido"
FIRST_NAME_COLUMN: str = "nombre"
INSTRUMENT_SOURCE_COLUMN: str = "instrumento"
FILE_ID_COLUMN: str = "id_archivo"
OBTAINED_COLUMN: str = "nota_obtenida"
MAXIMUM_COLUMN: str = "nota_max"
CONDITION_COLUMN: str = "condicion"
PERIOD_COLUMN: str = "periodo"
ENTRIES_COLUMN: str = "ingresos"
INSTRUMENT_COLUMN: str = "instrument"
GRADE_COLUMN: str = "grade"
WEEK_COLUMN: str = "week"
SESSIONS_COLUMN: str = "sessions"

WEEKLY_FREQUENCY: str = "W"
WEEK_PREFIX: str = "Sem"
SCALE_FACTOR: float = 10.0
GRADE_DECIMALS: int = 1

GREEN: str = "green"
YELLOW: str = "yellow"
RED: str = "red"

CONDITION_COLORS: Dict[str, str] = {
    "promocionado": GREEN,
    "regular": YELLOW,
    "libre": RED,
}

CONDITION_TEXTS: Dict[str, str] = {
    "promocionado": "Promociona",
    "regular": "Regular",
    "libre": "Libre",
}

NOT_PRESENTED_TEXT: str = "No se presentó"

GRADES_LABELS: Dict[str, str] = {"instrument": "Instrumento", "grade": "Nota"}

def build_names(participation: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    names: Dict[Tuple[str, str], str] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        last_name: str = getattr(row, LAST_NAME_COLUMN)
        first_name: str = getattr(row, FIRST_NAME_COLUMN)
        full_name: str = f"{last_name}, {first_name}"
        pair: Tuple[str, str] = (subject_key, user)
        names[pair] = full_name

    return names

def group_by_pair(table: pd.DataFrame) -> Dict[Tuple[str, str], pd.DataFrame]:
    groups: Dict[Tuple[str, str], pd.DataFrame] = {}
    grouped: pd.core.groupby.DataFrameGroupBy = table.groupby([SUBJECT_COLUMN, USER_COLUMN])

    for key, group in grouped:
        subject_key: str = key[0]
        user: str = key[1]
        pair: Tuple[str, str] = (subject_key, user)
        groups[pair] = group

    return groups

def build_grades_table(student_grades: Optional[pd.DataFrame]) -> pd.DataFrame:
    instruments: List[str] = []
    values: List[float] = []

    if student_grades is not None:
        has_maximum: pd.Series = student_grades[MAXIMUM_COLUMN] > 0
        valid: pd.DataFrame = student_grades.loc[has_maximum]
        ordered: pd.DataFrame = valid.sort_values(FILE_ID_COLUMN)

        for row in ordered.itertuples(index=False):
            instrument: str = getattr(row, INSTRUMENT_SOURCE_COLUMN)
            obtained: float = float(getattr(row, OBTAINED_COLUMN))
            maximum: float = float(getattr(row, MAXIMUM_COLUMN))
            ratio: float = obtained / maximum
            scaled: float = ratio * SCALE_FACTOR
            rounded: float = round(scaled, GRADE_DECIMALS)
            instruments.append(instrument)
            values.append(rounded)

    table_data: Dict[str, list] = {
        INSTRUMENT_COLUMN: instruments,
        GRADE_COLUMN: values,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_participation_table(student_traceability: Optional[pd.DataFrame], periods: List[str]) -> pd.DataFrame:
    entries_by_period: Dict[str, int] = {}

    if student_traceability is not None:
        weekly: pd.DataFrame = frecuencia_ingreso(df=student_traceability, freq=WEEKLY_FREQUENCY)

        for row in weekly.itertuples(index=False):
            period: str = getattr(row, PERIOD_COLUMN)
            entries: int = int(getattr(row, ENTRIES_COLUMN))
            entries_by_period[period] = entries

    weeks: List[str] = []
    sessions: List[int] = []
    week_number: int = 1

    for period_label in periods:
        week_label: str = f"{WEEK_PREFIX} {week_number}"
        period_entries: int = entries_by_period.get(period_label, 0)
        weeks.append(week_label)
        sessions.append(period_entries)
        week_number = week_number + 1

    table_data: Dict[str, list] = {
        WEEK_COLUMN: weeks,
        SESSIONS_COLUMN: sessions,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_traffic_light(condition: Optional[str]) -> Tuple[str, str]:
    color: str
    text: str

    if condition is None:
        color = RED
        text = NOT_PRESENTED_TEXT
    else:
        color = CONDITION_COLORS[condition]
        text = CONDITION_TEXTS[condition]

    result: Tuple[str, str] = (color, text)

    return result

def build_conditions(grades: pd.DataFrame, enrollment_cross: pd.DataFrame) -> Dict[Tuple[str, str], str]:
    conditions_table: pd.DataFrame = condicion_por_estudiante(calificaciones=grades, cruce=enrollment_cross, matriculados=True)
    conditions: Dict[Tuple[str, str], str] = {}

    for row in conditions_table.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        condition: str = getattr(row, CONDITION_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        conditions[pair] = condition

    return conditions

def build_periods(traceability: pd.DataFrame, subject_key: str) -> List[str]:
    is_subject: pd.Series = traceability[SUBJECT_COLUMN] == subject_key
    subject_rows: pd.DataFrame = traceability.loc[is_subject]
    weekly: pd.DataFrame = frecuencia_ingreso(df=subject_rows, freq=WEEKLY_FREQUENCY)
    periods: List[str] = weekly[PERIOD_COLUMN].tolist()
    sorted_periods: List[str] = sorted(periods)

    return sorted_periods

def build_all() -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    participation: pd.DataFrame = load_participation()
    grades: pd.DataFrame = load_grades()
    enrollment_cross: pd.DataFrame = load_enrollment_cross()
    traceability: pd.DataFrame = load_enrolled_traceability()
    names: Dict[Tuple[str, str], str] = build_names(participation=participation)
    grade_groups: Dict[Tuple[str, str], pd.DataFrame] = group_by_pair(table=grades)
    traceability_groups: Dict[Tuple[str, str], pd.DataFrame] = group_by_pair(table=traceability)
    conditions: Dict[Tuple[str, str], str] = build_conditions(grades=grades, enrollment_cross=enrollment_cross)
    is_enrolled: pd.Series = enrollment_cross[ENROLLED_COLUMN]
    enrolled_rows: pd.DataFrame = enrollment_cross.loc[is_enrolled]
    options: List[str] = []
    student_data: Dict[str, Dict[str, Any]] = {}

    for subject in SUBJECTS:
        subject_key: str = SUBJECT_KEYS[subject]
        periods: List[str] = build_periods(traceability=traceability, subject_key=subject_key)
        is_subject: pd.Series = enrolled_rows[SUBJECT_COLUMN] == subject_key
        subject_rows: pd.DataFrame = enrolled_rows.loc[is_subject]
        users: List[str] = sorted(subject_rows[USER_COLUMN].tolist())

        for user in users:
            pair: Tuple[str, str] = (subject_key, user)
            full_name: str = names[pair]
            option: str = f"{user} – {full_name} ({subject})"
            grades_table: pd.DataFrame = build_grades_table(student_grades=grade_groups.get(pair))
            participation_table: pd.DataFrame = build_participation_table(student_traceability=traceability_groups.get(pair), periods=periods)
            color: str
            text: str
            color, text = build_traffic_light(condition=conditions.get(pair))
            options.append(option)
            student_data[option] = {
                "grades": grades_table,
                "participation": participation_table,
                "traffic_light": color,
                "traffic_light_text": text,
            }

    result: Tuple[List[str], Dict[str, Dict[str, Any]]] = (options, student_data)

    return result

ALL_STUDENTS: Tuple[List[str], Dict[str, Dict[str, Any]]] = build_all()

STUDENTS: List[str] = ALL_STUDENTS[0]

STUDENT_DATA: Dict[str, Dict[str, Any]] = ALL_STUDENTS[1]
