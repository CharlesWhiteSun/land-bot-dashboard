import streamlit as st
from interface.error_provider_interface import ErrorProviderInterface
from enums.error_code import ErrorCode


class UIErrorHandler:
    def __init__(self, provider: ErrorProviderInterface):
        self.provider = provider

    def show_error(self, code: ErrorCode, trace_id: str = None):
        error = self.provider.get_error(code, trace_id)
        st.error(f"❌ {error['title']}\n\n{error['message']}\n\n💡 {error['suggest']}")
        if trace_id:
            st.code(f"追蹤代碼：{trace_id}", language="text")
