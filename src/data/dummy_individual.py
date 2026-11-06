from typing import Any, Dict, List

import pandas as pd

from data.dummy_common import (
    CAMILA_ROJAS,
    JOAQUIN_SILVA,
    LUCIA_FERNANDEZ,
    MARTINA_LOPEZ,
    MATEO_GOMEZ,
    SANTIAGO_RUIZ,
    SOFIA_BENITEZ,
    TOMAS_HERRERA,
    VALENTINA_DIAZ,
)

LUCIA_FERNANDEZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [8.5, 9.0, 9.5, 8.0],
}
LUCIA_FERNANDEZ_GRADES: pd.DataFrame = pd.DataFrame(LUCIA_FERNANDEZ_GRADES_DATA)

LUCIA_FERNANDEZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [14, 15, 16, 15, 17, 16, 18, 17],
}
LUCIA_FERNANDEZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(LUCIA_FERNANDEZ_PARTICIPATION_DATA)

MATEO_GOMEZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [6.0, 5.5, 7.0, 6.5],
}
MATEO_GOMEZ_GRADES: pd.DataFrame = pd.DataFrame(MATEO_GOMEZ_GRADES_DATA)

MATEO_GOMEZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [10, 9, 11, 8, 9, 7, 8, 6],
}
MATEO_GOMEZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(MATEO_GOMEZ_PARTICIPATION_DATA)

CAMILA_ROJAS_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [3.0, 2.5, 4.5, 2.0],
}
CAMILA_ROJAS_GRADES: pd.DataFrame = pd.DataFrame(CAMILA_ROJAS_GRADES_DATA)

CAMILA_ROJAS_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [6, 5, 4, 3, 2, 2, 1, 0],
}
CAMILA_ROJAS_PARTICIPATION: pd.DataFrame = pd.DataFrame(CAMILA_ROJAS_PARTICIPATION_DATA)

JOAQUIN_SILVA_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [7.5, 8.0, 8.5, 9.0],
}
JOAQUIN_SILVA_GRADES: pd.DataFrame = pd.DataFrame(JOAQUIN_SILVA_GRADES_DATA)

JOAQUIN_SILVA_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [18, 19, 17, 20, 21, 19, 22, 23],
}
JOAQUIN_SILVA_PARTICIPATION: pd.DataFrame = pd.DataFrame(JOAQUIN_SILVA_PARTICIPATION_DATA)

VALENTINA_DIAZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [5.5, 6.0, 4.5, 6.5],
}
VALENTINA_DIAZ_GRADES: pd.DataFrame = pd.DataFrame(VALENTINA_DIAZ_GRADES_DATA)

VALENTINA_DIAZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [12, 11, 13, 10, 9, 11, 8, 9],
}
VALENTINA_DIAZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(VALENTINA_DIAZ_PARTICIPATION_DATA)

TOMAS_HERRERA_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "TP 1", "TP 2"],
    "grade": [2.5, 3.0, 1.0, 2.0],
}
TOMAS_HERRERA_GRADES: pd.DataFrame = pd.DataFrame(TOMAS_HERRERA_GRADES_DATA)

TOMAS_HERRERA_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [5, 4, 4, 2, 3, 1, 1, 0],
}
TOMAS_HERRERA_PARTICIPATION: pd.DataFrame = pd.DataFrame(TOMAS_HERRERA_PARTICIPATION_DATA)

MARTINA_LOPEZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "Cuestionario 1", "Cuestionario 2"],
    "grade": [9.0, 8.5, 9.0, 9.5],
}
MARTINA_LOPEZ_GRADES: pd.DataFrame = pd.DataFrame(MARTINA_LOPEZ_GRADES_DATA)

MARTINA_LOPEZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [11, 12, 12, 13, 14, 13, 15, 14],
}
MARTINA_LOPEZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(MARTINA_LOPEZ_PARTICIPATION_DATA)

SANTIAGO_RUIZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "Cuestionario 1", "Cuestionario 2"],
    "grade": [5.0, 6.5, 6.0, 5.5],
}
SANTIAGO_RUIZ_GRADES: pd.DataFrame = pd.DataFrame(SANTIAGO_RUIZ_GRADES_DATA)

SANTIAGO_RUIZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [9, 8, 9, 7, 8, 6, 7, 6],
}
SANTIAGO_RUIZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(SANTIAGO_RUIZ_PARTICIPATION_DATA)

SOFIA_BENITEZ_GRADES_DATA: Dict[str, List[Any]] = {
    "instrument": ["Parcial 1", "Parcial 2", "Cuestionario 1", "Cuestionario 2"],
    "grade": [3.5, 2.0, 4.0, 3.0],
}
SOFIA_BENITEZ_GRADES: pd.DataFrame = pd.DataFrame(SOFIA_BENITEZ_GRADES_DATA)

SOFIA_BENITEZ_PARTICIPATION_DATA: Dict[str, List[Any]] = {
    "week": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
    "sessions": [5, 4, 3, 3, 2, 2, 1, 1],
}
SOFIA_BENITEZ_PARTICIPATION: pd.DataFrame = pd.DataFrame(SOFIA_BENITEZ_PARTICIPATION_DATA)

STUDENT_DATA: Dict[str, Dict[str, Any]] = {
    LUCIA_FERNANDEZ: {
        "grades": LUCIA_FERNANDEZ_GRADES,
        "participation": LUCIA_FERNANDEZ_PARTICIPATION,
        "traffic_light": "green",
        "traffic_light_text": "Desempeño y participación sostenidos",
    },
    MATEO_GOMEZ: {
        "grades": MATEO_GOMEZ_GRADES,
        "participation": MATEO_GOMEZ_PARTICIPATION,
        "traffic_light": "yellow",
        "traffic_light_text": "Participación en descenso",
    },
    CAMILA_ROJAS: {
        "grades": CAMILA_ROJAS_GRADES,
        "participation": CAMILA_ROJAS_PARTICIPATION,
        "traffic_light": "red",
        "traffic_light_text": "Riesgo de abandono",
    },
    JOAQUIN_SILVA: {
        "grades": JOAQUIN_SILVA_GRADES,
        "participation": JOAQUIN_SILVA_PARTICIPATION,
        "traffic_light": "green",
        "traffic_light_text": "Desempeño y participación sostenidos",
    },
    VALENTINA_DIAZ: {
        "grades": VALENTINA_DIAZ_GRADES,
        "participation": VALENTINA_DIAZ_PARTICIPATION,
        "traffic_light": "yellow",
        "traffic_light_text": "Rendimiento irregular",
    },
    TOMAS_HERRERA: {
        "grades": TOMAS_HERRERA_GRADES,
        "participation": TOMAS_HERRERA_PARTICIPATION,
        "traffic_light": "red",
        "traffic_light_text": "Riesgo de abandono",
    },
    MARTINA_LOPEZ: {
        "grades": MARTINA_LOPEZ_GRADES,
        "participation": MARTINA_LOPEZ_PARTICIPATION,
        "traffic_light": "green",
        "traffic_light_text": "Desempeño y participación sostenidos",
    },
    SANTIAGO_RUIZ: {
        "grades": SANTIAGO_RUIZ_GRADES,
        "participation": SANTIAGO_RUIZ_PARTICIPATION,
        "traffic_light": "yellow",
        "traffic_light_text": "Participación en descenso",
    },
    SOFIA_BENITEZ: {
        "grades": SOFIA_BENITEZ_GRADES,
        "participation": SOFIA_BENITEZ_PARTICIPATION,
        "traffic_light": "red",
        "traffic_light_text": "Riesgo de abandono",
    },
}

GRADES_LABELS: Dict[str, str] = {"instrument": "Instrumento", "grade": "Nota"}
