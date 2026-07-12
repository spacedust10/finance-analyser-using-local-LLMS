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
    def build_chat_service(df=None):
        """Chat service wired to the session's model choice; re-indexes any
        documents already attached this session (embeddings are per-model)."""
        from services.chat_service import ChatService
        from services.ollama_service import installed_models, chat_models, pick_embed_model

        models = installed_models()
        model = StateManager.get_model() or (chat_models(models)[0] if models else None)
        embed = pick_embed_model(models, model) if models else None

        service = ChatService(df, StateManager.is_semantic_enabled(),
                              model_name=model, embed_model=embed)
        service.set_web_enabled(StateManager.is_web_enabled())
        for chunks in st.session_state.doc_chunks.values():
            try:
                service.index_documents(chunks)
            except Exception as e:
                print(f"Document re-index failed: {e}")
        return service
    
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