import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from visualization import FinanceVisualizer
from financial_metrics import FinancialAnalyzer

class FinanceDashboard:
    def __init__(self, df):
        """Initialize with already processed data (categorized_df)."""
        self.df = df
        self.analysis_results = self.analyze_data()

    def analyze_data(self):
        """Performs financial analysis on the categorized data."""
        analyzer = FinancialAnalyzer(self.df)
        return analyzer.financial_analysis()

    def display_analysis_results(self):
        """Displays the analysis results in the dashboard."""
        st.markdown("## Yearly Figures")
        avg_income = f"**Average Annual Income:** {self.analysis_results['Average Annual Income']}"
        avg_expenses = f"**Average Annual Expenses:** {self.analysis_results['Average Annual Expenses']}"
        savings_rate = f"**Savings Rate:** {self.analysis_results['Annual Savings Rate Yearly']}"
        
        st.markdown(f"#### {avg_income}")
        st.markdown(f"#### {avg_expenses}")
        st.markdown(f"#### {savings_rate}")
        
        st.markdown("## Average Monthly Figures")
        avg_monthly_income = f"**Average Monthly Income:** {self.analysis_results['Average Monthly Income']}"
        avg_monthly_expenses = f"**Average Monthly Expenses:** {self.analysis_results['Average Monthly Expenses']}"
        monthly_savings_rate = f"**Monthly Savings Rate:** {self.analysis_results['Annual Savings Rate Monthly']}"
        
        st.markdown(f"#### {avg_monthly_income}")
        st.markdown(f"#### {avg_monthly_expenses}")
        st.markdown(f"#### {monthly_savings_rate}")
        
        top_expense_categories = self.analysis_results['Top Expense Categories']
        df = pd.DataFrame(list(top_expense_categories.items()), columns=['Category', 'Amount'])
        
        fig_table = go.Figure(data=[go.Table(
            header=dict(values=['Category', 'Amount']),
            cells=dict(values=[df['Category'], df['Amount']]))
        ])
        
        st.plotly_chart(fig_table)

    def create_dashboard(self):
        """Displays the graph results in the dashboard."""
        charts = FinanceVisualizer(self.df)

        unique_years = self.df['Year'].unique()

        income_tabs = []
        expense_tabs = []

        for year in unique_years:
            income_pie = charts.make_pie_chart(year, "Income")
            income_bar = charts.make_monthly_bar_chart(year, "Income")
            
            income_tabs.append((f'Income Breakdown for {year}', income_pie))
            income_tabs.append((f'Monthly Income for {year}', income_bar))
            
            expense_pie = charts.make_pie_chart(year, "Expense")
            expense_bar = charts.make_monthly_bar_chart(year, "Expense")
            expense_tabs.append((f'Expense Breakdown for {year}', expense_pie))
            expense_tabs.append((f'Monthly Expense for {year}', expense_bar))

        for title, chart in income_tabs:
            st.markdown(f"### {title}")
            st.plotly_chart(chart)

        for title, chart in expense_tabs:
            st.markdown(f"### {title}")
            st.plotly_chart(chart)

        income_vs_expense = charts.make_income_vs_expense_bar_chart()
        st.plotly_chart(income_vs_expense)

        savings_rate = charts.make_saving_rate_trend()
        st.plotly_chart(savings_rate)

        category_wise_spend = charts.make_category_wise_spend_bar_chart()
        st.plotly_chart(category_wise_spend)