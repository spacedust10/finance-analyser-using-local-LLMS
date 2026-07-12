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
