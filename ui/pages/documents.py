import streamlit as st
from config.styles import AppStyles
from services.document_service import DocumentService
from utils.state_manager import StateManager

class DocumentsPage:
    """Attach reference documents (filings, receipts, reports) to the assistant."""

    def render(self):
        st.markdown("### Reference documents")
        st.caption("PDF, TXT or Markdown — 10-K filings, receipts, annual reports. "
                   "Chunked and embedded locally; the assistant cites them as "
                   "[filename, part N] in its answers.")

        files = st.file_uploader(
            "Add documents", type=["pdf", "txt", "md"],
            accept_multiple_files=True, label_visibility="collapsed"
        )

        if files and st.button("Index documents", type="primary"):
            self._index(files)

        chunks_by_file = st.session_state.doc_chunks
        if chunks_by_file:
            st.markdown("#### Indexed")
            for name, chunks in chunks_by_file.items():
                st.markdown(f"- `{name}` — {len(chunks)} chunks")
            if st.button("Clear all documents"):
                st.session_state.doc_chunks = {}
                if st.session_state.rag_chat is not None:
                    st.session_state.rag_chat.clear_documents()
                st.rerun()
        else:
            st.markdown(
                AppStyles.empty_state(
                    "No documents attached",
                    "Add a filing or receipt above and the assistant can quote it back to you."
                ),
                unsafe_allow_html=True,
            )

    def _index(self, files):
        service = DocumentService()
        if st.session_state.rag_chat is None:
            st.session_state.rag_chat = StateManager.build_chat_service(StateManager.get_data())
        chat = st.session_state.rag_chat

        indexed, errors = 0, []
        with st.spinner("Chunking and embedding locally..."):
            for f in files:
                if f.name in st.session_state.doc_chunks:
                    continue   # already indexed this session
                try:
                    chunks = service.chunk(service.extract_text(f), f.name)
                    indexed += chat.index_documents(chunks)
                    st.session_state.doc_chunks[f.name] = chunks
                except Exception as e:
                    errors.append(f"{f.name}: {e}")

        if indexed:
            st.success(f"Indexed {indexed} chunks from {len(st.session_state.doc_chunks)} document(s)")
        for err in errors:
            st.error(f"Failed — {err} (embeddings need Ollama running)")
