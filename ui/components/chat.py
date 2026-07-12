import streamlit as st

def escape_dollars(text: str) -> str:
    """st.markdown treats $...$ as LaTeX — bare dollar amounts in LLM output
    would render as garbled math. Escape before display."""
    return text.replace("$", r"\$")

class ChatInterface:
    """Chat interface component"""

    @staticmethod
    def render(chat_service):
        """Render chat interface"""
        ChatInterface._render_example_questions()
        ChatInterface._render_chat_history()

        if prompt := st.chat_input("Ask about your finances..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.rerun()

        # last message is the user's → answer it in place so their message is
        # already on screen and the spinner lives inside the assistant bubble
        msgs = st.session_state.chat_messages
        if msgs and msgs[-1]["role"] == "user":
            with st.chat_message("assistant"):
                with st.spinner("Reading your ledger..."):
                    try:
                        response = chat_service.get_response(msgs[-1]["content"])
                    except Exception as e:
                        response = f"Something went wrong: {e}"
            msgs.append({"role": "assistant", "content": response})
            st.rerun()

    @staticmethod
    def _render_example_questions():
        """Render example questions"""
        with st.expander("Example questions", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**About your data**")
                questions = [
                    "What category did I spend the most on?",
                    "Find all coffee-related expenses",
                    "How much did I save this year?",
                    "Show me technology purchases"
                ]
                for i, q in enumerate(questions):
                    if st.button(q, key=f"q1_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": q})
                        st.rerun()

            with col2:
                st.markdown("**General finance**")
                questions = [
                    "USD to EUR exchange rate today",
                    "Best budgeting strategies",
                    "How to build an emergency fund?",
                    "Investment tips for beginners"
                ]
                for i, q in enumerate(questions):
                    if st.button(q, key=f"q2_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": q})
                        st.rerun()

    @staticmethod
    def _render_chat_history():
        """Render chat message history"""
        if not st.session_state.get('chat_messages'):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Welcome to your ledger. Ask me anything about your finances."
                }
            ]

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(escape_dollars(msg["content"]))
