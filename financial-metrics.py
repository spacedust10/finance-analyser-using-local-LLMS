import pandas as pd

class FinancialAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def financial_analysis(self):
        key_figures = {}
        yearly_income = self.data.loc[self.data['Expense/Income'] == 'Income'].groupby('Year')['Amount()'].sum().mean()
        yearly_expenses = self.data.loc[self.data['Expense/Income'] == 'Expense'].groupby('Year')['Amount()'].sum().mean()
        
        savings_yearly = yearly_income - yearly_expenses
        savings_rate_yearly = (savings_yearly / yearly_income) * 100 if yearly_income > 0 else 0
        
        top_expenses = self.data.loc[self.data['Expense/Income'] == 'Expense'].groupby('Category')['Amount()'].sum().sort_values(ascending=False)
        
        monthly_income = self.data.loc[self.data['Expense/Income'] == 'Income'].groupby(self.data['Date'].dt.to_period('M'))['Amount()'].sum().mean()
        monthly_expenses = self.data.loc[self.data['Expense/Income'] == 'Expense'].groupby(self.data['Date'].dt.to_period('M'))['Amount()'].sum().mean()
        
        savings_monthly = yearly_income - yearly_expenses
        savings_rate_monthly = (savings_monthly / yearly_income) * 100 if monthly_income > 0 else 0