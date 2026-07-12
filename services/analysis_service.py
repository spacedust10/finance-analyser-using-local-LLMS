import numpy as np
import pandas as pd

CADENCE_PER_YEAR = {'Weekly': 52, 'Monthly': 12, 'Quarterly': 4, 'Yearly': 1}
CADENCE_GAP_DAYS = {'Weekly': (5, 9), 'Monthly': (24, 38), 'Quarterly': (80, 100), 'Yearly': (330, 395)}

def totals(df: pd.DataFrame) -> tuple:
    """(income, expenses, savings, savings_rate_pct) — the one place this math lives"""
    income = float(df.loc[df['Expense/Income'] == 'Income', 'Amount'].sum())
    expenses = float(df.loc[df['Expense/Income'] == 'Expense', 'Amount'].sum())
    savings = income - expenses
    rate = savings / income * 100 if income > 0 else 0.0
    return income, expenses, savings, rate

def monthly_cash_flow(df: pd.DataFrame) -> pd.DataFrame:
    """Per-month Income, Expense, Net — the backbone of the overview charts."""
    monthly = df.groupby(['YearMonth', 'Expense/Income'])['Amount'].sum().unstack(fill_value=0)
    for col in ('Income', 'Expense'):
        if col not in monthly.columns:
            monthly[col] = 0.0
    monthly['Net'] = monthly['Income'] - monthly['Expense']
    return monthly.reset_index().sort_values('YearMonth')
