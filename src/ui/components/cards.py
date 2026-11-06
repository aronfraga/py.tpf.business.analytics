from typing import Dict, List
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

def kpi_card(card: Dict[str, str]) -> None:
    title: str = card["title"]
    value: str = card["value"]
    detail: str = card["detail"]
    html: str = '<div class="kpi-card">' + '<div class="kpi-title">' + title + "</div>" + '<div class="kpi-value">' + value + "</div>" + '<div class="kpi-detail">' + detail + "</div>" + "</div>"
    allow_html: bool = True
    
    st.markdown(html, unsafe_allow_html=allow_html)

def card_row(cards: List[Dict[str, str]]) -> None:
    column_count: int = len(cards)
    columns: List[DeltaGenerator] = st.columns(column_count)
    index: int = 0
    
    for card in cards:
        column: DeltaGenerator = columns[index]
        with column:
            kpi_card(card)
        index = index + 1
