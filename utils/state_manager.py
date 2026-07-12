import streamlit as st
from core.models import AppState
import pandas as pd
from typing import Optional

class StateManager:
    """Manages application state in Streamlit session"""
    
    @staticmethod
    def initialize():
        """Initialize default session state"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = AppState()

        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []

        if 'rag_chat' not in st.session_state:
            st.session_state.rag_chat = None

        if 'doc_chunks' not in st.session_state:
            st.session_state.doc_chunks = {}   # filename → chunk list

    @staticmethod
    def get_data() -> Optional[pd.DataFrame]:
        """Get categorized dataframe"""
        return st.session_state.app_state.categorized_df
    
    @staticmethod
    def set_data(df: pd.DataFrame, filename: str):
        """Set categorized dataframe"""
        st.session_state.app_state.categorized_df = df
        st.session_state.app_state.filename = filename
    
    @staticmethod
    def get_view() -> str:
        """Get current view"""
        return st.session_state.app_state.current_view
    
    @staticmethod
    def set_view(view: str):
        """Set current view"""
        st.session_state.app_state.current_view = view
    
    @staticmethod
    def is_web_enabled() -> bool:
        """Check if web search is enabled"""
        return st.session_state.app_state.web_enabled
    
    @staticmethod
    def set_web_enabled(enabled: bool):
        """Set web search state"""
        st.session_state.app_state.web_enabled = enabled
    
    @staticmethod
    def get_model() -> Optional[str]:
        """Selected Ollama model for this session"""
        return st.session_state.app_state.model_name

    @staticmethod
    def set_model(name: str):
        st.session_state.app_state.model_name = name

    @staticmethod
    def is_semantic_enabled() -> bool:
        """Check if semantic search is enabled"""
        return st.session_state.app_state.semantic_enabled
    
    @staticmethod
    def set_semantic_enabled(enabled: bool):
        """Set semantic search state"""
        st.session_state.app_state.semantic_enabled = enabled
