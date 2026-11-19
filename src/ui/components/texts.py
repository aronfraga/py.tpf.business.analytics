import streamlit as st

def section_title(text: str) -> None:
    html: str = '<div class="section-title">' + text + "</div>"
    allow_html: bool = True
    st.markdown(html, unsafe_allow_html=allow_html)
