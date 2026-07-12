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

def test_totals():
    df = pd.DataFrame({'Expense/Income': ['Income', 'Expense'], 'Amount': [200.0, 50.0]})
    assert totals(df) == (200.0, 50.0, 150.0, 75.0)

def test_totals_zero_income():
    df = pd.DataFrame({'Expense/Income': ['Expense'], 'Amount': [50.0]})
    assert totals(df) == (0.0, 50.0, -50.0, 0.0)

def test_monthly_summary_zero_income_month():
    df = pd.DataFrame({
        'YearMonth': ['2024-01', '2024-01', '2024-02'],
        'Expense/Income': ['Income', 'Expense', 'Expense'],
        'Amount': [100.0, 40.0, 10.0],
    })
    monthly = FinancialAnalysisService().get_monthly_summary(df)
    assert monthly.loc['2024-01', 'Savings_Rate'] == 60.0
    assert math.isnan(monthly.loc['2024-02', 'Savings_Rate']), "zero-income month must be NaN, not crash"

def test_cash_flow():
    cash = monthly_cash_flow(_ledger())
    assert len(cash) == 6
    assert cash['Net'].iloc[0] == 3000.0 - 15.49 - 110.0

def test_cash_flow_expense_only_data():
    df = _ledger()
    cash = monthly_cash_flow(df[df['Expense/Income'] == 'Expense'])
    assert (cash['Income'] == 0).all() and (cash['Net'] < 0).all()

def test_month_over_month_change():
    change = month_over_month_change(_ledger())
    assert len(change) == 5
    assert abs(change.iloc[0] - 10.0) < 1e-9, "store spend rises $10/month"

def test_top_merchants():
    top = top_merchants(_ledger(), n=3)
    assert len(top) == 3
    assert top['Total'].is_monotonic_decreasing

def test_recurring_monthly():
    rec = detect_recurring(_ledger())
    assert list(rec['Merchant']) == ['Netflix']
    assert rec['Cadence'].iloc[0] == 'Monthly'
    assert abs(rec['Annualized'].iloc[0] - 15.49 * 12) < 0.1

def test_recurring_cadences_and_rejections():
    def spend(dates, name, amounts):
        return pd.DataFrame({'Date': pd.to_datetime(dates), 'Name/Description': name,
                             'Amount': amounts, 'Expense/Income': 'Expense'})
    weekly = spend(pd.date_range('2024-01-01', periods=8, freq='7D'), 'Gym', [10.0] * 8)
    quarterly = spend(pd.date_range('2024-01-01', periods=4, freq='91D'), 'Water Bill', [90.0] * 4)
    yearly = spend(pd.date_range('2020-03-01', periods=4, freq='365D'), 'Insurance', [500.0] * 4)
    two_only = spend(['2024-01-01', '2024-02-01'], 'Rare', [9.0, 9.0])
    wobbly = spend(pd.date_range('2024-01-01', periods=5, freq='30D'), 'Random Shop',
                   [10.0, 200.0, 15.0, 300.0, 20.0])
    df = pd.concat([weekly, quarterly, yearly, two_only, wobbly])
    rec = detect_recurring(df)
    assert set(rec['Merchant']) == {'Gym', 'Water Bill', 'Insurance'}, f"got {rec}"
    assert dict(zip(rec['Merchant'], rec['Cadence'])) == {
        'Gym': 'Weekly', 'Water Bill': 'Quarterly', 'Insurance': 'Yearly'}

def test_forecast_shape():
    fc = forecast_monthly(_ledger(), months_ahead=3)
    assert len(fc) == 9
    assert math.isnan(fc['Expense'].iloc[-1])
    assert not math.isnan(fc['Expense_forecast'].iloc[-1])
    assert fc['Expense_lo'].iloc[-1] <= fc['Expense_forecast'].iloc[-1] <= fc['Expense_hi'].iloc[-1]
    assert fc['Expense_forecast'].iloc[-1] > fc['Expense'].dropna().iloc[0]

def test_forecast_needs_three_months():
    assert forecast_monthly(_ledger(months=2)).empty

# ── documents ────────────────────────────────────────────────────────────

def test_extract_text_txt():
    f = NamedBytesIO("hello ledger".encode(), "notes.txt")
    assert DocumentService().extract_text(f) == "hello ledger"

def test_extract_text_pdf():
    from pypdf import PdfWriter
    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(buf)
    text = DocumentService().extract_text(NamedBytesIO(buf.getvalue(), "filing.pdf"))
    assert text.startswith("[page 1]")

def test_chunker_overlap_and_citation():
    text = "\n\n".join(f"Paragraph {i} " + "x" * 300 for i in range(12))
    chunks = DocumentService().chunk(text, "10k.pdf")
    assert all(len(c["text"]) <= CHUNK_CHARS + 300 for c in chunks)
    assert chunks[0]["source"] == "10k.pdf" and chunks[0]["chunk"] == 1
    assert len(chunks) >= 3
    assert chunks[1]["text"][:50] in chunks[0]["text"], "overlap missing"

def test_chunker_short_text_single_chunk():
    chunks = DocumentService().chunk("just a receipt line", "r.txt")
    assert len(chunks) == 1 and chunks[0]["chunk"] == 1

# ── ollama service ───────────────────────────────────────────────────────

def test_chat_models_filters_embedders():
    models = ["llama3.1:latest", "nomic-embed-text:latest"]
    assert ollama_service.chat_models(models) == ["llama3.1:latest"]
    # all-embedding list falls back to everything rather than an empty picker
    assert ollama_service.chat_models(["nomic-embed-text:latest"]) == ["nomic-embed-text:latest"]

def test_pick_embed_model():
    assert ollama_service.pick_embed_model(
        ["llama3.1:latest", "nomic-embed-text:latest"], "fb") == "nomic-embed-text:latest"
    assert ollama_service.pick_embed_model(["llama3.1:latest"], "fb") == "fb"

def test_installed_models_unreachable_returns_empty():
    original = ollama_service.OLLAMA_URL
    ollama_service.OLLAMA_URL = "http://localhost:9"   # discard port, fails fast
    try:
        assert ollama_service.installed_models(timeout=0.5) == []
    finally:
        ollama_service.OLLAMA_URL = original

# ── RAG chat (FakeLLM, no Ollama) ────────────────────────────────────────

def test_query_routing():
    rag = _rag(_ledger(), web=True)
    assert rag._detect_query_type("how much did I spend on stores?") == 'personal_data'
    assert rag._detect_query_type("usd exchange rate today") == 'web_search'
    assert rag._detect_query_type("how do bonds work") == 'general_finance'
    rag.web_enabled = False
    assert rag._detect_query_type("usd exchange rate today") == 'general_finance', \
        "privacy mode must never route to the web"

def test_keyword_search_survives_regex_injection():
    rag = _rag(_ledger())
    out = rag._keyword_search_fallback("find (unclosed [paren Netflix")
    assert "Netflix" in out

def test_financial_summary_contents():
    summary = _rag(_ledger())._format_financial_summary()
    assert "18,000.00" in summary            # 6 months salary
    assert "Net savings" in summary

def test_chat_context_trims_and_excludes_current():
    rag = _rag()
    for i in range(10):
        rag.chat_history.append({"role": "user", "content": f"q{i}"})
        rag.chat_history.append({"role": "assistant", "content": f"a{i}"})
    rag.chat_history.append({"role": "user", "content": "CURRENT"})
    ctx = rag._get_chat_context()
    assert "CURRENT" not in ctx
    assert "q9" in ctx and "q0" not in ctx

def test_data_query_prompt_assembly():
    rag = _rag(_ledger())
    answer = rag.get_response("how much did I spend at Netflix?")
    assert answer.startswith("FAKE|")
    assert "FINANCIAL SNAPSHOT" in answer     # summary injected
    assert "Netflix" in answer                # retrieval found the merchant
    assert rag.chat_history[-1]["content"] == answer

def test_history_capped_at_20():
    rag = _rag(_ledger())
    for i in range(15):
        rag.get_response(f"question {i}")
    assert len(rag.chat_history) == 20

def test_analyst_verdict_uses_data():
    verdict = _rag(_ledger()).analyst_verdict()
    assert verdict.startswith("FAKE|") and "letter grade" in verdict

def test_no_data_query_asks_for_upload():
    rag = _rag()
    assert "upload" in rag._handle_data_query("what did I spend?").lower()

# ── UI helpers & theming ─────────────────────────────────────────────────

def test_escape_dollars():
    assert escape_dollars("save $100 and $200") == r"save \$100 and \$200"

def test_mom_delta():
    cash = pd.DataFrame({'Income': [100.0, 250.0]})
    assert _mom_delta(cash, 'Income') == "+$150 vs last mo"
    assert _mom_delta(cash.iloc[:1], 'Income') == ""

def test_css_carries_both_palettes():
    css = AppStyles.css("dark")
    assert PALETTES['dark']['card'] in css and PALETTES['light']['card'] in css
    assert 'data-ledger-theme="light"' in css
    assert '.st-key-theme_refresh' in css     # hidden rerun trigger stays hidden

def test_theme_sync_script_embeds_server_theme():
    assert 'SERVER_THEME = "light"' in AppStyles.theme_sync_script("light")

def test_components_html():
    card = AppStyles.metric_card("Income", "$5", "#fff", "+$1 vs last mo")
    assert "Income" in card and "+$1 vs last mo" in card
    chips = AppStyles.chips([("on-chip", True), ("off-chip", False)])
    assert 'ledger-chip on">on-chip' in chips and 'ledger-chip">off-chip' in chips
    assert "Empty" in AppStyles.empty_state("Empty", "body")

def test_all_charts_render_both_themes():
    df = _ledger(8)
    df['Category'] = df['Name/Description'].map(
        lambda n: 'Salary/Wages' if n == 'Payroll'
        else ('Subscriptions' if n == 'Netflix' else 'Shopping'))
    for theme in ('dark', 'light'):
        v = FinanceVisualizer(df, theme)
        figs = [v.cash_flow(), v.waterfall(), v.savings_rate_trend(), v.sankey(),
                v.treemap(), v.category_bar(), v.category_trends(), v.mom_change(),
                v.recurring_bar(detect_recurring(df)), v.top_merchants_bar(), v.forecast()]
        assert all(f is not None for f in figs), f"chart returned None in {theme}"

def test_charts_degrade_to_none_without_data():
    income_only = _ledger()[lambda d: d['Expense/Income'] == 'Income'].copy()
    income_only['Category'] = 'Salary/Wages'
    v = FinanceVisualizer(income_only, 'dark')
    assert v.treemap() is None and v.category_bar() is None and v.waterfall() is None
    assert v.recurring_bar(pd.DataFrame()) is None

if __name__ == "__main__":
    tests = [fn for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    for fn in tests:
        fn()
    print(f"ok — {len(tests)} tests")
