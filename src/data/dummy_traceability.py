from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import ALGEBRA, ALGORITHMS, PROBABILITY

INTERACTIONS_BY_ACTION_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "action": [
        "Ver curso", "Ver recurso", "Ver foro", "Participar en foro", "Entregar tarea",
        "Realizar cuestionario",
    ],
    "count": [1840, 2310, 760, 320, 410, 590],
}
INTERACTIONS_BY_ACTION_ALGEBRA: pd.DataFrame = pd.DataFrame(INTERACTIONS_BY_ACTION_ALGEBRA_DATA)

INTERACTIONS_BY_ACTION_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "action": [
        "Ver curso", "Ver recurso", "Ver foro", "Participar en foro", "Entregar tarea",
        "Realizar cuestionario",
    ],
    "count": [2450, 2980, 1020, 480, 920, 640],
}
INTERACTIONS_BY_ACTION_ALGORITHMS: pd.DataFrame = pd.DataFrame(INTERACTIONS_BY_ACTION_ALGORITHMS_DATA)

INTERACTIONS_BY_ACTION_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "action": [
        "Ver curso", "Ver recurso", "Ver foro", "Participar en foro", "Entregar tarea",
        "Realizar cuestionario",
    ],
    "count": [1210, 1650, 540, 210, 330, 480],
}
INTERACTIONS_BY_ACTION_PROBABILITY: pd.DataFrame = pd.DataFrame(INTERACTIONS_BY_ACTION_PROBABILITY_DATA)

INTERACTIONS_BY_ACTION: Dict[str, pd.DataFrame] = {
    ALGEBRA: INTERACTIONS_BY_ACTION_ALGEBRA,
    ALGORITHMS: INTERACTIONS_BY_ACTION_ALGORITHMS,
    PROBABILITY: INTERACTIONS_BY_ACTION_PROBABILITY,
}

ACTIVITY_HEATMAP_ALGEBRA_ROWS: List[List[int]] = [
    [3, 6, 38, 41, 52, 30],
    [2, 5, 44, 47, 55, 36],
    [4, 7, 40, 45, 58, 41],
    [3, 6, 42, 43, 50, 35],
    [5, 4, 33, 29, 36, 24],
    [8, 2, 14, 18, 22, 26],
    [9, 3, 11, 16, 28, 44],
]
ACTIVITY_HEATMAP_ALGEBRA_INDEX: List[str] = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
ACTIVITY_HEATMAP_ALGEBRA_COLUMNS: List[str] = ["00-04 h", "04-08 h", "08-12 h", "12-16 h", "16-20 h", "20-24 h"]
ACTIVITY_HEATMAP_ALGEBRA: pd.DataFrame = pd.DataFrame(ACTIVITY_HEATMAP_ALGEBRA_ROWS, index=ACTIVITY_HEATMAP_ALGEBRA_INDEX, columns=ACTIVITY_HEATMAP_ALGEBRA_COLUMNS)

ACTIVITY_HEATMAP_ALGORITHMS_ROWS: List[List[int]] = [
    [8, 5, 45, 58, 70, 62],
    [7, 6, 50, 61, 74, 66],
    [9, 6, 47, 60, 77, 71],
    [8, 7, 49, 57, 69, 64],
    [10, 5, 36, 40, 48, 45],
    [14, 3, 18, 25, 34, 52],
    [12, 4, 15, 22, 39, 68],
]
ACTIVITY_HEATMAP_ALGORITHMS_INDEX: List[str] = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
ACTIVITY_HEATMAP_ALGORITHMS_COLUMNS: List[str] = ["00-04 h", "04-08 h", "08-12 h", "12-16 h", "16-20 h", "20-24 h"]
ACTIVITY_HEATMAP_ALGORITHMS: pd.DataFrame = pd.DataFrame(ACTIVITY_HEATMAP_ALGORITHMS_ROWS, index=ACTIVITY_HEATMAP_ALGORITHMS_INDEX, columns=ACTIVITY_HEATMAP_ALGORITHMS_COLUMNS)

ACTIVITY_HEATMAP_PROBABILITY_ROWS: List[List[int]] = [
    [2, 4, 25, 30, 36, 20],
    [3, 5, 28, 33, 38, 24],
    [2, 4, 27, 31, 40, 26],
    [3, 5, 26, 29, 35, 22],
    [4, 3, 20, 19, 24, 16],
    [5, 2, 9, 12, 15, 18],
    [6, 2, 8, 11, 19, 27],
]
ACTIVITY_HEATMAP_PROBABILITY_INDEX: List[str] = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
ACTIVITY_HEATMAP_PROBABILITY_COLUMNS: List[str] = ["00-04 h", "04-08 h", "08-12 h", "12-16 h", "16-20 h", "20-24 h"]
ACTIVITY_HEATMAP_PROBABILITY: pd.DataFrame = pd.DataFrame(ACTIVITY_HEATMAP_PROBABILITY_ROWS, index=ACTIVITY_HEATMAP_PROBABILITY_INDEX, columns=ACTIVITY_HEATMAP_PROBABILITY_COLUMNS)

ACTIVITY_HEATMAP: Dict[str, pd.DataFrame] = {
    ALGEBRA: ACTIVITY_HEATMAP_ALGEBRA,
    ALGORITHMS: ACTIVITY_HEATMAP_ALGORITHMS,
    PROBABILITY: ACTIVITY_HEATMAP_PROBABILITY,
}

TIMELINE_ALGEBRA_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "interactions": [540, 610, 720, 810, 770, 880, 905, 850, 940, 980],
}
TIMELINE_ALGEBRA: pd.DataFrame = pd.DataFrame(TIMELINE_ALGEBRA_DATA)

TIMELINE_ALGORITHMS_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "interactions": [720, 800, 960, 1090, 1040, 1180, 1230, 1150, 1260, 1330],
}
TIMELINE_ALGORITHMS: pd.DataFrame = pd.DataFrame(TIMELINE_ALGORITHMS_DATA)

TIMELINE_PROBABILITY_DATA: Dict[str, List[Any]] = {
    "date": [
        "2025-08-18", "2025-08-25", "2025-09-01", "2025-09-08", "2025-09-15", "2025-09-22",
        "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-20",
    ],
    "interactions": [360, 410, 470, 530, 495, 565, 590, 545, 600, 640],
}
TIMELINE_PROBABILITY: pd.DataFrame = pd.DataFrame(TIMELINE_PROBABILITY_DATA)

TIMELINE: Dict[str, pd.DataFrame] = {
    ALGEBRA: TIMELINE_ALGEBRA,
    ALGORITHMS: TIMELINE_ALGORITHMS,
    PROBABILITY: TIMELINE_PROBABILITY,
}

TRACEABILITY_INTERPRETATION: Dict[str, str] = {
    ALGEBRA: (
        "La mayor parte de las interacciones corresponde a la consulta de recursos. "
        "El uso se concentra entre semana por la tarde y baja los fines de semana."
    ),
    ALGORITHMS: (
        "Las entregas de tareas tienen un peso mayor que en las otras asignaturas. "
        "Hay un uso nocturno sostenido, incluso los domingos."
    ),
    PROBABILITY: (
        "La participación en foros es baja frente a la consulta de recursos. La "
        "franja de 16 a 20 h concentra la mayor actividad."
    ),
}
