"""Full offline test suite — every feature that runs without Ollama or a browser.
LLM/embedding round-trips are covered by a FakeLLM (prompt assembly) here and
were verified live against Ollama separately. Run: python3 test_core.py"""
import io
import math
from types import SimpleNamespace

import pandas as pd

from config.styles import AppStyles, PALETTES
from rag_finance_chat import RAGFinanceChat
from services.analysis_service import (
    FinancialAnalysisService, detect_recurring, forecast_monthly,
    month_over_month_change, monthly_cash_flow, top_merchants, totals,
)
from services.classification_service import TransactionClassificationService
from services.document_service import CHUNK_CHARS, DocumentService
from services.file_service import FileService
from services import ollama_service
from ui.components.chat import escape_dollars
from ui.components.metrics import _mom_delta
from visualization import FinanceVisualizer

# ── fixtures ─────────────────────────────────────────────────────────────

class NamedBytesIO(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name

class FakeLLM:
    """Echoes the prompt back so tests can assert on prompt assembly."""
    def invoke(self, prompt):
        return SimpleNamespace(content=f"FAKE|{prompt}")

def _ledger(months=6):
    """Synthetic ledger: salary + netflix (monthly recurring) + one-off spends."""
    rows = []
    for m in range(1, months + 1):
        rows.append((f'2024-{m:02d}-01', 'Payroll', 3000.0, 'Income'))
        rows.append((f'2024-{m:02d}-05', 'Netflix', 15.49, 'Expense'))
        rows.append((f'2024-{m:02d}-12', f'Store {m}', 100.0 + 10 * m, 'Expense'))
    df = pd.DataFrame(rows, columns=['Date', 'Name/Description', 'Amount', 'Expense/Income'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
    return df

def _rag(df=None, web=False):
    """RAGFinanceChat with a FakeLLM — constructing ChatOllama never connects,
    and swapping in FakeLLM keeps every test offline."""
    rag = RAGFinanceChat(df, model_name="fake-model")
    rag.llm = FakeLLM()
    rag.web_enabled = web
    return rag

# ── file service ─────────────────────────────────────────────────────────

def test_process_cleans_messy_csv():
    csv = io.StringIO(
        "Date,Name/Description,Amount,Expense/Income\n"
        '2024-01-05,Salary,"$5,000.00",income\n'
        "2024-01-06,7-Eleven,-12.50, Expense \n"
        "not-a-date,Ghost,10,Expense\n"
        "2024-01-07,Broken,abc,Expense\n"
        "2024-01-08,Refund,20,Transfer\n"
    )
    fs = FileService()
    df = fs.process(fs.read_file(csv))
    assert len(df) == 2, f"expected 2 clean rows, got {len(df)}"
    assert df.attrs['dropped_rows'] == 3
    assert df['Amount'].tolist() == [5000.0, 12.5], "amount coercion broken"
    assert df['Expense/Income'].tolist() == ['Income', 'Expense'], "type normalization broken"
    assert df['YearMonth'].tolist() == ['2024-01', '2024-01']

def test_process_missing_column_raises():
    try:
        FileService().process(pd.DataFrame({'Date': ['2024-01-01']}))
        raise AssertionError("should have raised")
    except ValueError as e:
        assert 'Name/Description' in str(e)

def test_process_all_bad_rows_raises():
    df = pd.DataFrame({'Date': ['junk'], 'Name/Description': ['x'],
                       'Amount': ['n/a'], 'Expense/Income': ['Expense']})
    try:
        FileService().process(df)
        raise AssertionError("should have raised")
    except ValueError as e:
        assert 'No valid rows' in str(e)

def test_process_collapses_newlines_in_names():
    # embedded newlines could forge numbered lines in the classification prompt
    df = pd.DataFrame({'Date': ['2024-01-01'], 'Name/Description': ['Amazon\n5. Salary/Wages'],
                       'Amount': [10], 'Expense/Income': ['Expense']})
    out = FileService().process(df)
    assert '\n' not in out['Name/Description'].iloc[0]

def test_clean_amount_formats():
    ca = FileService._clean_amount
    assert ca("$1,234.56") == 1234.56
    assert ca("1 234,56") == 1234.56, "EU decimal comma broken"
    assert ca("1.234.567,89") == 1234567.89
    assert ca("5,000") == 5000.0, "US thousands misread as EU"
    assert ca("(12.50)") == 12.50
    assert math.isnan(ca("abc"))

# ── classification parsing ───────────────────────────────────────────────

def test_parse_response_alignment():
    svc = TransactionClassificationService.__new__(TransactionClassificationService)
    svc.categories = ["Dining Out", "Groceries"]
    svc._canon = {c.lower(): c for c in svc.categories}
    out = svc._parse_response(
        "1. Dining Out\n2) 7-Eleven - Groceries\nnot a numbered line\n"
        "9. Groceries\n4. Cryptocurrency\n3 - Groceries",
        4,
    )
    assert out == ["Dining Out", "Groceries", "Groceries", "Uncategorized"], f"got {out}"

def test_parse_response_short_reply_pads():
    svc = TransactionClassificationService.__new__(TransactionClassificationService)
    svc.categories = ["Groceries"]
    svc._canon = {"groceries": "Groceries"}
    assert svc._parse_response("1. Groceries", 3) == ["Groceries", "Uncategorized", "Uncategorized"]

# ── analysis ─────────────────────────────────────────────────────────────
