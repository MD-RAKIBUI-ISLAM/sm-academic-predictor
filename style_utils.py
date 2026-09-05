# style_utils.py

import streamlit as st


def load_css():
    # encoding="utf-8" যোগ করা হয়েছে
    with open("assets/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)