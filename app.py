import streamlit as st
from services.data_workflow_service import load_initial_data, run_data_service
from services.ui_initializer import ui_init

# 載入 UI 設定
# if "initialized" not in st.session_state:
#     st.session_state.initialized = True
#     ui_init()
ui_init()

# 執行房價資料服務
if "data_ready" not in st.session_state:
    st.session_state["data_ready"] = load_initial_data()

if st.session_state["data_ready"]:
    run_data_service()
