import plotly.express as px

def make_pie_chart(df, year, label):
    sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    color_scale = px.colors.qualitative.Set2
    
    pie_fig = px.pie(sub_df, values='Amount (EUR)', names='Category', color_discrete_sequence=color_scale)
    pie_fig.update_traces(textposition='inside', direction='clockwise', hole=0.3, textinfo="label+percent")
    
    total_expense = df[(df['Expense/Income'] == 'Expense') & (df['Year'] == year)]['Amount'].sum() 
    total_income = df[(df['Expense/Income'] == 'Income') & (df['Year'] == year)]['Amount'].sum()
    
    if label == 'Expense':
        total_text = "€ " + str(round(total_expense))
        saving_rate = round((total_income - total_expense) / total_income * 100)
        saving_rate_text = ": Saving rate " + str(saving_rate) + "%"
    else:
        saving_rate_text = ""
        total_text = "€ " + str(round(total_income))

    pie_fig.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        title=dict(text=label + " Breakdown " + str(year) + saving_rate_text),
        annotations=[dict(text=total_text, x=0.5, y=0.5, font_size=12, showarrow=False)]
    )
    return pie_fig

def make_monthly_bar_chart(df, year, label):
    df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    total_by_month = (df.groupby(['Month', 'Month Name'])['Amount']
                        .sum()
                        .to_frame()
                        .reset_index()
                        .sort_values(by='Month')
                        .reset_index(drop=True))
    if label == "Income":
        color_scale = px.colors.sequential.YlGn
    else:
        color_scale = px.colors.sequential.OrRd
    
    bar_fig = px.bar(total_by_month, x='Month Name', y='Amount', text_auto='.2s', title=label + " per month", color='Amount', color_continuous_scale=color_scale)
    return bar_fig