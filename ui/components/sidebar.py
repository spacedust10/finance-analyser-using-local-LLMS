import streamlit as st
from services.file_service import FileService
from services.classification_service import TransactionClassificationService
from services.ollama_service import installed_models, chat_models, pick_embed_model
from services.analysis_service import totals
from utils.state_manager import StateManager

class Sidebar:
    """Sidebar: model choice, file upload, ledger stats, settings"""

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def render(self):
        """Render complete sidebar"""
        self._render_model_picker()
        st.sidebar.markdown("---")
        self._render_file_upload()
        st.sidebar.markdown("---")
        self._render_stats()
        st.sidebar.markdown("---")
        self._render_settings()

    def _render_model_picker(self):
        """Let the user pick any locally installed Ollama model for the session."""
        st.sidebar.markdown("### Model")
        models = installed_models()
        if not models:
            st.sidebar.warning("Ollama not detected — chat and classification are off. "
                               "Start Ollama and reload.")
            return

        options = chat_models(models)
        current = StateManager.get_model()
        if current not in options:
            current = options[0]
            StateManager.set_model(current)

        selected = st.sidebar.selectbox(
            "Ollama model", options, index=options.index(current),
            help="Used for chat, classification and analyst briefs all session"
        )
        if selected != StateManager.get_model():
            StateManager.set_model(selected)
            st.session_state.rag_chat = None   # rebuilt lazily with the new model
        st.sidebar.caption(f"embeddings: {pick_embed_model(models, selected)}")
