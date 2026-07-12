import streamlit as st
import pandas as pd
from config.styles import AppStyles
from services.analysis_service import monthly_cash_flow, totals

def _mom_delta(cash: pd.DataFrame, col: str) -> str:
    """'+$123 vs last mo' for the most recent complete pair of months."""
    if len(cash) < 2:
        return ""
    change = cash[col].iloc[-1] - cash[col].iloc[-2]
    sign = "+" if change >= 0 else "−"
    return f"{sign}${abs(change):,.0f} vs last mo"

class MetricsDisplay:
    """Component for displaying financial metrics"""

    @staticmethod
    def render(df: pd.DataFrame, theme: str = "dark"):
        """Render ledger metric cards with month-over-month deltas"""
        c = AppStyles.palette(theme)
        income, expenses, savings, rate = totals(df)
        cash = monthly_cash_flow(df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                AppStyles.metric_card("Total Income", f"${income:,.0f}",
                                      c["emerald"], _mom_delta(cash, 'Income')),
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                AppStyles.metric_card("Total Expenses", f"${expenses:,.0f}",
                                      c["amber"], _mom_delta(cash, 'Expense')),
                unsafe_allow_html=True
            )
        with col3:
            accent = c["mint"] if savings >= 0 else c["rose"]
            st.markdown(
                AppStyles.metric_card("Net Savings", f"${savings:,.0f}",
                                      accent, _mom_delta(cash, 'Net')),
                unsafe_allow_html=True
            )
        with col4:
            accent = c["mint"] if rate >= 20 else c["amber"]
            st.markdown(
                AppStyles.metric_card("Savings Rate", f"{rate:.1f}%", accent),
                unsafe_allow_html=True
            )
