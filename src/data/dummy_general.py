from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import ALGEBRA, ALGORITHMS, PROBABILITY

GENERAL_KPIS: Dict[str, List[Dict[str, str]]] = {
    ALGEBRA: [
        {"title": "Matriculados", "value": "120", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "96", "detail": "80% de la matrícula"},
        {"title": "Inactivos", "value": "24", "detail": "20% de la matrícula"},
        {"title": "Promedio de notas", "value": "6.8", "detail": "Escala de 0 a 10"},
        {"title": "Promedio de sesiones", "value": "12.4", "detail": "Por estudiante activo"},
    ],
    ALGORITHMS: [
        {"title": "Matriculados", "value": "150", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "111", "detail": "74% de la matrícula"},
        {"title": "Inactivos", "value": "39", "detail": "26% de la matrícula"},
        {"title": "Promedio de notas", "value": "6.2", "detail": "Escala de 0 a 10"},
        {"title": "Promedio de sesiones", "value": "15.8", "detail": "Por estudiante activo"},
    ],
    PROBABILITY: [
        {"title": "Matriculados", "value": "90", "detail": "Estudiantes inscriptos"},
        {"title": "Activos", "value": "63", "detail": "70% de la matrícula"},
        {"title": "Inactivos", "value": "27", "detail": "30% de la matrícula"},
        {"title": "Promedio de notas", "value": "5.9", "detail": "Escala de 0 a 10"},
        {"title": "Promedio de sesiones", "value": "9.7", "detail": "Por estudiante activo"},
    ],
}

ACTIVE_INACTIVE_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "status": ["Activos", "Inactivos"],
    "count": [96, 24],
}
ACTIVE_INACTIVE_ALGEBRA: pd.DataFrame = pd.DataFrame(ACTIVE_INACTIVE_ALGEBRA_DATA)

ACTIVE_INACTIVE_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "status": ["Activos", "Inactivos"],
    "count": [111, 39],
}
ACTIVE_INACTIVE_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACTIVE_INACTIVE_ALGORITHMS_DATA)

ACTIVE_INACTIVE_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "status": ["Activos", "Inactivos"],
    "count": [63, 27],
}
ACTIVE_INACTIVE_PROBABILITY: pd.DataFrame = pd.DataFrame(ACTIVE_INACTIVE_PROBABILITY_DATA)

ACTIVE_INACTIVE: Dict[str, pd.DataFrame] = {
    ALGEBRA: ACTIVE_INACTIVE_ALGEBRA,
    ALGORITHMS: ACTIVE_INACTIVE_ALGORITHMS,
    PROBABILITY: ACTIVE_INACTIVE_PROBABILITY,
}

GRADE_DISTRIBUTION_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "range": ["0-2", "2-4", "4-6", "6-8", "8-10"],
    "count": [5, 8, 23, 35, 25],
}
GRADE_DISTRIBUTION_ALGEBRA: pd.DataFrame = pd.DataFrame(GRADE_DISTRIBUTION_ALGEBRA_DATA)

GRADE_DISTRIBUTION_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "range": ["0-2", "2-4", "4-6", "6-8", "8-10"],
    "count": [7, 12, 29, 42, 21],
}
GRADE_DISTRIBUTION_ALGORITHMS: pd.DataFrame = pd.DataFrame(GRADE_DISTRIBUTION_ALGORITHMS_DATA)

GRADE_DISTRIBUTION_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "range": ["0-2", "2-4", "4-6", "6-8", "8-10"],
    "count": [7, 11, 18, 17, 10],
}
GRADE_DISTRIBUTION_PROBABILITY: pd.DataFrame = pd.DataFrame(GRADE_DISTRIBUTION_PROBABILITY_DATA)

GRADE_DISTRIBUTION: Dict[str, pd.DataFrame] = {
    ALGEBRA: GRADE_DISTRIBUTION_ALGEBRA,
    ALGORITHMS: GRADE_DISTRIBUTION_ALGORITHMS,
    PROBABILITY: GRADE_DISTRIBUTION_PROBABILITY,
}

PARTICIPATION_TREND_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [9.1, 10.4, 11.2, 12.0, 13.1, 12.6, 13.8, 14.2],
}
PARTICIPATION_TREND_ALGEBRA: pd.DataFrame = pd.DataFrame(PARTICIPATION_TREND_ALGEBRA_DATA)

PARTICIPATION_TREND_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [12.3, 13.5, 14.8, 15.9, 16.4, 15.7, 17.2, 17.9],
}
PARTICIPATION_TREND_ALGORITHMS: pd.DataFrame = pd.DataFrame(PARTICIPATION_TREND_ALGORITHMS_DATA)

PARTICIPATION_TREND_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [7.2, 8.1, 8.9, 9.6, 10.2, 9.8, 10.6, 11.0],
}
PARTICIPATION_TREND_PROBABILITY: pd.DataFrame = pd.DataFrame(PARTICIPATION_TREND_PROBABILITY_DATA)

PARTICIPATION_TREND: Dict[str, pd.DataFrame] = {
    ALGEBRA: PARTICIPATION_TREND_ALGEBRA,
    ALGORITHMS: PARTICIPATION_TREND_ALGORITHMS,
    PROBABILITY: PARTICIPATION_TREND_PROBABILITY,
}

GENERAL_INTERPRETATION: str = (
    "Las tres asignaturas muestran una participación creciente a lo largo del "
    "período. Algoritmos y Estructuras de Datos concentra la mayor matrícula y el "
    "mayor promedio de sesiones, mientras que Probabilidad y Estadística presenta "
    "la proporción más alta de estudiantes inactivos."
)
