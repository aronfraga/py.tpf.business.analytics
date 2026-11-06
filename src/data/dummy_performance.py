from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import ALGEBRA, ALGORITHMS, PROBABILITY

INSTRUMENT_COMPARISON_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2", "Recuperatorio"],
    "average": [6.4, 6.9, 7.8, 7.5, 5.6],
}
INSTRUMENT_COMPARISON_ALGEBRA: pd.DataFrame = pd.DataFrame(INSTRUMENT_COMPARISON_ALGEBRA_DATA)

INSTRUMENT_COMPARISON_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2", "TP Integrador"],
    "average": [5.9, 6.3, 7.4, 7.1, 7.8],
}
INSTRUMENT_COMPARISON_ALGORITHMS: pd.DataFrame = pd.DataFrame(INSTRUMENT_COMPARISON_ALGORITHMS_DATA)

INSTRUMENT_COMPARISON_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "Cuestionario 1", "Cuestionario 2", "Recuperatorio"],
    "average": [5.4, 5.8, 6.9, 6.5, 5.0],
}
INSTRUMENT_COMPARISON_PROBABILITY: pd.DataFrame = pd.DataFrame(INSTRUMENT_COMPARISON_PROBABILITY_DATA)

INSTRUMENT_COMPARISON: Dict[str, pd.DataFrame] = {
    ALGEBRA: INSTRUMENT_COMPARISON_ALGEBRA,
    ALGORITHMS: INSTRUMENT_COMPARISON_ALGORITHMS,
    PROBABILITY: INSTRUMENT_COMPARISON_PROBABILITY,
}

GRADE_HISTOGRAM_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "range": ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10"],
    "count": [2, 3, 3, 5, 9, 14, 16, 19, 15, 10],
}
GRADE_HISTOGRAM_ALGEBRA: pd.DataFrame = pd.DataFrame(GRADE_HISTOGRAM_ALGEBRA_DATA)

GRADE_HISTOGRAM_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "range": ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10"],
    "count": [3, 4, 5, 7, 12, 17, 20, 22, 13, 8],
}
GRADE_HISTOGRAM_ALGORITHMS: pd.DataFrame = pd.DataFrame(GRADE_HISTOGRAM_ALGORITHMS_DATA)

GRADE_HISTOGRAM_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "range": ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10"],
    "count": [3, 4, 5, 6, 8, 10, 9, 8, 6, 4],
}
GRADE_HISTOGRAM_PROBABILITY: pd.DataFrame = pd.DataFrame(GRADE_HISTOGRAM_PROBABILITY_DATA)

GRADE_HISTOGRAM: Dict[str, pd.DataFrame] = {
    ALGEBRA: GRADE_HISTOGRAM_ALGEBRA,
    ALGORITHMS: GRADE_HISTOGRAM_ALGORITHMS,
    PROBABILITY: GRADE_HISTOGRAM_PROBABILITY,
}

COURSE_STATUS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "status": ["Libre", "Regular", "Promociona"],
    "count": [18, 41, 37],
}
COURSE_STATUS_ALGEBRA: pd.DataFrame = pd.DataFrame(COURSE_STATUS_ALGEBRA_DATA)

COURSE_STATUS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "status": ["Libre", "Regular", "Promociona"],
    "count": [27, 52, 32],
}
COURSE_STATUS_ALGORITHMS: pd.DataFrame = pd.DataFrame(COURSE_STATUS_ALGORITHMS_DATA)

COURSE_STATUS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "status": ["Libre", "Regular", "Promociona"],
    "count": [21, 29, 13],
}
COURSE_STATUS_PROBABILITY: pd.DataFrame = pd.DataFrame(COURSE_STATUS_PROBABILITY_DATA)

COURSE_STATUS: Dict[str, pd.DataFrame] = {
    ALGEBRA: COURSE_STATUS_ALGEBRA,
    ALGORITHMS: COURSE_STATUS_ALGORITHMS,
    PROBABILITY: COURSE_STATUS_PROBABILITY,
}

PERFORMANCE_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "Los trabajos prácticos obtienen mejores promedios que los parciales. El "
        "recuperatorio muestra el promedio más bajo."
    ),
    ALGORITHMS: (
        "El TP Integrador alcanza el promedio más alto. La distribución de notas se "
        "concentra entre 6 y 8."
    ),
    PROBABILITY: (
        "Los cuestionarios superan a los parciales en promedio. Un tercio de los "
        "estudiantes activos queda en condición Libre."
    ),
}
