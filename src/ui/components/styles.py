from pathlib import Path
import streamlit as st

THIS_FILE: Path = Path(__file__)
COMPONENTS_DIR: Path = THIS_FILE.resolve().parent
UI_DIR: Path = COMPONENTS_DIR.parent
CSS_FILE_NAME: str = "theme.css"
CSS_PATH: Path = UI_DIR / CSS_FILE_NAME

def inject_styles() -> None:
    encoding: str = "utf-8"
    content: str = CSS_PATH.read_text(encoding=encoding)
    
    html: str = "<style>" + content + "</style>"
    
    allow_html: bool = True
    
    st.markdown(html, unsafe_allow_html=allow_html)
