# Changelog

## 1.0.0 — 2026-07-12

Complete rebuild of the analyzer as "The Private Ledger".

### Added
- Layered architecture: `services/` (file, classification, analysis, chat, ollama, documents), `ui/` (pages + components), `config/`, `core/`, `utils/`
- Robust CSV ingestion: US/EU amount formats, mixed-case types, invalid-row dropping with persistent warnings
- Local-LLM transaction classification with position-mapped parsing and merchant-knowledge prompting
- Analysis engine: totals, monthly cash flow, month-over-month change, top merchants, subscription detection (weekly/monthly/quarterly/yearly cadences), 3-month linear forecast with confidence band
- RAG assistant: financial snapshot injection, semantic + keyword transaction retrieval, reference-document RAG with `[filename, part N]` citations, query routing (personal / web / general), analyst-style prompting, on-demand analyst brief
- Document ingestion: PDF/TXT/MD chunking with overlap, embedded locally
- Ollama model picker — any installed model drives chat, classification and briefs; dedicated embedding model auto-selected
- Live web search via ddgs (opt-in; privacy mode default)
- Dual light/dark theme with instant client-side sync and theme-aware Plotly charts (11 curated charts)
- 40-test offline suite (`python3 test_core.py`), mutation-checked

### Removed
- Monolithic `file_processor.py` / `finance_dashboard.py` / `transaction_classifier.py` / `financial_metrics.py`
- Low-insight charts (pies, gauge, radar, violin, sunburst, box, heatmap)
