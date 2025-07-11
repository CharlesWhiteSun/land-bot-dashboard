import streamlit as st
from utils.ui_slow_loader import show_loading_screen
    
def render_main():
    """
    主畫面內容
    """
    st.title("🏡 房價分析儀表板")
    st.subheader("歡迎使用房價資料探索工具")

    st.info("👉 您可透過左側選單進行操作")
    # 你可以加入顯示資料表格、圖表等元件
    # st.dataframe(...), st.plotly_chart(...), etc.

if "update_clicked" not in st.session_state:
    st.session_state.update_clicked = False

if "slow_loading" not in st.session_state:
    show_loading_screen(seconds=3)
