from typing import Any, Dict, List
import streamlit as st
from streamlit.navigation.page import StreamlitPage
from ui.components.styles import inject_styles

GENERAL_PAGE: Dict[str, Any] = {"path": "ui/pages/general.py", "title": "General", "icon": ":material/dashboard:", "is_default": True}
PARTICIPATION_PAGE: Dict[str, Any] = {"path": "ui/pages/participation.py", "title": "Participación", "icon": ":material/groups:", "is_default": False}
TRACEABILITY_PAGE: Dict[str, Any] = {"path": "ui/pages/traceability.py", "title": "Trazabilidad", "icon": ":material/timeline:", "is_default": False}
PERFORMANCE_PAGE: Dict[str, Any] = {"path": "ui/pages/performance.py", "title": "Rendimiento Académico", "icon": ":material/school:", "is_default": False}
NOTES_VS_PARTICIPATION_PAGE: Dict[str, Any] = {"path": "ui/pages/notes_vs_participation.py", "title": "Notas vs Participación", "icon": ":material/scatter_plot:", "is_default": False}
INDIVIDUAL_PAGE: Dict[str, Any] = {"path": "ui/pages/individual.py", "title": "Individual", "icon": ":material/person:", "is_default": False}
ENROLLMENT_ALERTS_PAGE: Dict[str, Any] = {"path": "ui/pages/enrollment_alerts.py", "title": "Matrícula y Alertas", "icon": ":material/notifications:", "is_default": False}
PAGE_DEFINITIONS: List[Dict[str, Any]] = [GENERAL_PAGE, PARTICIPATION_PAGE, TRACEABILITY_PAGE, PERFORMANCE_PAGE, NOTES_VS_PARTICIPATION_PAGE, INDIVIDUAL_PAGE, ENROLLMENT_ALERTS_PAGE]

def build_page(definition: Dict[str, Any]) -> StreamlitPage:
    path: str = definition["path"]
    title: str = definition["title"]
    icon: str = definition["icon"]
    is_default: bool = definition["is_default"]
    
    page: StreamlitPage = st.Page(path, title=title, icon=icon, default=is_default)
    return page

def main() -> None:
    app_title: str = "Dashboard académico"
    layout: str = "wide"
    st.set_page_config(page_title=app_title, layout=layout)
    inject_styles()
    pages: List[StreamlitPage] = []
    for definition in PAGE_DEFINITIONS:
        page: StreamlitPage = build_page(definition)
        pages.append(page)
    navigation: StreamlitPage = st.navigation(pages)
    navigation.run()

main()
