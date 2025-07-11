# app.py
from st.setup import init

init()

import streamlit as st
from services.data_workflow_service import data_ready, run_data_service
from st.sidebar import render_sidebar
from st.main import render_main

render_main()
render_sidebar()

# # 執行房價資料服務
if "data_ready" not in st.session_state:
    st.session_state["data_ready"] = data_ready()

if st.session_state["data_ready"]:
    run_data_service()
