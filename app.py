import os
import streamlit as st
st.set_page_config(page_title="API", page_icon="🎈", layout="wide", initial_sidebar_state="collapsed")
from streamlit_navigation_bar import st_navbar
import pages as pg

pages = ["PBF", "BPC", "RECEITA F", "GITHUB"]
parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "./images/cubes.svg")
# Corrected urls dictionary to match pages list exactly
urls = {"GITHUB": "https://github.com/juvenalculino", "RECEITA F": "https://consultacpf.streamlit.app"}  # Removed the period

# Estilização com CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Defina os estilos
styles = {
    "nav": {
        "background-color": "royalblue",
        "justify-content": "left",
    },
    "img": {
        "padding-right": "10px",
    },
    "span": {
        "color": "white",
        "font-size": "10px",
        "font-weight": "bold",
    },
    "active": {
        "background-color": "white",
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "14px",
    }
}

options = {
    "show_menu": False,
    "show_sidebar": False,
}

page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    options=options,
)

functions = {
    "Home": pg.show_home,
    "PBF": pg.show_pbf,
    "BPC": pg.show_bpc,
}

go_to = functions.get(page)
if go_to:
    go_to()