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

    def _render_categories(self, df: pd.DataFrame, viz: FinanceVisualizer):
        col1, col2 = st.columns(2)
        with col1:
            _chart(viz.treemap(), "treemap")
        with col2:
            _chart(viz.category_bar(), "category_bar")
        _chart(viz.category_trends(), "category_trends")
        _chart(viz.mom_change(), "mom_change")

        breakdown = self.analysis_service.get_category_breakdown(df)
        if not breakdown.empty:
            st.markdown("#### Category breakdown")
            st.dataframe(breakdown, use_container_width=True)

    def _render_recurring(self, df: pd.DataFrame, viz: FinanceVisualizer):
        recurring = detect_recurring(df)
        if recurring.empty:
            st.info("No recurring charges detected — needs 3+ steady charges "
                    "from the same merchant at a regular cadence.")
            _chart(viz.top_merchants_bar(), "top_merchants")
            return

        annualized = recurring['Annualized'].sum()
        st.markdown(
            AppStyles.metric_card("Recurring spend, annualized",
                                  f"${annualized:,.0f}/yr",
                                  "var(--rose)",
                                  f"{len(recurring)} active subscriptions"),
            unsafe_allow_html=True,
        )
        _chart(viz.recurring_bar(recurring), "recurring_bar")
        st.dataframe(recurring, use_container_width=True, hide_index=True)
        _chart(viz.top_merchants_bar(), "top_merchants")

    def _render_forecast(self, df: pd.DataFrame, viz: FinanceVisualizer):
        forecast = forecast_monthly(df)
        if forecast.empty:
            st.info("Forecast needs at least 3 months of data.")
            return

        next_expense = forecast['Expense_forecast'].dropna().iloc[1]
        next_net = forecast['Net_forecast'].dropna().iloc[1]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                AppStyles.metric_card("Projected spending, next month",
                                      f"${next_expense:,.0f}", "var(--amber)"),
                unsafe_allow_html=True,
            )
        with col2:
            accent = "var(--mint)" if next_net >= 0 else "var(--rose)"
            st.markdown(
                AppStyles.metric_card("Projected net, next month",
                                      f"${next_net:,.0f}", accent),
                unsafe_allow_html=True,
            )
        _chart(viz.forecast(), "forecast")
        st.caption("Linear trend over your monthly history with an 80% confidence band — "
                   "a planning guide, not a guarantee.")

        monthly = self.analysis_service.get_monthly_summary(df)
        if not monthly.empty:
            st.markdown("#### Monthly summary")
            st.dataframe(monthly, use_container_width=True)
