import streamlit as st
from utils.ui_main import ui_main
from utils.ui_slow_loader import show_loading_screen

def ui_init():

    # 主畫面設定
    ui_main()
    show_loading_screen(seconds=3)
    
