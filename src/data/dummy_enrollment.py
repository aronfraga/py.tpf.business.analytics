from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import ALGEBRA, ALGORITHMS, PROBABILITY

ENROLLMENT_KPIS: Dict[str, List[Dict[str, str]]] = {
    ALGEBRA: [
        {"title": "Matriculados", "value": "120", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "96", "detail": "Con actividad registrada"},
        {"title": "No inscriptos activos", "value": "3", "detail": "Usuarios sin matrícula"},
        {"title": "Inscriptos sin participación", "value": "4", "detail": "Nunca ingresaron"},
        {"title": "Alertas", "value": "4", "detail": "Estudiantes a revisar"},
    ],
    ALGORITHMS: [
        {"title": "Matriculados", "value": "150", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "111", "detail": "Con actividad registrada"},
        {"title": "No inscriptos activos", "value": "2", "detail": "Usuarios sin matrícula"},
        {"title": "Inscriptos sin participación", "value": "3", "detail": "Nunca ingresaron"},
        {"title": "Alertas", "value": "4", "detail": "Estudiantes a revisar"},
    ],
    PROBABILITY: [
        {"title": "Matriculados", "value": "90", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "63", "detail": "Con actividad registrada"},
        {"title": "No inscriptos activos", "value": "3", "detail": "Usuarios sin matrícula"},
        {"title": "Inscriptos sin participación", "value": "3", "detail": "Nunca ingresaron"},
        {"title": "Alertas", "value": "3", "detail": "Estudiantes a revisar"},
    ],
}

ENROLLED_VS_ACTIVE_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "status": ["Matriculados", "Activos"],
    "count": [120, 96],
}
ENROLLED_VS_ACTIVE_ALGEBRA: pd.DataFrame = pd.DataFrame(ENROLLED_VS_ACTIVE_ALGEBRA_DATA)

ENROLLED_VS_ACTIVE_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "status": ["Matriculados", "Activos"],
    "count": [150, 111],
}
ENROLLED_VS_ACTIVE_ALGORITHMS: pd.DataFrame = pd.DataFrame(ENROLLED_VS_ACTIVE_ALGORITHMS_DATA)

ENROLLED_VS_ACTIVE_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "status": ["Matriculados", "Activos"],
    "count": [90, 63],
}
ENROLLED_VS_ACTIVE_PROBABILITY: pd.DataFrame = pd.DataFrame(ENROLLED_VS_ACTIVE_PROBABILITY_DATA)

ENROLLED_VS_ACTIVE: Dict[str, pd.DataFrame] = {
    ALGEBRA: ENROLLED_VS_ACTIVE_ALGEBRA,
    ALGORITHMS: ENROLLED_VS_ACTIVE_ALGORITHMS,
    PROBABILITY: ENROLLED_VS_ACTIVE_PROBABILITY,
}

NOT_ENROLLED_ACTIVE_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "user": ["u-4012", "u-4187", "u-4230"],
    "sessions": [14, 6, 3],
    "last_activity": ["2025-10-21", "2025-10-17", "2025-10-09"],
}
NOT_ENROLLED_ACTIVE_ALGEBRA: pd.DataFrame = pd.DataFrame(NOT_ENROLLED_ACTIVE_ALGEBRA_DATA)

NOT_ENROLLED_ACTIVE_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "user": ["u-5031", "u-5144"],
    "sessions": [9, 4],
    "last_activity": ["2025-10-22", "2025-10-12"],
}
NOT_ENROLLED_ACTIVE_ALGORITHMS: pd.DataFrame = pd.DataFrame(NOT_ENROLLED_ACTIVE_ALGORITHMS_DATA)

NOT_ENROLLED_ACTIVE_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "user": ["u-6008", "u-6075", "u-6122"],
    "sessions": [11, 7, 2],
    "last_activity": ["2025-10-20", "2025-10-15", "2025-10-03"],
}
NOT_ENROLLED_ACTIVE_PROBABILITY: pd.DataFrame = pd.DataFrame(NOT_ENROLLED_ACTIVE_PROBABILITY_DATA)

NOT_ENROLLED_ACTIVE: Dict[str, pd.DataFrame] = {
    ALGEBRA: NOT_ENROLLED_ACTIVE_ALGEBRA,
    ALGORITHMS: NOT_ENROLLED_ACTIVE_ALGORITHMS,
    PROBABILITY: NOT_ENROLLED_ACTIVE_PROBABILITY,
}

NOT_ENROLLED_ACTIVE_LABELS: Dict[str, str] = {
    "user": "Usuario",
    "sessions": "Sesiones",
    "last_activity": "Última actividad",
}

ENROLLED_NO_PARTICIPATION_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "student": ["Bruno Acosta", "Delfina Paz", "Ramiro Ibáñez", "Julieta Cruz"],
    "enrollment_date": ["2025-08-11", "2025-08-12", "2025-08-14", "2025-08-20"],
    "last_access": ["Nunca", "Nunca", "Nunca", "Nunca"],
}
ENROLLED_NO_PARTICIPATION_ALGEBRA: pd.DataFrame = pd.DataFrame(ENROLLED_NO_PARTICIPATION_ALGEBRA_DATA)

ENROLLED_NO_PARTICIPATION_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "student": ["Emilia Navarro", "Facundo Ortiz", "Pilar Medina"],
    "enrollment_date": ["2025-08-10", "2025-08-13", "2025-08-18"],
    "last_access": ["Nunca", "Nunca", "Nunca"],
}
ENROLLED_NO_PARTICIPATION_ALGORITHMS: pd.DataFrame = pd.DataFrame(ENROLLED_NO_PARTICIPATION_ALGORITHMS_DATA)

ENROLLED_NO_PARTICIPATION_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "student": ["Agustín Peralta", "Renata Vega", "Lautaro Sosa"],
    "enrollment_date": ["2025-08-12", "2025-08-15", "2025-08-19"],
    "last_access": ["Nunca", "Nunca", "Nunca"],
}
ENROLLED_NO_PARTICIPATION_PROBABILITY: pd.DataFrame = pd.DataFrame(ENROLLED_NO_PARTICIPATION_PROBABILITY_DATA)

ENROLLED_NO_PARTICIPATION: Dict[str, pd.DataFrame] = {
    ALGEBRA: ENROLLED_NO_PARTICIPATION_ALGEBRA,
    ALGORITHMS: ENROLLED_NO_PARTICIPATION_ALGORITHMS,
    PROBABILITY: ENROLLED_NO_PARTICIPATION_PROBABILITY,
}

ENROLLED_NO_PARTICIPATION_LABELS: Dict[str, str] = {
    "student": "Estudiante",
    "enrollment_date": "Fecha de inscripción",
    "last_access": "Último acceso",
}

ALERTS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "student": ["Camila Rojas", "Mateo Gómez", "Bruno Acosta", "Delfina Paz"],
    "alert": ["Riesgo de abandono", "Participación en descenso", "Sin ingresos", "Sin ingresos"],
    "detail": [
        "Sin actividad hace 14 días", "Cuatro semanas consecutivas de baja",
        "Inscripto y nunca ingresó", "Inscripta y nunca ingresó",
    ],
}
ALERTS_ALGEBRA: pd.DataFrame = pd.DataFrame(ALERTS_ALGEBRA_DATA)

ALERTS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "student": ["Tomás Herrera", "Valentina Díaz", "Emilia Navarro", "Facundo Ortiz"],
    "alert": ["Riesgo de abandono", "Rendimiento irregular", "Sin ingresos", "Sin ingresos"],
    "detail": [
        "Sin actividad hace 12 días", "Notas dispares entre instrumentos",
        "Inscripta y nunca ingresó", "Inscripto y nunca ingresó",
    ],
}
ALERTS_ALGORITHMS: pd.DataFrame = pd.DataFrame(ALERTS_ALGORITHMS_DATA)

ALERTS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "student": ["Sofía Benítez", "Santiago Ruiz", "Agustín Peralta"],
    "alert": ["Riesgo de abandono", "Participación en descenso", "Sin ingresos"],
    "detail": [
        "Sin actividad hace 16 días", "Tres semanas consecutivas de baja",
        "Inscripto y nunca ingresó",
    ],
}
ALERTS_PROBABILITY: pd.DataFrame = pd.DataFrame(ALERTS_PROBABILITY_DATA)

ALERTS: Dict[str, pd.DataFrame] = {
    ALGEBRA: ALERTS_ALGEBRA,
    ALGORITHMS: ALERTS_ALGORITHMS,
    PROBABILITY: ALERTS_PROBABILITY,
}

ALERTS_LABELS: Dict[str, str] = {
    "student": "Estudiante",
    "alert": "Alerta",
    "detail": "Detalle",
}

ENROLLMENT_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "Ocho de cada diez matriculados están activos. Hay usuarios con actividad que "
        "no figuran en la matrícula y estudiantes inscriptos que nunca ingresaron."
    ),
    ALGORITHMS: (
        "Es la asignatura con más matriculados y la mayor cantidad de estudiantes "
        "inactivos en términos absolutos. Las alertas combinan abandono e "
        "inscripciones sin ingresos."
    ),
    PROBABILITY: (
        "Presenta la menor proporción de estudiantes activos sobre la matrícula. "
        "Todas las alertas corresponden a abandono o falta de ingresos."
    ),
}
