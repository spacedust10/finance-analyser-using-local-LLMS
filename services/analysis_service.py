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

def month_over_month_change(df: pd.DataFrame) -> pd.Series:
    """Dollar change in total spending vs the previous month."""
    spend = df[df['Expense/Income'] == 'Expense'].groupby('YearMonth')['Amount'].sum().sort_index()
    return spend.diff().dropna()

def top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    spend = df[df['Expense/Income'] == 'Expense']
    merchants = spend.groupby('Name/Description')['Amount'].agg(['sum', 'count'])
    merchants.columns = ['Total', 'Charges']
    return merchants.sort_values('Total', ascending=False).head(n)

def detect_recurring(df: pd.DataFrame) -> pd.DataFrame:
    """Rocket-Money-style subscription detection: a merchant is recurring when
    it has 3+ charges, a steady amount (CV < 0.35), and a regular gap that
    matches a known cadence."""
    spend = df[df['Expense/Income'] == 'Expense']
    rows = []
    for merchant, charges in spend.groupby('Name/Description'):
        if len(charges) < 3:
            continue
        charges = charges.sort_values('Date')
        median_gap = charges['Date'].diff().dt.days.dropna().median()
        mean_amount = charges['Amount'].mean()
        amount_cv = charges['Amount'].std() / mean_amount if mean_amount else 1.0
        cadence = next(
            (name for name, (lo, hi) in CADENCE_GAP_DAYS.items() if lo <= median_gap <= hi),
            None
        )
        if cadence and amount_cv < 0.35:
            rows.append({
                'Merchant': merchant,
                'Cadence': cadence,
                'Avg charge': round(mean_amount, 2),
                'Charges': len(charges),
                'Annualized': round(mean_amount * CADENCE_PER_YEAR[cadence], 2),
                'Last charge': charges['Date'].max().date(),
            })
    recurring = pd.DataFrame(rows)
    if recurring.empty:
        return recurring
    return recurring.sort_values('Annualized', ascending=False).reset_index(drop=True)
