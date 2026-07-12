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

    def index_documents(self, chunks: list) -> int:
        """Add pre-chunked reference documents ({'text','source','chunk'}) to
        the document vector store. Returns number of chunks indexed."""
        docs = [
            Document(page_content=c["text"],
                     metadata={"source": c["source"], "chunk": c["chunk"]})
            for c in chunks
        ]
        if self.document_store is None:
            self.document_store = InMemoryVectorStore(embedding=self._make_embeddings())
        self.document_store.add_documents(docs)
        for c in chunks:
            if c["source"] not in self.document_names:
                self.document_names.append(c["source"])
        return len(docs)

    def clear_documents(self):
        self.document_store = None
        self.document_names = []

    # ── analysis snapshot ────────────────────────────────────────────────

    def _analyze_financial_data(self):
        """Compute the summary snapshot injected into every data prompt."""
        try:
            df = self.financial_data
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            analysis = {'total_transactions': len(df)}
            if 'Date' in df.columns:
                analysis['date_range'] = {
                    'start': df['Date'].min().strftime('%Y-%m-%d') if pd.notna(df['Date'].min()) else 'Unknown',
                    'end': df['Date'].max().strftime('%Y-%m-%d') if pd.notna(df['Date'].max()) else 'Unknown'
                }

            income_df = df[df['Expense/Income'] == 'Income']
            expense_df = df[df['Expense/Income'] == 'Expense']
            analysis['income'] = {'total': float(income_df['Amount'].sum()), 'transactions': len(income_df)}
            analysis['expenses'] = {'total': float(expense_df['Amount'].sum()), 'transactions': len(expense_df)}

            total_income = analysis['income']['total']
            total_expenses = analysis['expenses']['total']
            analysis['savings'] = {
                'total': total_income - total_expenses,
                'rate': ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
            }

            if len(expense_df) > 0 and 'Category' in expense_df.columns:
                analysis['top_expense_categories'] = (
                    expense_df.groupby('Category')['Amount'].sum()
                    .sort_values(ascending=False).head(5).to_dict()
                )
            return analysis
        except Exception as e:
            print(f"Error analyzing financial data: {e}")
            return {}

    def _format_financial_summary(self) -> str:
        if not self.financial_analysis:
            return "No financial data available."
        a = self.financial_analysis
        summary = (
            f"FINANCIAL SNAPSHOT\n"
            f"Period: {a.get('date_range', {}).get('start', 'N/A')} to {a.get('date_range', {}).get('end', 'N/A')}\n"
            f"Transactions: {a.get('total_transactions', 0)}\n"
            f"Income: ${a.get('income', {}).get('total', 0):,.2f} ({a.get('income', {}).get('transactions', 0)} transactions)\n"
            f"Expenses: ${a.get('expenses', {}).get('total', 0):,.2f} ({a.get('expenses', {}).get('transactions', 0)} transactions)\n"
            f"Net savings: ${a.get('savings', {}).get('total', 0):,.2f} (rate {a.get('savings', {}).get('rate', 0):.1f}%)\n"
        )
        if 'top_expense_categories' in a:
            summary += "Top expense categories:\n"
            for cat, amt in a['top_expense_categories'].items():
                summary += f"- {cat}: ${amt:,.2f}\n"
        return summary

    # ── retrieval ────────────────────────────────────────────────────────
