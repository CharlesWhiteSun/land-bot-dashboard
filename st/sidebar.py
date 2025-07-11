import streamlit as st

def on_update_click():
    st.toast("資料正在更新中...", icon="🔄")

def on_other_click():
    st.toast("您已點選其他功能...", icon="✨")

def render_sidebar():
    """
    側邊欄元件（選單、按鈕等）
    """
    st.sidebar.title("🔧 功能操作選單")

    st.sidebar.button("🔄 更新內政部房價資訊", on_click=on_update_click)
    st.sidebar.button("✨ 其他功能", on_click=on_other_click)
    st.sidebar.radio("選擇操作項目", ["首頁", "下載資料", "資料分析"])

if "update_clicked" not in st.session_state:
    st.session_state.update_clicked = False

if "other_clicked" not in st.session_state:
    st.session_state.other_clicked = False
