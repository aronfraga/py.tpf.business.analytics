from typing import List
import streamlit as st

def selector(label: str, options: List[str], key: str) -> str:
    selection: str = st.selectbox(label, options, key=key)
    return selection
