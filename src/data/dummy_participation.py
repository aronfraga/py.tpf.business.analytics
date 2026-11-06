from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import (
    ALGEBRA,
    ALGORITHMS,
    PROBABILITY,
    RANGE_2_WEEKS,
    RANGE_4_WEEKS,
    RANGE_ALL,
)

ACTIVITY_ALL_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "activities": [310, 355, 420, 480, 455, 520, 540, 505, 560, 590],
}
ACTIVITY_ALL_ALGEBRA: pd.DataFrame = pd.DataFrame(ACTIVITY_ALL_ALGEBRA_DATA)

ACTIVITY_ALL_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "activities": [420, 470, 560, 640, 615, 700, 735, 690, 760, 800],
}
ACTIVITY_ALL_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACTIVITY_ALL_ALGORITHMS_DATA)

ACTIVITY_ALL_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "activities": [210, 240, 275, 310, 290, 335, 350, 325, 360, 380],
}
ACTIVITY_ALL_PROBABILITY: pd.DataFrame = pd.DataFrame(ACTIVITY_ALL_PROBABILITY_DATA)

ACTIVITY_4_WEEKS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "activities": [78, 85, 92, 88, 96, 101, 94, 105],
}
ACTIVITY_4_WEEKS_ALGEBRA: pd.DataFrame = pd.DataFrame(ACTIVITY_4_WEEKS_ALGEBRA_DATA)

ACTIVITY_4_WEEKS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "activities": [110, 118, 126, 121, 133, 139, 130, 145],
}
ACTIVITY_4_WEEKS_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACTIVITY_4_WEEKS_ALGORITHMS_DATA)

ACTIVITY_4_WEEKS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "activities": [52, 57, 61, 58, 64, 68, 63, 71],
}
ACTIVITY_4_WEEKS_PROBABILITY: pd.DataFrame = pd.DataFrame(ACTIVITY_4_WEEKS_PROBABILITY_DATA)

ACTIVITY_2_WEEKS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "activities": [96, 41, 102, 98, 38, 105, 110],
}
ACTIVITY_2_WEEKS_ALGEBRA: pd.DataFrame = pd.DataFrame(ACTIVITY_2_WEEKS_ALGEBRA_DATA)

ACTIVITY_2_WEEKS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "activities": [138, 60, 146, 141, 55, 150, 158],
}
ACTIVITY_2_WEEKS_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACTIVITY_2_WEEKS_ALGORITHMS_DATA)

ACTIVITY_2_WEEKS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "activities": [66, 28, 70, 68, 26, 72, 76],
}
ACTIVITY_2_WEEKS_PROBABILITY: pd.DataFrame = pd.DataFrame(ACTIVITY_2_WEEKS_PROBABILITY_DATA)

ACCESSES_ALL_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "accesses": [220, 245, 290, 330, 315, 360, 372, 350, 385, 402],
}
ACCESSES_ALL_ALGEBRA: pd.DataFrame = pd.DataFrame(ACCESSES_ALL_ALGEBRA_DATA)

ACCESSES_ALL_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "accesses": [300, 330, 395, 450, 430, 490, 515, 480, 530, 560],
}
ACCESSES_ALL_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACCESSES_ALL_ALGORITHMS_DATA)

ACCESSES_ALL_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "accesses": [150, 170, 195, 220, 205, 240, 250, 230, 255, 270],
}
ACCESSES_ALL_PROBABILITY: pd.DataFrame = pd.DataFrame(ACCESSES_ALL_PROBABILITY_DATA)

ACCESSES_4_WEEKS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "accesses": [55, 60, 66, 62, 70, 73, 68, 76],
}
ACCESSES_4_WEEKS_ALGEBRA: pd.DataFrame = pd.DataFrame(ACCESSES_4_WEEKS_ALGEBRA_DATA)

ACCESSES_4_WEEKS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "accesses": [78, 84, 90, 86, 95, 99, 92, 103],
}
ACCESSES_4_WEEKS_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACCESSES_4_WEEKS_ALGORITHMS_DATA)

ACCESSES_4_WEEKS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-09-29", "2025-10-02", "2025-10-06", "2025-10-09", "2025-10-13", "2025-10-16",
        "2025-10-20", "2025-10-23",
    ],
    "accesses": [37, 41, 44, 42, 46, 49, 45, 51],
}
ACCESSES_4_WEEKS_PROBABILITY: pd.DataFrame = pd.DataFrame(ACCESSES_4_WEEKS_PROBABILITY_DATA)

ACCESSES_2_WEEKS_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "accesses": [70, 29, 74, 71, 27, 76, 80],
}
ACCESSES_2_WEEKS_ALGEBRA: pd.DataFrame = pd.DataFrame(ACCESSES_2_WEEKS_ALGEBRA_DATA)

ACCESSES_2_WEEKS_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "accesses": [99, 43, 105, 101, 40, 108, 114],
}
ACCESSES_2_WEEKS_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACCESSES_2_WEEKS_ALGORITHMS_DATA)

ACCESSES_2_WEEKS_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-10-10", "2025-10-12", "2025-10-14", "2025-10-16", "2025-10-18", "2025-10-20",
        "2025-10-22",
    ],
    "accesses": [48, 20, 51, 49, 19, 52, 55],
}
ACCESSES_2_WEEKS_PROBABILITY: pd.DataFrame = pd.DataFrame(ACCESSES_2_WEEKS_PROBABILITY_DATA)

ACTIVITY_BY_DATE: Dict[str, Dict[str, pd.DataFrame]] = {
    RANGE_ALL: {
        ALGEBRA: ACTIVITY_ALL_ALGEBRA,
        ALGORITHMS: ACTIVITY_ALL_ALGORITHMS,
        PROBABILITY: ACTIVITY_ALL_PROBABILITY,
    },
    RANGE_4_WEEKS: {
        ALGEBRA: ACTIVITY_4_WEEKS_ALGEBRA,
        ALGORITHMS: ACTIVITY_4_WEEKS_ALGORITHMS,
        PROBABILITY: ACTIVITY_4_WEEKS_PROBABILITY,
    },
    RANGE_2_WEEKS: {
        ALGEBRA: ACTIVITY_2_WEEKS_ALGEBRA,
        ALGORITHMS: ACTIVITY_2_WEEKS_ALGORITHMS,
        PROBABILITY: ACTIVITY_2_WEEKS_PROBABILITY,
    },
}

ACCESS_EVOLUTION: Dict[str, Dict[str, pd.DataFrame]] = {
    RANGE_ALL: {
        ALGEBRA: ACCESSES_ALL_ALGEBRA,
        ALGORITHMS: ACCESSES_ALL_ALGORITHMS,
        PROBABILITY: ACCESSES_ALL_PROBABILITY,
    },
    RANGE_4_WEEKS: {
        ALGEBRA: ACCESSES_4_WEEKS_ALGEBRA,
        ALGORITHMS: ACCESSES_4_WEEKS_ALGORITHMS,
        PROBABILITY: ACCESSES_4_WEEKS_PROBABILITY,
    },
    RANGE_2_WEEKS: {
        ALGEBRA: ACCESSES_2_WEEKS_ALGEBRA,
        ALGORITHMS: ACCESSES_2_WEEKS_ALGORITHMS,
        PROBABILITY: ACCESSES_2_WEEKS_PROBABILITY,
    },
}

PARTICIPATION_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "La actividad crece de forma sostenida desde el inicio del período y cae de "
        "manera marcada los fines de semana. Los accesos acompañan la misma "
        "tendencia."
    ),
    ALGORITHMS: (
        "Es la asignatura con mayor actividad. El pico de las últimas semanas "
        "coincide con las entregas de trabajos prácticos."
    ),
    PROBABILITY: (
        "La actividad es la más baja de las tres asignaturas, aunque mantiene una "
        "tendencia creciente. Se observa una caída leve en octubre."
    ),
}
