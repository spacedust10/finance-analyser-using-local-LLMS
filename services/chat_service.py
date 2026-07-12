import pandas as pd
from rag_finance_chat import RAGFinanceChat

class ChatService:
    """Service wrapper for RAG chat functionality"""

    def __init__(self, data: pd.DataFrame = None, use_semantic_search: bool = False,
                 model_name: str = None, embed_model: str = None):
        self._chat = RAGFinanceChat(data, use_semantic_search,
                                    model_name=model_name, embed_model=embed_model)

    @property
    def semantic_enabled(self) -> bool:
        return self._chat.use_semantic_search

    @property
    def model_name(self) -> str:
        return self._chat.model_name

    @property
    def document_names(self) -> list:
        return self._chat.document_names

    def get_response(self, query: str) -> str:
        return self._chat.get_response(query)

    def analyst_verdict(self) -> str:
        return self._chat.analyst_verdict()

    def index_documents(self, chunks: list) -> int:
        return self._chat.index_documents(chunks)

    def clear_documents(self) -> None:
        self._chat.clear_documents()

    def set_web_enabled(self, enabled: bool) -> None:
        self._chat.set_web_enabled(enabled)

    def enable_semantic_search(self) -> None:
        self._chat.enable_semantic_search()

    def disable_semantic_search(self) -> None:
        self._chat.disable_semantic_search()
