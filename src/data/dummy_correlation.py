from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import ALGEBRA, ALGORITHMS, PROBABILITY

SCATTER_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "sessions": [3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 19, 21],
    "grade": [4.5, 2.5, 5.5, 4.0, 6.5, 5.0, 7.5, 5.5, 7.0, 8.5, 6.5, 9.0],
}
SCATTER_ALGEBRA: pd.DataFrame = pd.DataFrame(SCATTER_ALGEBRA_DATA)

SCATTER_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "sessions": [4, 6, 7, 9, 10, 12, 14, 15, 17, 19, 22, 24],
    "grade": [3.5, 5.0, 3.0, 5.5, 4.5, 6.5, 5.5, 7.0, 6.0, 8.0, 7.5, 8.5],
}
SCATTER_ALGORITHMS: pd.DataFrame = pd.DataFrame(SCATTER_ALGORITHMS_DATA)

SCATTER_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "sessions": [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 16, 18],
    "grade": [3.0, 2.0, 4.5, 3.5, 5.5, 4.0, 6.0, 5.0, 6.5, 5.5, 7.5, 7.0],
}
SCATTER_PROBABILITY: pd.DataFrame = pd.DataFrame(SCATTER_PROBABILITY_DATA)

SCATTER: Dict[str, pd.DataFrame] = {
    ALGEBRA: SCATTER_ALGEBRA,
    ALGORITHMS: SCATTER_ALGORITHMS,
    PROBABILITY: SCATTER_PROBABILITY,
}

TREND_LINE_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "sessions": [3, 21],
    "grade": [3.9, 8.1],
}
TREND_LINE_ALGEBRA: pd.DataFrame = pd.DataFrame(TREND_LINE_ALGEBRA_DATA)

TREND_LINE_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "sessions": [4, 24],
    "grade": [3.7, 8.2],
}
TREND_LINE_ALGORITHMS: pd.DataFrame = pd.DataFrame(TREND_LINE_ALGORITHMS_DATA)

TREND_LINE_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "sessions": [2, 18],
    "grade": [2.7, 7.0],
}
TREND_LINE_PROBABILITY: pd.DataFrame = pd.DataFrame(TREND_LINE_PROBABILITY_DATA)

TREND_LINE: Dict[str, pd.DataFrame] = {
    ALGEBRA: TREND_LINE_ALGEBRA,
    ALGORITHMS: TREND_LINE_ALGORITHMS,
    PROBABILITY: TREND_LINE_PROBABILITY,
}

CORRELATION: Dict[str, Dict[str, str]] = {
    ALGEBRA: {"title": "Correlación sesiones–nota", "value": "0.78", "detail": "Asociación positiva fuerte"},
    ALGORITHMS: {"title": "Correlación sesiones–nota", "value": "0.81", "detail": "Asociación positiva fuerte"},
    PROBABILITY: {"title": "Correlación sesiones–nota", "value": "0.74", "detail": "Asociación positiva fuerte"},
}

CORRELATION_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "A mayor cantidad de sesiones, las notas tienden a ser más altas. Algunos "
        "estudiantes con pocas sesiones obtienen notas medias."
    ),
    ALGORITHMS: (
        "La relación es la más fuerte de las tres asignaturas. Pocas sesiones se "
        "asocian con notas por debajo de 5."
    ),
    PROBABILITY: (
        "La relación es positiva, con mayor dispersión en el tramo medio de sesiones."
    ),
}
