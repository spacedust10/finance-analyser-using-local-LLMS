import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from services.analysis_service import (
    detect_recurring, forecast_monthly, month_over_month_change,
    monthly_cash_flow, top_merchants,
)

# The Private Ledger palettes — mirror config/styles.py
PALETTES = {
    "dark": dict(
        paper="#F4EFE6", muted="#8A948C", emerald="#4FCE8B", mint="#7ADFA9",
        amber="#E0A458", rose="#E2606B", grid="rgba(244,239,230,0.08)",
        band="rgba(224,164,88,0.18)",
    ),
    "light": dict(
        paper="#1C231F", muted="#6B746D", emerald="#1F9D5B", mint="#177A46",
        amber="#B97F2A", rose="#C43D49", grid="rgba(28,35,31,0.10)",
        band="rgba(185,127,42,0.16)",
    ),
}

for _kind, _c in PALETTES.items():
    pio.templates[f"ledger_{_kind}"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="IBM Plex Sans, sans-serif", color=_c["paper"]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=[_c["emerald"], _c["amber"], "#5B8DB8", _c["rose"], _c["mint"], "#8E7CC3"],
            xaxis=dict(gridcolor=_c["grid"], zerolinecolor=_c["grid"]),
            yaxis=dict(gridcolor=_c["grid"], zerolinecolor=_c["grid"]),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=60, r=20, b=40, l=50),
        )
    )

class FinanceVisualizer:
    """Curated, theme-aware chart set for the dashboard."""

    def __init__(self, df: pd.DataFrame, theme: str = "dark"):
        self.df = df.copy()
        self.theme = theme if theme in PALETTES else "dark"
        self.c = PALETTES[self.theme]
        self.template = f"ledger_{self.theme}"

    def _fig(self, title: str, height: int = 420) -> go.Figure:
        fig = go.Figure()
        fig.update_layout(template=self.template, title=title, height=height)
        return fig

    def cash_flow(self):
        """Income up, spending down, net as a line — one chart tells the month's story."""
        monthly = monthly_cash_flow(self.df)
        if monthly.empty:
            return None
        fig = self._fig("Cash flow by month", height=440)
        fig.add_bar(x=monthly['YearMonth'], y=monthly['Income'], name='Income',
                    marker_color=self.c["emerald"])
        fig.add_bar(x=monthly['YearMonth'], y=-monthly['Expense'], name='Spending',
                    marker_color=self.c["amber"])
        fig.add_scatter(x=monthly['YearMonth'], y=monthly['Net'], name='Net',
                        mode='lines+markers', line=dict(color=self.c["paper"], width=2))
        fig.update_layout(barmode='relative', yaxis_title="Amount ($)", hovermode='x unified')
        return fig

    def waterfall(self):
        """Where the income went: top categories down to net savings."""
        income = self.df[self.df['Expense/Income'] == 'Income']['Amount'].sum()
        spend = self.df[self.df['Expense/Income'] == 'Expense']
        if spend.empty or 'Category' not in spend.columns:
            return None
        top = spend.groupby('Category')['Amount'].sum().nlargest(6)
        other = spend['Amount'].sum() - top.sum()

        labels = ['Income'] + list(top.index) + ['Other', 'Net savings']
        measures = ['absolute'] + ['relative'] * (len(top) + 1) + ['total']
        values = [income] + [-v for v in top.values] + [-other, 0]

        fig = self._fig("Where the income went", height=480)
        fig.add_trace(go.Waterfall(
            orientation="v", measure=measures, x=labels, y=values,
            text=[f"${abs(v):,.0f}" for v in values[:-1]] + [""],
            textposition="outside",
            connector={"line": {"color": self.c["grid"]}},
            decreasing={"marker": {"color": self.c["amber"]}},
            increasing={"marker": {"color": self.c["emerald"]}},
            totals={"marker": {"color": self.c["mint"]}},
        ))
        fig.update_layout(showlegend=False, yaxis_title="Amount ($)")
        return fig
