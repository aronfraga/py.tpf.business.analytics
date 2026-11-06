import streamlit as st

def section_title(text: str) -> None:
    html: str = '<div class="section-title">' + text + "</div>"
    allow_html: bool = True
    st.markdown(html, unsafe_allow_html=allow_html)

def interpretation(text: str) -> None:
    label: str = "Interpretación"
    html: str = '<div class="interpretation">' + '<span class="interpretation-label">' + label + "</span>" + '<p class="interpretation-text">' + text + "</p>" + "</div>"
    allow_html: bool = True
    st.markdown(html, unsafe_allow_html=allow_html)
