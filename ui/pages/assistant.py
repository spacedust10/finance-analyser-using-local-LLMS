import streamlit as st
from config.styles import AppStyles
from ui.components.chat import ChatInterface
from utils.state_manager import StateManager

class AssistantPage:
    """AI Assistant page component"""

    def render(self):
        """Render AI assistant page"""
        df = StateManager.get_data()

        if st.session_state.rag_chat is None and df is not None:
            st.session_state.rag_chat = StateManager.build_chat_service(df)

        chat_service = st.session_state.rag_chat
        doc_count = len(st.session_state.doc_chunks)
        model = chat_service.model_name if chat_service else StateManager.get_model()

        st.markdown(
            AppStyles.chips([
                (f"{len(df)} transactions" if df is not None else "no data", df is not None),
                (model or "no model", model is not None),
                (f"{doc_count} documents" if doc_count else "no documents", doc_count > 0),
                ("web search" if StateManager.is_web_enabled() else "privacy mode", StateManager.is_web_enabled()),
                ("semantic search" if StateManager.is_semantic_enabled() else "standard search", StateManager.is_semantic_enabled()),
            ]),
            unsafe_allow_html=True,
        )

        if chat_service is not None:
            chat_service.set_web_enabled(StateManager.is_web_enabled())

            if StateManager.is_semantic_enabled() and not chat_service.semantic_enabled:
                with st.spinner("Enabling semantic search..."):
                    chat_service.enable_semantic_search()
                st.rerun()
            elif not StateManager.is_semantic_enabled() and chat_service.semantic_enabled:
                chat_service.disable_semantic_search()
                st.rerun()

            ChatInterface.render(chat_service)
        else:
            st.markdown(
                AppStyles.empty_state(
                    "The assistant is waiting on your ledger",
                    "Upload a CSV in the sidebar to start a conversation about your finances."
                ),
                unsafe_allow_html=True,
            )
