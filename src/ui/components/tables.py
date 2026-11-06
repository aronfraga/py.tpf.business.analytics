from typing import Any, Dict

import pandas as pd
import streamlit as st

def table(data: pd.DataFrame, title: str, labels: Dict[str, str]) -> None:
    title_html: str = '<div class="table-title">' + title + "</div>"
    allow_html: bool = True
    
    st.markdown(title_html, unsafe_allow_html=allow_html)
    
    column_config: Dict[str, Any] = {}
    
    for column_name, label in labels.items():
        column: Any = st.column_config.Column(label=label)
        column_config[column_name] = column
    
    hide_index: bool = True
    st.dataframe(data, hide_index=hide_index, column_config=column_config)
