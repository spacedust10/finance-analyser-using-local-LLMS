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

    def _render_file_upload(self):
        """Render file upload section"""
        st.sidebar.markdown("### Upload")

        uploaded_file = st.sidebar.file_uploader(
            "Choose CSV file",
            type="csv",
            help="Upload your bank statement CSV"
        )

        if uploaded_file:
            if st.sidebar.button("Process file", type="primary"):
                self._process_file(uploaded_file)

    def _process_file(self, uploaded_file):
        """Process uploaded file"""
        try:
            progress = st.sidebar.progress(0)
            status = st.sidebar.empty()

            status.text("Reading file...")
            progress.progress(20)
            df = self.file_service.read_file(uploaded_file)

            status.text("Cleaning data...")
            progress.progress(40)
            df = self.file_service.process(df)
            # warnings persist in session state — inline st.sidebar.warning
            # vanishes on the next rerun before the user can read it
            warnings = []
            if df.attrs.get('dropped_rows'):
                warnings.append(f"Skipped {df.attrs['dropped_rows']} rows with invalid date/amount/type")

            status.text("Classifying with local AI...")
            progress.progress(70)
            try:
                classifier = TransactionClassificationService(model_name=StateManager.get_model())
                df = classifier.process_dataframe(df)
            except Exception as e:
                df['Category'] = 'Uncategorized'
                warnings.append(f"AI classification skipped (is Ollama running?): {e}")

            st.session_state.data_warnings = warnings
            st.session_state.chat_messages = []  # new data → old transcript is about the old file
            StateManager.set_data(df, uploaded_file.name)
            st.session_state.rag_chat = StateManager.build_chat_service(df)

            progress.progress(100)
            status.empty()
            st.sidebar.success(f"Processed {len(df)} transactions")

        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

    def _render_stats(self):
        """Render quick stats"""
        df = StateManager.get_data()

        if df is not None:
            st.sidebar.markdown("### Ledger")

            for w in st.session_state.get('data_warnings', []):
                st.sidebar.warning(f"⚠ {w}")

            income, expenses, savings, _ = totals(df)

            st.sidebar.metric("Income", f"${income:,.0f}")
            st.sidebar.metric("Expenses", f"${expenses:,.0f}")
            st.sidebar.metric("Net savings", f"${savings:,.0f}")
            st.sidebar.caption(f"{len(df)} transactions on file")

    def _render_settings(self):
        """Render settings section"""
        st.sidebar.markdown("### Settings")

        web_enabled = st.sidebar.toggle("Enable web search", value=StateManager.is_web_enabled())
        StateManager.set_web_enabled(web_enabled)

        if web_enabled:
            st.sidebar.caption("Live rates & news available to the assistant")
        else:
            st.sidebar.caption("Nothing leaves this machine")

        semantic_enabled = st.sidebar.toggle(
            "Semantic search",
            value=StateManager.is_semantic_enabled(),
            help="Embedding-based fuzzy matching over your transactions"
        )
        StateManager.set_semantic_enabled(semantic_enabled)

        st.sidebar.caption("Theme follows the app setting (⋮ → Settings → Appearance); "
                           "charts adapt automatically.")
