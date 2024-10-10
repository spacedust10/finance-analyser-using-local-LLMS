import pandas as pd

class FinancialAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def financial_analysis(self):
        key_figures = {}
        yearly_income = self.data.loc[self.data['Expense/Income'] == 'Income'].groupby('Year')['Amount()'].sum().mean()
        yearly_expenses = self.data.loc[self.data['Expense/Income'] == 'Expense'].groupby('Year')['Amount()'].sum().mean()
        
        top_expenses = self.data.loc[self.data['Expense/Income'] == 'Expense'].groupby('Category')['Amount()'].sum().sort_values(ascending=False)