import pandas as pd
from fredapi import Fred
import plotly.graph_objects as go

# -------------------------------------------------------
# Enter your FRED API key here:
FRED_API_KEY = "YOUR_FRED_API_KEY"
# https://fred.stlouisfed.org/docs/api/api_key.html
# -------------------------------------------------------

## pip install fredapi pandas plotly
## chatgpt:
#    can you plot: Headline CPI Core CPI Core PCE Dallas Fed Trimmed mean PCE since 2016
#    lets try interactive plotly chart
# 

fred = Fred(api_key=FRED_API_KEY)

series = {
    "Headline CPI": "CPIAUCSL",
    "Core CPI": "CPILFESL",
    "Core PCE": "PCEPILFE",
    "Dallas Fed Trimmed Mean PCE": "PCETRIM12M159SFRBDAL",
}

start = "2015-01-01"   # start early so YoY begins in 2016

data = pd.DataFrame()

for name, code in series.items():
    s = fred.get_series(code)
    s.name = name
    data = pd.concat([data, s], axis=1)

# Calculate year-over-year inflation
yoy = data.pct_change(12) * 100
yoy = yoy.loc["2016-01-01":]

fig = go.Figure()

colors = {
    "Headline CPI": "#1f77b4",
    "Core CPI": "#d62728",
    "Core PCE": "#2ca02c",
    "Dallas Fed Trimmed Mean PCE": "#9467bd",
}

for col in yoy.columns:
    fig.add_trace(
        go.Scatter(
            x=yoy.index,
            y=yoy[col],
            mode="lines",
            name=col,
            line=dict(width=2.5, color=colors[col]),
            hovertemplate="%{x|%b %Y}<br>%{y:.2f}%<extra></extra>",
        )
    )

fig.update_layout(
    title="U.S. Inflation Measures (Year-over-Year)",
    template="plotly_white",
    hovermode="x unified",
    height=650,
    width=1100,
    legend=dict(
        orientation="h",
        y=1.08,
        x=0,
    ),
    xaxis_title="",
    yaxis_title="Percent",
)

fig.update_yaxes(ticksuffix="%", zeroline=True)

fig.show()