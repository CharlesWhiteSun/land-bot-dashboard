#setup.py
'''Streamlit Program Entry Point'''
import streamlit as st

# CRITICAL: set_page_config MUST be the first Streamlit command
def init():
    st.set_page_config(
        page_title="房價分析儀表板",
        page_icon="🏡",
        layout="wide",
        initial_sidebar_state="expanded"
    )