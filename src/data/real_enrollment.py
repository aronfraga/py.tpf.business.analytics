from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from data.real_common import (
    load_all_traceability,
    load_enrollment_cross,
    load_enrollment_list,
    load_participation,
    sort_by_id_asc,
    sum_tables,
)
from kpis.kpis_matricula import estudiantes_activos, resumen_activos_por_matricula
from constants import (
    ACTIVE_LABEL,
    ACTIVE_OF_ENROLLED_DETAIL_TEMPLATE,
    ALERTS_KEY,
    ALERTS_LABEL,
    ALERT_ACTIVE_WITH_DROP,
    ALERT_DROP_DETAIL_TEMPLATE,
    ALERT_NOT_ENROLLED_ACTIVE,
    ALERT_NOT_ENROLLED_DETAIL_TEMPLATE,
    ALERT_NO_ENTRIES,
    ALERT_NO_ENTRIES_DETAIL,
    ALERT_TABLE_COLUMN,
    CACHE_TTL_SECONDS,
    CARDS_KEY,
    CARD_ALERTS_DETAIL,
    CARD_NEVER_ENTERED_DETAIL,
    CARD_NO_ENROLLMENT_DETAIL,
    CARD_OFFICIAL_ENROLLMENTS_DETAIL,
    COUNT_COLUMN,
    DATE_FORMAT,
    DETAIL_KEY,
    ENROLLED_ACTIVE_COLUMN,
    ENROLLED_COLUMN,
    ENROLLED_LABEL,
    ENROLLED_WITH_ACTIVITY_LABEL,
    ENROLLED_NO_PARTICIPATION_TITLE,
    ENROLLED_VS_ACTIVE_KEY,
    ENROLLMENT_DATE_COLUMN,
    ENROLLMENT_DATE_TABLE_COLUMN,
    ENTRY_COLUMN,
    FIRST_NAME_COLUMN,
    FLAG_ACTIVE_WITH_DROP,
    FLAG_ENROLLED_WITHOUT_ACTIVITY,
    FLAG_NOT_ENROLLED_ACTIVE,
    FULL_NAME_TEMPLATE,
    INTERACTIONS_COLUMN,
    LAST_ACCESS_TABLE_COLUMN,
    LAST_ACTIVITY_TABLE_COLUMN,
    LAST_INTERACTION_COLUMN,
    LAST_NAME_COLUMN,
    NEVER_LABEL,
    NOT_ENROLLED_ACTIVE_COLUMN,
    NOT_ENROLLED_ACTIVE_TITLE,
    NOT_ENROLLED_KEY,
    NO_PARTICIPATION_KEY,
    ONE_DECIMAL_FORMAT,
    PERCENT_FACTOR,
    SESSIONS_COLUMN,
    SPINNER_BUILD_ENROLLMENT,
    STATUS_COLUMN,
    STUDENT_LABEL_TEMPLATE,
    STUDENT_TABLE_COLUMN,
    SUBJECTS,
    SUBJECT_ALL,
    SUBJECT_COLUMN,
    SUBJECT_KEYS,
    TITLE_KEY,
    USER_COLUMN,
    USER_TABLE_COLUMN,
    VALUE_KEY,
    ZERO_PERCENT_TEXT,
)

def format_date(moment: pd.Timestamp) -> str:
    text: str = moment.strftime(DATE_FORMAT)

    return text

def index_participation(participation: pd.DataFrame) -> Dict[Tuple[str, str], Any]:
    index: Dict[Tuple[str, str], Any] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        index[pair] = row

    return index

def index_enrollment_dates(enrollment_list: pd.DataFrame) -> Dict[Tuple[str, str], pd.Timestamp]:
    dates: Dict[Tuple[str, str], pd.Timestamp] = {}

    for row in enrollment_list.itertuples(index=False):
        subject_key: str = getattr(row, SUBJECT_COLUMN)
        user: str = getattr(row, USER_COLUMN)
        moment: pd.Timestamp = getattr(row, ENROLLMENT_DATE_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        dates[pair] = moment

    return dates

def index_sessions(traceability: pd.DataFrame) -> Dict[Tuple[str, str], int]:
    sessions: Dict[Tuple[str, str], int] = {}
    grouped: pd.core.groupby.DataFrameGroupBy = traceability.groupby([SUBJECT_COLUMN, USER_COLUMN])
    counts: pd.Series = grouped[ENTRY_COLUMN].sum()

    for key, value in counts.items():
        subject_key: str = key[0]
        user: str = key[1]
        pair: Tuple[str, str] = (subject_key, user)
        sessions[pair] = int(value)

    return sessions

def select_users(cross: pd.DataFrame, flag_column: str, subject_key: str) -> List[str]:
    has_flag: pd.Series = cross[flag_column]
    is_subject: pd.Series = cross[SUBJECT_COLUMN] == subject_key
    mask: pd.Series = has_flag & is_subject
    selected: pd.DataFrame = cross.loc[mask]
    users: List[str] = sorted(selected[USER_COLUMN].tolist())

    return users

def build_student_label(user: str, participation_row: Any) -> str:
    last_name: str = getattr(participation_row, LAST_NAME_COLUMN)
    first_name: str = getattr(participation_row, FIRST_NAME_COLUMN)
    label: str = STUDENT_LABEL_TEMPLATE.format(user=user, full_name=FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name))

    return label

def build_not_enrolled_table(users: List[str], subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    user_values: List[str] = []
    session_values: List[int] = []
    last_activity_values: List[str] = []

    for user in users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        last_interaction: pd.Timestamp = getattr(participation_row, LAST_INTERACTION_COLUMN)
        user_values.append(user)
        session_values.append(sessions.get(pair, 0))
        last_activity_values.append(format_date(moment=last_interaction))

    table_data: Dict[str, list] = {
        USER_TABLE_COLUMN: user_values,
        SESSIONS_COLUMN: session_values,
        LAST_ACTIVITY_TABLE_COLUMN: last_activity_values,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = [SESSIONS_COLUMN, USER_TABLE_COLUMN]
    sort_order: List[bool] = [False, True]
    result: pd.DataFrame = table.sort_values(by=sort_columns, ascending=sort_order).reset_index(drop=True)

    return result

def build_no_participation_table(users: List[str], subject_key: str, participation_index: Dict[Tuple[str, str], Any], enrollment_dates: Dict[Tuple[str, str], pd.Timestamp]) -> pd.DataFrame:
    students: List[str] = []
    dates: List[str] = []
    last_access: List[str] = []

    for user in users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        student_label: str = build_student_label(user=user, participation_row=participation_row)
        enrollment_moment: pd.Timestamp = enrollment_dates[pair]
        students.append(student_label)
        dates.append(format_date(moment=enrollment_moment))
        last_access.append(NEVER_LABEL)

    table_data: Dict[str, list] = {
        STUDENT_TABLE_COLUMN: students,
        ENROLLMENT_DATE_TABLE_COLUMN: dates,
        LAST_ACCESS_TABLE_COLUMN: last_access,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_alerts_table(cross: pd.DataFrame, subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    students: List[str] = []
    alerts: List[str] = []
    details: List[str] = []
    drop_users: List[str] = select_users(cross=cross, flag_column=FLAG_ACTIVE_WITH_DROP, subject_key=subject_key)
    no_entry_users: List[str] = select_users(cross=cross, flag_column=FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
    not_enrolled_users: List[str] = select_users(cross=cross, flag_column=FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)

    for user in drop_users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        interactions: int = int(getattr(participation_row, INTERACTIONS_COLUMN))
        last_text: str = format_date(moment=getattr(participation_row, LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_ACTIVE_WITH_DROP)
        details.append(ALERT_DROP_DETAIL_TEMPLATE.format(interactions=interactions, last_text=last_text))

    for user in no_entry_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_NO_ENTRIES)
        details.append(ALERT_NO_ENTRIES_DETAIL)

    for user in not_enrolled_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        session_count: int = sessions.get(pair, 0)
        last_text = format_date(moment=getattr(participation_row, LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(ALERT_NOT_ENROLLED_ACTIVE)
        details.append(ALERT_NOT_ENROLLED_DETAIL_TEMPLATE.format(sessions=session_count, last_text=last_text))

    table_data: Dict[str, list] = {
        STUDENT_TABLE_COLUMN: students,
        ALERT_TABLE_COLUMN: alerts,
        DETAIL_KEY: details,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def select_summary_row(summary: pd.DataFrame, subject_key: str) -> pd.Series:
    is_subject: pd.Series = summary[SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = summary.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def build_cards(enrolled_count: int, enrolled_active: int, not_enrolled_active: int, no_participation: int, alerts_count: int) -> List[Dict[str, str]]:
    active_percent: str = format(enrolled_active / enrolled_count * PERCENT_FACTOR, ONE_DECIMAL_FORMAT) if enrolled_count > 0 else ZERO_PERCENT_TEXT
    cards: List[Dict[str, str]] = [
        {TITLE_KEY: ENROLLED_LABEL, VALUE_KEY: str(enrolled_count), DETAIL_KEY: CARD_OFFICIAL_ENROLLMENTS_DETAIL},
        {TITLE_KEY: ENROLLED_WITH_ACTIVITY_LABEL, VALUE_KEY: str(enrolled_active), DETAIL_KEY: ACTIVE_OF_ENROLLED_DETAIL_TEMPLATE.format(percent=active_percent)},
        {TITLE_KEY: NOT_ENROLLED_ACTIVE_TITLE, VALUE_KEY: str(not_enrolled_active), DETAIL_KEY: CARD_NO_ENROLLMENT_DETAIL},
        {TITLE_KEY: ENROLLED_NO_PARTICIPATION_TITLE, VALUE_KEY: str(no_participation), DETAIL_KEY: CARD_NEVER_ENTERED_DETAIL},
        {TITLE_KEY: ALERTS_LABEL, VALUE_KEY: str(alerts_count), DETAIL_KEY: CARD_ALERTS_DETAIL},
    ]

    return cards

def sum_cards(cards: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    per_subject: List[List[Dict[str, str]]] = list(cards.values())
    totals: List[int] = []

    for position in range(len(per_subject[0])):
        total: int = sum(int(subject_cards[position][VALUE_KEY]) for subject_cards in per_subject)
        totals.append(total)

    enrolled_total, active_total, not_enrolled_total, no_participation_total, alerts_total = totals
    result: List[Dict[str, str]] = build_cards(enrolled_count=enrolled_total, enrolled_active=active_total, not_enrolled_active=not_enrolled_total, no_participation=no_participation_total, alerts_count=alerts_total)

    return result

def build_enrolled_vs_active(enrolled_count: int, enrolled_active: int) -> pd.DataFrame:
    table_data: Dict[str, list] = {
        STATUS_COLUMN: [ENROLLED_LABEL, ACTIVE_LABEL],
        COUNT_COLUMN: [enrolled_count, enrolled_active],
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=SPINNER_BUILD_ENROLLMENT)
def build_all() -> Dict[str, Dict[str, Any]]:
    participation: pd.DataFrame = load_participation()
    cross: pd.DataFrame = load_enrollment_cross()
    enrollment_list: pd.DataFrame = load_enrollment_list()
    traceability: pd.DataFrame = load_all_traceability()
    participation_index: Dict[Tuple[str, str], Any] = index_participation(participation=participation)
    enrollment_dates: Dict[Tuple[str, str], pd.Timestamp] = index_enrollment_dates(enrollment_list=enrollment_list)
    sessions: Dict[Tuple[str, str], int] = index_sessions(traceability=traceability)
    active_students: pd.DataFrame = estudiantes_activos(participacion=participation, cruce=cross)
    summary: pd.DataFrame = resumen_activos_por_matricula(activos=active_students)
    cards: Dict[str, List[Dict[str, str]]] = {}
    enrolled_vs_active: Dict[str, pd.DataFrame] = {}
    not_enrolled: Dict[str, pd.DataFrame] = {}
    no_participation: Dict[str, pd.DataFrame] = {}
    alerts: Dict[str, pd.DataFrame] = {}

    for subject in SUBJECTS:
        subject_key: str = SUBJECT_KEYS[subject]
        summary_row: pd.Series = select_summary_row(summary=summary, subject_key=subject_key)
        enrolled_users: List[str] = select_users(cross=cross, flag_column=ENROLLED_COLUMN, subject_key=subject_key)
        not_enrolled_users: List[str] = select_users(cross=cross, flag_column=FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)
        no_participation_users: List[str] = select_users(cross=cross, flag_column=FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
        not_enrolled[subject] = build_not_enrolled_table(users=not_enrolled_users, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        no_participation_table: pd.DataFrame = build_no_participation_table(users=no_participation_users, subject_key=subject_key, participation_index=participation_index, enrollment_dates=enrollment_dates)
        no_participation[subject] = no_participation_table.assign(subject=subject)
        alerts[subject] = build_alerts_table(cross=cross, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        enrolled_count: int = len(enrolled_users)
        enrolled_active_count: int = int(summary_row[ENROLLED_ACTIVE_COLUMN])
        not_enrolled_active_count: int = int(summary_row[NOT_ENROLLED_ACTIVE_COLUMN])
        alerts_count: int = len(alerts[subject])
        cards[subject] = build_cards(
            enrolled_count=enrolled_count,
            enrolled_active=enrolled_active_count,
            not_enrolled_active=not_enrolled_active_count,
            no_participation=len(no_participation_users),
            alerts_count=alerts_count,
        )
        enrolled_vs_active[subject] = build_enrolled_vs_active(enrolled_count=enrolled_count, enrolled_active=enrolled_active_count)

    not_enrolled[SUBJECT_ALL] = pd.concat(list(not_enrolled.values()), ignore_index=True)
    no_participation[SUBJECT_ALL] = pd.concat(list(no_participation.values()), ignore_index=True)
    alerts[SUBJECT_ALL] = pd.concat(list(alerts.values()), ignore_index=True)
    for subject_name in list(alerts.keys()):
        not_enrolled[subject_name] = sort_by_id_asc(not_enrolled[subject_name], USER_TABLE_COLUMN)
        no_participation[subject_name] = sort_by_id_asc(no_participation[subject_name], STUDENT_TABLE_COLUMN)
        alerts[subject_name] = sort_by_id_asc(alerts[subject_name], STUDENT_TABLE_COLUMN)

    cards[SUBJECT_ALL] = sum_cards(cards=cards)
    enrolled_vs_active[SUBJECT_ALL] = sum_tables(list(enrolled_vs_active.values()), [STATUS_COLUMN], [COUNT_COLUMN])

    result: Dict[str, Dict[str, Any]] = {
        CARDS_KEY: cards,
        ENROLLED_VS_ACTIVE_KEY: enrolled_vs_active,
        NOT_ENROLLED_KEY: not_enrolled,
        NO_PARTICIPATION_KEY: no_participation,
        ALERTS_KEY: alerts,
    }

    return result
