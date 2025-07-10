import streamlit as st
import time

def show_loading_screen(seconds: int = 3) -> None:
    
    placeholder = st.empty()

    # 動畫畫面 + 可透過 JS/CSS 控制顯示與否
    loading_html = """
    <div id="custom-loader" style="display: flex; justify-content: center; align-items: center; height: 50vh;">
        <div style="text-align: center;">
            <div style="font-size: 3.3rem; font-weight: bold; color: #ffffff;">
                🚀 資料初始化中，請稍候...
            </div>
            <div style="margin-top: 30px;">
                <svg width="120" height="120" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                    <circle cx="50" cy="50" fill="none" stroke="#ffffff" stroke-width="10" r="35" 
                            stroke-dasharray="164.93361431346415 56.97787143782138">
                        <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite"
                        dur="1s" values="0 50 50;360 50 50" keyTimes="0;1"></animateTransform>
                    </circle>
                </svg>
            </div>
        </div>
    </div>
    """

    # 顯示畫面
    placeholder.markdown(loading_html, unsafe_allow_html=True)

    # 模擬載入等待
    time.sleep(seconds)

    # 透過 JS + CSS 將 loading 畫面隱藏
    hide_script = """
    <script>
        const loader = document.getElementById("custom-loader");
        if (loader) {
            loader.style.display = "none";
        }
    </script>
    """
    placeholder.markdown(hide_script, unsafe_allow_html=True)
