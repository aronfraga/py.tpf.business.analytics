from typing import Any, Dict
import html
import pandas as pd
import streamlit as st

EMPTY_TEXT: str = "—"

def table(data: pd.DataFrame, title: str, labels: Dict[str, str]) -> None:
    colored_table(data, title, labels)

def colored_table(data: pd.DataFrame, title: str, labels: Dict[str, str]) -> None:
    title_html: str = '<div class="table-title">' + html.escape(title) + "</div>"
    header_cells: str = ""
    body_rows: str = ""

    for column_name, label in labels.items():
        header_cells = header_cells + "<th>" + html.escape(label) + "</th>"

    for row in data.itertuples(index=False):
        cells: str = ""

        for column_name in labels.keys():
            value: Any = getattr(row, column_name)
            text: str = EMPTY_TEXT if pd.isna(value) else str(value)
            cells = cells + "<td>" + html.escape(text) + "</td>"

        body_rows = body_rows + "<tr>" + cells + "</tr>"

    table_html: str = '<div class="colored-table-wrap"><table class="colored-table"><thead><tr>' + header_cells + "</tr></thead><tbody>" + body_rows + "</tbody></table></div>"
    allow_html: bool = True
    st.markdown(title_html + table_html, unsafe_allow_html=allow_html)
