# The Private Ledger — Finance Analyzer using Local LLMs

Your finances, analyzed where they live — on your machine. Upload a bank-statement
CSV and get a Rocket-Money-style dashboard, subscription detection, spending
forecasts, and an AI analyst you can chat with — all powered by local Ollama
models. Nothing leaves your computer unless you explicitly enable web search.

## Features

- **Dashboard** — monthly cash flow (income up / spending down / net line),
  income-to-savings waterfall, money-flow sankey, category treemap and trends,
  month-over-month change, savings-rate tracking against the 20% guideline
- **Recurring charges** — Rocket-Money-style subscription detection
  (weekly / monthly / quarterly / yearly cadences) with annualized cost
- **Forecast** — 3-month spending projection with an 80% confidence band
- **AI assistant** — RAG chat over your transactions with analyst-style,
  evidence-cited answers; on-demand analyst brief (grade + strength / risk / action)
- **Documents** — attach 10-K filings, receipts, or reports (PDF/TXT/MD);
  chunked and embedded locally, cited as `[filename, part N]` in answers
- **Model picker** — use any Ollama model you have installed; a dedicated
  embedding model (e.g. `nomic-embed-text`) is auto-selected when present
- **Smart classification** — the LLM's merchant knowledge categorizes
  transactions deterministically, with graceful fallback when Ollama is off
- **Dual themes** — light and dark, with charts that re-theme instantly
- **Robust CSV cleaning** — US (`$1,234.56`) and EU (`1 234,56`) amount formats,
  mixed-case types, invalid rows dropped and reported

## Setup

```bash
# 1. Install Ollama and pull at least one model
ollama pull llama3.2            # chat + classification
ollama pull nomic-embed-text    # embeddings (optional, recommended)

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

CSV format (see `sample_transactions.csv`):

```csv
Date,Name/Description,Expense/Income,Amount
2024-01-05,Acme Corp Payroll,Income,2900.00
2024-01-06,Netflix.com,Expense,13.99
```

## Architecture

```
.
├── app.py                      # shell: nav, theme sync, routing
├── rag_finance_chat.py         # RAG engine: retrieval, routing, prompts, verdict
├── visualization.py            # 11 theme-aware Plotly charts
├── test_core.py                # 40-test offline suite
├── sample_transactions.csv     # synthetic 7-year test dataset
├── services/
│   ├── file_service.py         # CSV read + clean (amounts, dates, types)
│   ├── classification_service.py  # LLM categorization, position-mapped parsing
│   ├── analysis_service.py     # totals, cash flow, recurring, forecast
│   ├── ollama_service.py       # local model discovery
│   ├── document_service.py     # PDF/TXT extraction + chunking
│   └── chat_service.py         # wrapper around the RAG engine
├── ui/
│   ├── pages/                  # dashboard, assistant, documents
│   └── components/             # sidebar, metrics, chat
├── config/
│   ├── settings.py             # app, model and category config
│   └── styles.py               # design system (dual palettes, theme sync)
├── core/
│   └── models.py               # session state dataclass
├── utils/
│   └── state_manager.py        # session state + chat-service factory
└── .streamlit/config.toml      # light/dark theme definitions
```

## Tests

```bash
python3 test_core.py    # 40 offline tests, no Ollama needed
```

## Privacy

All analysis, classification, embeddings, and chat run against your local
Ollama instance. The only network calls are the optional web search toggle
(ddgs) and Google Fonts. Note: Ollama "cloud" models (e.g. `*-cloud`) proxy to
ollama.com — pick a fully local model if that matters to you.
