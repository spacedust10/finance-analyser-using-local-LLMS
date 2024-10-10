import plotly.express as px

class FinanceVisualizer:
    def __init__(self, df, year):
        self.df = df
        self.year = year

        self.income_vs_expense_bar_chart = self.make_income_vs_expense_bar_chart()
        self.saving_rate_trend = self.make_saving_rate_trend()
        self.category_wise_spend_bar_chart = self.make_category_wise_spend_bar_chart()
        self.income_pie_chart = self.make_pie_chart('Income')
        self.expense_pie_chart = self.make_pie_chart('Expense')
        self.monthly_income_bar_chart = self.make_monthly_bar_chart('Income')
        self.monthly_expense_bar_chart = self.make_monthly_bar_chart('Expense')

    def make_pie_chart(self, label):
        sub_df = self.df[(self.df['Expense/Income'] == label) & (self.df['Year'] == self.year)]
        color_scale = px.colors.qualitative.Set2
        
        pie_fig = px.pie(sub_df, values='Amount', names='Category', color_discrete_sequence=color_scale)
        pie_fig.update_traces(textposition='inside', direction='clockwise', hole=0.3, textinfo="label+percent")
        
        total_expense = self.df[(self.df['Expense/Income'] == 'Expense') & (self.df['Year'] == self.year)]['Amount'].sum() 
        total_income = self.df[(self.df['Expense/Income'] == 'Income') & (self.df['Year'] == self.year)]['Amount'].sum()
        
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
            title=dict(text=label + " Breakdown " + str(self.year) + saving_rate_text),
            annotations=[dict(text=total_text, x=0.5, y=0.5, font_size=12, showarrow=False)]
        )
        return pie_fig

    def make_monthly_bar_chart(self, label):
        df_filtered = self.df[(self.df['Expense/Income'] == label) & (self.df['Year'] == self.year)]
        total_by_month = (df_filtered.groupby(['Month', 'Month Name'])['Amount']
                            .sum()
                            .to_frame()
                            .reset_index()
                            .sort_values(by='Month')
                            .reset_index(drop=True))
        if label == "Income":
            color_scale = px.colors.sequential.YlGn
        else:
            color_scale = px.colors.sequential.OrRd
        
        bar_fig = px.bar(total_by_month, x='Month Name', y='Amount', text_auto='.2s', 
                            title=label + " per month", color='Amount', color_continuous_scale=color_scale)
        return bar_fig

    def make_income_vs_expense_bar_chart(self):
        total_by_month = self.df.groupby(['Month', 'Month Name', 'Expense/Income'])['Amount'].sum().unstack().fillna(0)
        bar_fig = px.bar(total_by_month.reset_index(), x='Month Name', y=total_by_month.columns,
                        title='Income vs Expense Over Time', 
                        labels={'value': 'Amount', 'Month Name': 'Month'},
                        color_discrete_sequence=px.colors.qualitative.Set1)
        bar_fig.update_layout(barmode='group')
        return bar_fig

    def make_saving_rate_trend(self):
        self.df['Saving Rate'] = (self.df['Income'] - self.df['Expense']) / self.df['Income'] * 100
        saving_rate_trend = self.df.groupby('Year')['Saving Rate'].mean().reset_index()
        
        line_fig = px.line(saving_rate_trend, x='Year', y='Saving Rate', 
                            title='Saving Rate Trend', labels={'Saving Rate': 'Saving Rate (%)'})
        return line_fig

    def make_category_wise_spend_bar_chart(self):
        category_spend = self.df[self.df['Expense/Income'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index()
        bar_fig = px.bar(category_spend, x='Category', y='Amount', 
                        title='Category Wise Spending', 
                        labels={'Amount': 'Total Spending', 'Category': 'Expense Category'})
        return bar_fig