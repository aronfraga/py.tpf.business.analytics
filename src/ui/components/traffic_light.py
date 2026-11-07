import streamlit as st

def traffic_light(color: str, text: str) -> None:
    bulb_class: str = "traffic-light-bulb traffic-light-" + color
    title: str = "Semáforo"
    html: str = '<div class="traffic-light">' + '<div class="' + bulb_class + '"></div>' + "<div>" + '<div class="traffic-light-title">' + title + "</div>" + '<div class="traffic-light-text">' + text + "</div>" + "</div>" + "</div>"
    allow_html: bool = True
    st.markdown(html, unsafe_allow_html=allow_html)
