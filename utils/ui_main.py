import streamlit as st

def ui_main():

    # 主畫面
    st.title("🏡 房價分析儀表板")
    st.write("主畫面")

    # 測邊欄
    st.sidebar.header("🖱 選單")
    if st.sidebar.button("🔔 PING!", type="primary", help="顯示 PING 通知"):
        st.toast("✅ PING!", icon="🔔")
    if st.sidebar.button("💥 PANG!", type="primary", help="顯示 PANG 通知"):
        st.toast("⚠️ PANG!", icon="💥")

