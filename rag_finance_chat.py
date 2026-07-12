import re
from typing import Optional

import pandas as pd
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.chat_models import ChatOllama

from config.settings import ModelConfig

ANALYST_STYLE = """STYLE:
- Answer like a personal financial analyst: lead with the number, then the "so what"
- Cite the evidence: name the merchants, dates, and amounts you used from the data
- When document excerpts are provided, cite them as [filename, part N]
- Write dollar amounts in plain text (e.g. "totals 851.01 dollars" or "$851.01")
- Markdown formatting, concise, no filler"""

class RAGFinanceChat:
    """RAG chat over the user's transactions plus optional reference documents."""

    def __init__(self, financial_data=None, use_semantic_search: bool = False,
                 model_name: str = None, embed_model: str = None):
        defaults = ModelConfig()
        self.model_name = model_name or defaults.model_name
        self.embed_model = embed_model or self.model_name
        self.llm = ChatOllama(model=self.model_name, temperature=defaults.temperature)

        self.financial_data = financial_data
        self.use_semantic_search = use_semantic_search
        self.web_enabled = False
        self.chat_history = []
        self.vector_store = None
        self.embeddings = None
        self.document_store = None
        self.document_names = []

        if financial_data is not None and not financial_data.empty:
            self.financial_analysis = self._analyze_financial_data()
            if use_semantic_search:
                self._initialize_semantic_search()
        else:
            self.financial_analysis = None

    # ── indexing ──────────────────────────────────────────────────────────

    def _make_embeddings(self):
        if self.embeddings is None:
            self.embeddings = OllamaEmbeddings(model=self.embed_model)
        return self.embeddings

    def _initialize_semantic_search(self):
        """Embed each transaction for fuzzy retrieval."""
        try:
            if self.financial_data is None or len(self.financial_data) == 0:
                return
            documents = []
            for idx, row in self.financial_data.iterrows():
                content = (
                    f"Transaction: {row.get('Name/Description', 'N/A')} | "
                    f"Category: {row.get('Category', 'N/A')} | "
                    f"Amount: ${abs(row.get('Amount', 0)):.2f} | "
                    f"Type: {row.get('Expense/Income', 'N/A')} | "
                    f"Date: {row.get('Date', 'N/A')}"
                )
                documents.append(Document(page_content=content, metadata={'index': idx}))
            self.vector_store = InMemoryVectorStore(embedding=self._make_embeddings())
            self.vector_store.add_documents(documents)
        except Exception as e:
            print(f"Semantic search initialization failed: {e}")
            self.use_semantic_search = False
