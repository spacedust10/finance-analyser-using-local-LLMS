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
        
        key_figures['Average Annual Income'] = f"${yearly_income:,.2f}"
        key_figures['Average Annual Expenses'] = f"${yearly_expenses:,.2f}"
        key_figures['Annual Savings Rate'] = f"{savings_rate_yearly:.2f}%"
        key_figures['Annual Savings Rate'] = f"{savings_rate_monthly:.2f}%"
        key_figures['Top Expense Categories'] = {category: f"${amount:,.2f}" for category, amount in top_expenses.head().items()}
        key_figures['Average Monthly Income'] = f"${monthly_income:,.2f}"
        key_figures['Average Monthly Expenses'] = f"${monthly_expenses:,.2f}"
        return key_figures