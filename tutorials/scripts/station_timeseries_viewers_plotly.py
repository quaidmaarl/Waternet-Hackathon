# filename: station_timeseries_viewers_plotly.py
"""
Plotly time-series viewers for water stations with gap handling.

DataFrame requirements:
    columns = ['locatiecode','datum','fewsparameternaam','meetwaarde','eenheid']

Exports (Figure-returning):
    - make_plotly_timeseries(df, station1, station2, param, max_gap_days=180)
    - make_plotly_timeseries_two_params(df, station1, param1, station2, param2, max_gap_days=365)

Optional (ipywidgets viewers for notebooks):
    - create_plotly_viewer_one_param_two_stations(df, max_gap_days=180)
    - create_plotly_viewer_two_params_two_stations(df, max_gap_days=365)
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------- Shared utilities ----------
def _coerce_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df['meetwaarde'] = pd.to_numeric(df['meetwaarde'], errors='coerce')
    return df

def _break_gaps(d: pd.DataFrame, max_gap_days: int) -> pd.DataFrame:
    """Insert NaNs after large time gaps so Plotly breaks the line."""
    if d.empty:
        return d.assign(meetwaarde_line=pd.Series(dtype=float))
    d = d.sort_values('datum').copy()
    d['meetwaarde'] = pd.to_numeric(d['meetwaarde'], errors='coerce')
    gaps = d['datum'].diff() > pd.Timedelta(days=max_gap_days)
    d['meetwaarde_line'] = d['meetwaarde']
    d.loc[gaps, 'meetwaarde_line'] = np.nan
    return d

def _unit_of(d: pd.DataFrame) -> str:
    return d['eenheid'].dropna().iloc[0] if (not d.empty and d['eenheid'].notna().any()) else ''

def _x_range_from(*date_series: pd.Series):
    all_dates = pd.concat([s for s in date_series if s is not None], ignore_index=True).dropna()
    return [all_dates.min(), all_dates.max()] if not all_dates.empty else None

# ---------- Figure-returning APIs ----------
def make_plotly_timeseries(
    df: pd.DataFrame,
    station1: str,
    station2: str,
    param: str,
    max_gap_days: int = 180
) -> go.Figure:
    """
    Two stations, one parameter (single y-axis if units match).
    Example:
        fig = make_plotly_timeseries(df, 'BOT001', 'AMS002', 'Zuurgraad', 180)
        fig.show()
    """
    dfx = _coerce_df(df)
    d1 = dfx[(dfx['locatiecode'] == station1) & (dfx['fewsparameternaam'] == param)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])
    d2 = dfx[(dfx['locatiecode'] == station2) & (dfx['fewsparameternaam'] == param)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])

    d1 = _break_gaps(d1, max_gap_days)
    d2 = _break_gaps(d2, max_gap_days)

    unit1, unit2 = _unit_of(d1), _unit_of(d2)
    same_units = (unit1 == unit2) or (not unit1 and not unit2)
    y_label = f"Value ({unit1})" if same_units and unit1 else "Value"

    fig = go.Figure()
    c1, c2 = '#1f77b4', '#d62728'  # Plotly tab10 blue/red

    if not d1.empty:
        fig.add_trace(go.Scatter(
            x=d1['datum'], y=d1['meetwaarde_line'],
            mode='lines+markers',
            name=f'{station1}',
            line=dict(width=2, color=c1),
            marker=dict(symbol='circle', size=6, color=c1),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                f"Station: {station1}<br>"
                f"Param: {param}<br>"
                "Value: %{y:.4g}" + (f" {unit1}" if unit1 else "") + "<extra></extra>"
            )
        ))

    if not d2.empty:
        fig.add_trace(go.Scatter(
            x=d2['datum'], y=d2['meetwaarde_line'],
            mode='lines+markers',
            name=f'{station2}',
            line=dict(width=2, color=c2),  # solid line to match your Matplotlib viewer
            marker=dict(symbol='circle', size=6, color=c2),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                f"Station: {station2}<br>"
                f"Param: {param}<br>"
                "Value: %{y:.4g}" + (f" {unit2}" if unit2 else "") + "<extra></extra>"
            )
        ))

    x_range = _x_range_from(d1['datum'] if not d1.empty else None,
                            d2['datum'] if not d2.empty else None)

    fig.update_layout(
        title=f'{param} — time series',
        xaxis=dict(
            title='Date',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            range=x_range
        ),
        yaxis=dict(title=y_label),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        margin=dict(l=60, r=20, t=60, b=60),
        template='plotly_white'
    )

    if unit1 and unit2 and unit1 != unit2:
        fig.add_annotation(text=f"Note: units differ — {station1}: {unit1}, {station2}: {unit2}",
                           xref='paper', yref='paper', x=0, y=1.08,
                           showarrow=False, font=dict(size=11, color='crimson'))

    return fig


def make_plotly_timeseries_two_params(
    df: pd.DataFrame,
    station1: str, param1: str,
    station2: str, param2: str,
    max_gap_days: int = 365
) -> go.Figure:
    """
    Two stations with (possibly) different parameters.
    Uses secondary y-axis when params/units differ and both series exist.
    Example:
        fig = make_plotly_timeseries_two_params(df, 'BOT001','Zuurgraad', 'AMS002','Temperatuur', 365)
        fig.show()
    """
    dfx = _coerce_df(df)
    d1 = dfx[(dfx['locatiecode'] == station1) & (dfx['fewsparameternaam'] == param1)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])
    d2 = dfx[(dfx['locatiecode'] == station2) & (dfx['fewsparameternaam'] == param2)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])

    d1 = _break_gaps(d1, max_gap_days)
    d2 = _break_gaps(d2, max_gap_days)

    unit1, unit2 = _unit_of(d1), _unit_of(d2)
    use_dual = (param1 != param2 or unit1 != unit2) and (not d1.empty and not d2.empty)

    fig = go.Figure()
    c1, c2 = '#1f77b4', '#d62728'

    # Left axis
    if not d1.empty:
        fig.add_trace(go.Scatter(
            x=d1['datum'], y=d1['meetwaarde_line'],
            mode='lines+markers',
            name=f'{station1} — {param1}',
            line=dict(width=2, color=c1),
            marker=dict(symbol='circle', size=6, color=c1),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                f"Station: {station1}<br>"
                f"Param: {param1}<br>"
                "Value: %{y:.4g}" + (f" {unit1}" if unit1 else "") + "<extra></extra>"
            ),
            yaxis='y'  # primary
        ))

    # Right axis (or left if same scale)
    if not d2.empty:
        fig.add_trace(go.Scatter(
            x=d2['datum'], y=d2['meetwaarde_line'],
            mode='lines+markers',
            name=f'{station2} — {param2}',
            line=dict(width=2, color=c2),
            marker=dict(symbol='circle', size=6, color=c2),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                f"Station: {station2}<br>"
                f"Param: {param2}<br>"
                "Value: %{y:.4g}" + (f" {unit2}" if unit2 else "") + "<extra></extra>"
            ),
            yaxis='y2' if use_dual else 'y'
        ))

    x_range = _x_range_from(d1['datum'] if not d1.empty else None,
                            d2['datum'] if not d2.empty else None)

    layout = dict(
        title='Time series',
        xaxis=dict(
            title='Date',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            range=x_range
        ),
        yaxis=dict(title=f'{param1}' + (f' ({unit1})' if unit1 else '')),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        margin=dict(l=60, r=60 if use_dual else 20, t=60, b=60),
        template='plotly_white'
    )

    if use_dual:
        # Secondary y-axis on the right
        layout['yaxis2'] = dict(
            title=f'{param2}' + (f' ({unit2})' if unit2 else ''),
            overlaying='y',
            side='right',
            showgrid=False
        )

    fig.update_layout(**layout)
    return fig

# ---------- Optional ipywidgets viewers (not required for plain Figure use) ----------
try:
    from ipywidgets import Dropdown, VBox, HBox, Output, Layout
    from IPython.display import display

    def create_plotly_viewer_one_param_two_stations(df: pd.DataFrame, max_gap_days: int = 180):
        dfx = _coerce_df(df)
        station_options = sorted(dfx['locatiecode'].dropna().unique().tolist())
        param_options   = sorted(dfx['fewsparameternaam'].dropna().unique().tolist())

        st1 = Dropdown(options=station_options, description='Station 1:', layout=Layout(width='45%'))
        st2 = Dropdown(options=station_options, description='Station 2:', layout=Layout(width='45%'))
        pa  = Dropdown(options=param_options,   description='Parameter:', layout=Layout(width='45%'))

        out = Output(layout=Layout(border='1px solid #ddd'))

        def _draw(*_):
            with out:
                out.clear_output(wait=True)
                fig = make_plotly_timeseries(dfx, st1.value, st2.value, pa.value, max_gap_days=max_gap_days)
                fig.show()

        # init
        if station_options and param_options:
            st1.value = station_options[0]
            st2.value = station_options[1] if len(station_options) > 1 else station_options[0]
            pa.value  = param_options[0]
            _draw()

        for w in (st1, st2, pa):
            w.observe(_draw, names='value')

        return VBox([HBox([st1, st2]), pa, out])

    def create_plotly_viewer_two_params_two_stations(df: pd.DataFrame, max_gap_days: int = 365):
        dfx = _coerce_df(df)
        station_options = sorted(dfx['locatiecode'].dropna().unique().tolist())
        param_options   = sorted(dfx['fewsparameternaam'].dropna().unique().tolist())

        st1 = Dropdown(options=station_options, description='Station 1:', layout=Layout(width='45%'))
        st2 = Dropdown(options=station_options, description='Station 2:', layout=Layout(width='45%'))
        p1  = Dropdown(options=param_options,   description='Param 1:',   layout=Layout(width='45%'))
        p2  = Dropdown(options=param_options,   description='Param 2:',   layout=Layout(width='45%'))

        out = Output(layout=Layout(border='1px solid #ddd'))

        def _draw(*_):
            with out:
                out.clear_output(wait=True)
                fig = make_plotly_timeseries_two_params(dfx, st1.value, p1.value, st2.value, p2.value, max_gap_days=max_gap_days)
                fig.show()

        # init
        if station_options and param_options:
            st1.value = station_options[0]
            st2.value = station_options[1] if len(station_options) > 1 else station_options[0]
            p1.value  = param_options[0]
            p2.value  = param_options[min(1, len(param_options)-1)]
            _draw()

        for w in (st1, st2, p1, p2):
            w.observe(_draw, names='value')

        return VBox([HBox([st1, st2]), HBox([p1, p2]), out])

except Exception:
    # ipywidgets not available; figure-returning functions still work
    pass
