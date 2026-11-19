from typing import Any, Dict, List, Tuple
from data.services.real_common import (load_all_traceability, load_enrollment_cross, load_enrollment_list, load_participation, sort_by_id_asc)
from data.kpis.kpis_matricula import estudiantes_activos, resumen_activos_por_matricula
import pandas as pd
import streamlit as st
import constants as const

def format_date(moment: pd.Timestamp) -> str:
    text: str = moment.strftime(const.DATE_FORMAT)

    return text

def index_participation(participation: pd.DataFrame) -> Dict[Tuple[str, str], Any]:
    index: Dict[Tuple[str, str], Any] = {}

    for row in participation.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        index[pair] = row

    return index

def index_enrollment_dates(enrollment_list: pd.DataFrame) -> Dict[Tuple[str, str], pd.Timestamp]:
    dates: Dict[Tuple[str, str], pd.Timestamp] = {}

    for row in enrollment_list.itertuples(index=False):
        subject_key: str = getattr(row, const.SUBJECT_COLUMN)
        user: str = getattr(row, const.USER_COLUMN)
        moment: pd.Timestamp = getattr(row, const.ENROLLMENT_DATE_COLUMN)
        pair: Tuple[str, str] = (subject_key, user)
        dates[pair] = moment

    return dates

def index_sessions(traceability: pd.DataFrame) -> Dict[Tuple[str, str], int]:
    sessions: Dict[Tuple[str, str], int] = {}
    grouped: pd.core.groupby.DataFrameGroupBy = traceability.groupby([const.SUBJECT_COLUMN, const.USER_COLUMN])
    counts: pd.Series = grouped[const.ENTRY_COLUMN].sum()

    for key, value in counts.items():
        subject_key: str = key[0]
        user: str = key[1]
        pair: Tuple[str, str] = (subject_key, user)
        sessions[pair] = int(value)

    return sessions

def select_users(cross: pd.DataFrame, flag_column: str, subject_key: str) -> List[str]:
    has_flag: pd.Series = cross[flag_column]
    is_subject: pd.Series = cross[const.SUBJECT_COLUMN] == subject_key
    mask: pd.Series = has_flag & is_subject
    selected: pd.DataFrame = cross.loc[mask]
    users: List[str] = sorted(selected[const.USER_COLUMN].tolist())

    return users

def build_student_label(user: str, participation_row: Any) -> str:
    last_name: str = getattr(participation_row, const.LAST_NAME_COLUMN)
    first_name: str = getattr(participation_row, const.FIRST_NAME_COLUMN)
    label: str = const.STUDENT_LABEL_TEMPLATE.format(
        user=user, full_name=const.FULL_NAME_TEMPLATE.format(last_name=last_name, first_name=first_name))

    return label

def build_not_enrolled_table(users: List[str], subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    user_values: List[str] = []
    session_values: List[int] = []
    last_activity_values: List[str] = []

    for user in users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        last_interaction: pd.Timestamp = getattr(participation_row, const.LAST_INTERACTION_COLUMN)
        user_values.append(build_student_label(user=user, participation_row=participation_row))
        session_values.append(sessions.get(pair, 0))
        last_activity_values.append(format_date(moment=last_interaction))

    table_data: Dict[str, list] = {
        const.USER_TABLE_COLUMN: user_values,
        const.SESSIONS_COLUMN: session_values,
        const.LAST_ACTIVITY_TABLE_COLUMN: last_activity_values,
    }
    table: pd.DataFrame = pd.DataFrame(table_data)
    sort_columns: List[str] = [const.SESSIONS_COLUMN, const.USER_TABLE_COLUMN]
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
        last_access.append(const.NEVER_LABEL)

    table_data: Dict[str, list] = {
        const.STUDENT_TABLE_COLUMN: students,
        const.ENROLLMENT_DATE_TABLE_COLUMN: dates,
        const.LAST_ACCESS_TABLE_COLUMN: last_access,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def build_alerts_table(cross: pd.DataFrame, subject_key: str, participation_index: Dict[Tuple[str, str], Any], sessions: Dict[Tuple[str, str], int]) -> pd.DataFrame:
    students: List[str] = []
    alerts: List[str] = []
    details: List[str] = []
    drop_users: List[str] = select_users(cross=cross, flag_column=const.FLAG_ACTIVE_WITH_DROP, subject_key=subject_key)
    no_entry_users: List[str] = select_users(
        cross=cross, flag_column=const.FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
    not_enrolled_users: List[str] = select_users(
        cross=cross, flag_column=const.FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)

    for user in drop_users:
        pair: Tuple[str, str] = (subject_key, user)
        participation_row: Any = participation_index[pair]
        interactions: int = int(getattr(participation_row, const.INTERACTIONS_COLUMN))
        last_text: str = format_date(moment=getattr(participation_row, const.LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(const.ALERT_ACTIVE_WITH_DROP)
        details.append(const.ALERT_DROP_DETAIL_TEMPLATE.format(interactions=interactions, last_text=last_text))

    for user in no_entry_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(const.ALERT_NO_ENTRIES)
        details.append(const.ALERT_NO_ENTRIES_DETAIL)

    for user in not_enrolled_users:
        pair = (subject_key, user)
        participation_row = participation_index[pair]
        session_count: int = sessions.get(pair, 0)
        last_text = format_date(moment=getattr(participation_row, const.LAST_INTERACTION_COLUMN))
        students.append(build_student_label(user=user, participation_row=participation_row))
        alerts.append(const.ALERT_NOT_ENROLLED_ACTIVE)
        details.append(const.ALERT_NOT_ENROLLED_DETAIL_TEMPLATE.format(sessions=session_count, last_text=last_text))

    table_data: Dict[str, list] = {
        const.STUDENT_TABLE_COLUMN: students,
        const.ALERT_TABLE_COLUMN: alerts,
        const.DETAIL_KEY: details,
    }
    result: pd.DataFrame = pd.DataFrame(table_data)

    return result

def select_summary_row(summary: pd.DataFrame, subject_key: str) -> pd.Series:
    is_subject: pd.Series = summary[const.SUBJECT_COLUMN] == subject_key
    selected: pd.DataFrame = summary.loc[is_subject]
    row: pd.Series = selected.iloc[0]

    return row

def build_cards(enrolled_count: int, enrolled_active: int, not_enrolled_active: int, no_participation: int, alerts_count: int) -> List[Dict[str, str]]:
    active_percent: str = format(enrolled_active / enrolled_count * const.PERCENT_FACTOR, const.ONE_DECIMAL_FORMAT) if enrolled_count > 0 else const.ZERO_PERCENT_TEXT
    cards: List[Dict[str, str]] = [
        {const.TITLE_KEY: const.ENROLLED_LABEL, const.VALUE_KEY: str(enrolled_count), const.DETAIL_KEY: const.CARD_OFFICIAL_ENROLLMENTS_DETAIL},
        {const.TITLE_KEY: const.ENROLLED_WITH_ACTIVITY_LABEL, const.VALUE_KEY: str(enrolled_active), const.DETAIL_KEY: const.ACTIVE_OF_ENROLLED_DETAIL_TEMPLATE.format(percent=active_percent)},
        {const.TITLE_KEY: const.NOT_ENROLLED_ACTIVE_TITLE, const.VALUE_KEY: str(not_enrolled_active), const.DETAIL_KEY: const.CARD_NO_ENROLLMENT_DETAIL},
        {const.TITLE_KEY: const.ENROLLED_NO_PARTICIPATION_TITLE, const.VALUE_KEY: str(no_participation), const.DETAIL_KEY: const.CARD_NEVER_ENTERED_DETAIL},
        {const.TITLE_KEY: const.ALERTS_LABEL, const.VALUE_KEY: str(alerts_count), const.DETAIL_KEY: const.CARD_ALERTS_DETAIL},
    ]

    return cards

def sum_cards(cards: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    per_subject: List[List[Dict[str, str]]] = list(cards.values())
    totals: List[int] = []

    for position in range(len(per_subject[0])):
        total: int = sum(int(subject_cards[position][const.VALUE_KEY]) for subject_cards in per_subject)
        totals.append(total)

    enrolled_total, active_total, not_enrolled_total, no_participation_total, alerts_total = totals
    result: List[Dict[str, str]] = build_cards(enrolled_count=enrolled_total, enrolled_active=active_total, not_enrolled_active=not_enrolled_total, no_participation=no_participation_total, alerts_count=alerts_total)

    return result

@st.cache_data(ttl=const.CACHE_TTL_SECONDS, show_spinner=const.SPINNER_BUILD_ENROLLMENT)
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
    not_enrolled: Dict[str, pd.DataFrame] = {}
    no_participation: Dict[str, pd.DataFrame] = {}
    alerts: Dict[str, pd.DataFrame] = {}

    for subject in const.SUBJECTS:
        subject_key: str = const.SUBJECT_KEYS[subject]
        summary_row: pd.Series = select_summary_row(summary=summary, subject_key=subject_key)
        enrolled_users: List[str] = select_users(
            cross=cross, flag_column=const.ENROLLED_COLUMN, subject_key=subject_key)
        not_enrolled_users: List[str] = select_users(
            cross=cross, flag_column=const.FLAG_NOT_ENROLLED_ACTIVE, subject_key=subject_key)
        no_participation_users: List[str] = select_users(
            cross=cross, flag_column=const.FLAG_ENROLLED_WITHOUT_ACTIVITY, subject_key=subject_key)
        not_enrolled_table: pd.DataFrame = build_not_enrolled_table(
            users=not_enrolled_users, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        not_enrolled[subject] = not_enrolled_table.assign(subject=subject)
        no_participation_table: pd.DataFrame = build_no_participation_table(users=no_participation_users, subject_key=subject_key, participation_index=participation_index, enrollment_dates=enrollment_dates)
        no_participation[subject] = no_participation_table.assign(subject=subject)
        alerts[subject] = build_alerts_table(
            cross=cross, subject_key=subject_key, participation_index=participation_index, sessions=sessions)
        enrolled_count: int = len(enrolled_users)
        enrolled_active_count: int = int(summary_row[const.ENROLLED_ACTIVE_COLUMN])
        not_enrolled_active_count: int = int(summary_row[const.NOT_ENROLLED_ACTIVE_COLUMN])
        alerts_count: int = len(alerts[subject])
        cards[subject] = build_cards(
            enrolled_count=enrolled_count,
            enrolled_active=enrolled_active_count,
            not_enrolled_active=not_enrolled_active_count,
            no_participation=len(no_participation_users),
            alerts_count=alerts_count,
        )

    not_enrolled[const.SUBJECT_ALL] = pd.concat(list(not_enrolled.values()), ignore_index=True)
    no_participation[const.SUBJECT_ALL] = pd.concat(list(no_participation.values()), ignore_index=True)
    alerts[const.SUBJECT_ALL] = pd.concat(list(alerts.values()), ignore_index=True)
    for subject_name in list(alerts.keys()):
        not_enrolled[subject_name] = sort_by_id_asc(not_enrolled[subject_name], const.USER_TABLE_COLUMN)
        no_participation[subject_name] = sort_by_id_asc(no_participation[subject_name], const.STUDENT_TABLE_COLUMN)
        alerts[subject_name] = sort_by_id_asc(alerts[subject_name], const.STUDENT_TABLE_COLUMN)

    cards[const.SUBJECT_ALL] = sum_cards(cards=cards)

    result: Dict[str, Dict[str, Any]] = {
        const.CARDS_KEY: cards,
        const.NOT_ENROLLED_KEY: not_enrolled,
        const.NO_PARTICIPATION_KEY: no_participation,
        const.ALERTS_KEY: alerts,
    }

    return result
