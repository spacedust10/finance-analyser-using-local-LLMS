import streamlit as st
import pandas as pd

from config.styles import AppStyles
from services.analysis_service import FinancialAnalysisService, detect_recurring, forecast_monthly
from ui.components.chat import escape_dollars
from ui.components.metrics import MetricsDisplay
from utils.state_manager import StateManager
from visualization import FinanceVisualizer

def _chart(fig, key: str):
    if fig:
        st.plotly_chart(fig, use_container_width=True, key=key)

class DashboardPage:
    """Curated dashboard: overview, categories, recurring, forecast"""

    def __init__(self, analysis_service: FinancialAnalysisService):
        self.analysis_service = analysis_service

    def render(self, theme: str = "dark"):
        df = StateManager.get_data()
        if df is None:
            st.markdown(
                AppStyles.empty_state(
                    "An empty ledger",
                    "Upload a CSV of transactions in the sidebar — everything is analyzed on this machine."
                ),
                unsafe_allow_html=True,
            )
            return

        MetricsDisplay.render(df, theme)
        self._render_analyst_brief(df)

        viz = FinanceVisualizer(df, theme)
        overview, categories, recurring, forecast = st.tabs(
            ["Overview", "Categories", "Recurring", "Forecast"]
        )
        with overview:
            self._render_overview(viz)
        with categories:
            self._render_categories(df, viz)
        with recurring:
            self._render_recurring(df, viz)
        with forecast:
            self._render_forecast(df, viz)

    def _render_analyst_brief(self, df: pd.DataFrame):
        """LLM verdict on financial health — generated on demand, cached per data+model."""
        cache_key = f"verdict_{len(df)}_{StateManager.get_model()}"
        with st.expander("Analyst brief — local AI verdict"):
            if st.button("Generate brief", key="gen_brief"):
                if st.session_state.rag_chat is None:
                    st.session_state.rag_chat = StateManager.build_chat_service(df)
                with st.spinner("The analyst is reading your ledger..."):
                    st.session_state[cache_key] = st.session_state.rag_chat.analyst_verdict()
            if cache_key in st.session_state:
                st.markdown(escape_dollars(st.session_state[cache_key]))

    def _render_overview(self, viz: FinanceVisualizer):
        _chart(viz.cash_flow(), "cash_flow")
        col1, col2 = st.columns(2)
        with col1:
            _chart(viz.waterfall(), "waterfall")
        with col2:
            _chart(viz.savings_rate_trend(), "savings_rate")
        _chart(viz.sankey(), "sankey")
