import plotly.express as px
import pandas as pd

class FinanceVisualizer:
    def __init__(self, df):
        self.df = df

    def make_pie_chart(self, year, label):
        sub_df = self.df[(self.df['Expense/Income'] == label) & (self.df['Year'] == year)]
        color_scale = px.colors.qualitative.Set2
        
        pie_fig = px.pie(sub_df, values='Amount', names='Category', color_discrete_sequence=color_scale)
        pie_fig.update_traces(textposition='inside', direction='clockwise', hole=0.3, textinfo="label+percent")
        
        total_expense = self.df[(self.df['Expense/Income'] == 'Expense') & (self.df['Year'] == year)]['Amount'].sum() 
        total_income = self.df[(self.df['Expense/Income'] == 'Income') & (self.df['Year'] == year)]['Amount'].sum()
        
        if label == 'Expense':
            total_text = "$ " + str(round(total_expense))
            saving_rate = round((total_income - total_expense) / total_income * 100)
            saving_rate_text = ": Saving rate " + str(saving_rate) + "%"
        else:
            saving_rate_text = ""
            total_text = "$ " + str(round(total_income))

        pie_fig.update_layout(
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            title=dict(text=label + " Breakdown " + str(year) + saving_rate_text),
            annotations=[dict(text=total_text, x=0.5, y=0.5, font_size=12, showarrow=False)]
        )
        return pie_fig

    def make_monthly_bar_chart(self, year, label):
        df = self.df[(self.df['Expense/Income'] == label) & (self.df['Year'] == year)]
        total_by_month = (df.groupby([df['Date'].dt.to_period('M')])['Amount'].sum()
                            .to_frame()
                            .reset_index()
                            .sort_values(by='Date')
                            .reset_index(drop=True))
        
        total_by_month['Month Name'] = total_by_month['Date'].dt.strftime('%B %Y')
        
        if label == "Income":
            color_scale = px.colors.sequential.YlGn
        else:
            color_scale = px.colors.sequential.OrRd
        
        bar_fig = px.bar(total_by_month, x='Month Name', y='Amount', text_auto='.2s', title=label + " per month", color='Amount', color_continuous_scale=color_scale)
        return bar_fig

    def make_income_vs_expense_bar_chart(self):
        total_by_month = self.df.groupby([self.df['Date'].dt.to_period('M'), 'Expense/Income'])['Amount'].sum().unstack().fillna(0)
        bar_fig = px.bar(total_by_month.reset_index(), x=total_by_month.index.to_series().dt.strftime('%B %Y'), y=total_by_month.columns,
                            title='Income vs Expense Over Time', 
                            labels={'value': 'Amount', 'Month Name': 'Month'},
                            color_discrete_sequence=px.colors.qualitative.Set1)
        bar_fig.update_layout(barmode='group')
        return bar_fig

    def make_saving_rate_trend(self):
        income_per_year = self.df[self.df['Expense/Income'] == 'Income'].groupby(self.df['Date'].dt.year)['Amount'].sum()
        expense_per_year = self.df[self.df['Expense/Income'] == 'Expense'].groupby(self.df['Date'].dt.year)['Amount'].sum()

        saving_rate_df = pd.DataFrame({'Income': income_per_year, 'Expense': expense_per_year})
        saving_rate_df['Saving Rate'] = (saving_rate_df['Income'] - saving_rate_df['Expense']) / saving_rate_df['Income'] * 100

        saving_rate_df = saving_rate_df.reset_index()

        line_fig = px.line(saving_rate_df, x='Date', y='Saving Rate', 
                            title='Saving Rate Trend', 
                            labels={'Saving Rate': 'Saving Rate (%)', 'Date': 'Year'})
        return line_fig

    def make_category_wise_spend_bar_chart(self):
        category_spend = self.df[self.df['Expense/Income'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index()
        bar_fig = px.bar(category_spend, x='Category', y='Amount', 
                        title='Category Wise Spending', 
                        labels={'Amount': 'Total Spending', 'Category': 'Expense Category'})
        return bar_fig