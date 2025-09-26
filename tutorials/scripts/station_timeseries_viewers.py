# filename: station_timeseries_viewers.py
"""
Interactive time-series viewers for water stations with gap handling.

DataFrame requirements:
    columns = ['locatiecode','datum','fewsparameternaam','meetwaarde','eenheid']

Exports:
    - create_viewer_one_param_two_stations(df, max_gap_days=180)
    - create_viewer_two_params_two_stations(df, max_gap_days=365)

Usage (in a notebook/Colab):
    from station_timeseries_viewers import (
        create_viewer_one_param_two_stations,
        create_viewer_two_params_two_stations,
    )

    viewer1 = create_viewer_one_param_two_stations(df, max_gap_days=180)
    display(viewer1)

    viewer2 = create_viewer_two_params_two_stations(df, max_gap_days=365)
    display(viewer2)
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import Dropdown, VBox, HBox, Output, Layout


# ---------- Shared utilities ----------
def _coerce_df(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure datetime and numeric types; return a copy."""
    df = df.copy()
    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
    df['meetwaarde'] = pd.to_numeric(df['meetwaarde'], errors='coerce')
    return df


def _break_gaps(d: pd.DataFrame, max_gap_days: int) -> pd.DataFrame:
    """Insert NaN at the first sample after a large gap to break plot lines."""
    if d.empty:
        return d.assign(meetwaarde_line=pd.Series(dtype=float))
    d = d.sort_values('datum').copy()
    gaps = d['datum'].diff() > pd.Timedelta(days=max_gap_days)
    d['meetwaarde_line'] = d['meetwaarde']
    d.loc[gaps, 'meetwaarde_line'] = np.nan
    return d


def _pad_ylim(vals: pd.Series, axis):
    """Set y-limits with a small padding based on available values."""
    v = vals.replace([np.inf, -np.inf], np.nan).dropna()
    if v.empty:
        axis.set_ylim(0.0, 1.0)
        return
    vmin, vmax = v.min(), v.max()
    pad = 0.05 * (vmax - vmin if vmax > vmin else (abs(vmax) + 1.0))
    axis.set_ylim(vmin - pad, vmax + pad)


def _xlimits_from(*date_series: pd.Series):
    """Compute global x-limits from multiple datetime Series."""
    all_dates = pd.concat([s for s in date_series if s is not None], ignore_index=True).dropna()
    if all_dates.empty:
        return pd.Timestamp('1970-01-01'), pd.Timestamp('1970-01-02')
    return all_dates.min(), all_dates.max()


def _unit_of(d: pd.DataFrame) -> str:
    """Get first non-null unit string or empty."""
    return d['eenheid'].dropna().iloc[0] if (not d.empty and d['eenheid'].notna().any()) else ''


# ---------- Viewer A: One parameter across two stations ----------
def create_viewer_one_param_two_stations(df: pd.DataFrame, max_gap_days: int = 180):
    """
    Interactive viewer: select one parameter and compare two stations (same y-axis if units match).
    Returns a VBox widget you can display().
    """
    df = _coerce_df(df)

    station_options = sorted(df['locatiecode'].dropna().unique().tolist())
    param_options   = sorted(df['fewsparameternaam'].dropna().unique().tolist())

    station1_dd = Dropdown(options=station_options, description='Station 1:', layout=Layout(width='50%'))
    station2_dd = Dropdown(options=station_options, description='Station 2:', layout=Layout(width='50%'))
    param_dd    = Dropdown(options=param_options,   description='Parameter:', layout=Layout(width='50%'))

    out = Output(layout=Layout(border='1px solid #ddd'))

    def _plot(st1, st2, param):
        d1 = df[(df['locatiecode'] == st1) & (df['fewsparameternaam'] == param)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])
        d2 = df[(df['locatiecode'] == st2) & (df['fewsparameternaam'] == param)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])

        d1 = _break_gaps(d1, max_gap_days)
        d2 = _break_gaps(d2, max_gap_days)

        unit1, unit2 = _unit_of(d1), _unit_of(d2)

        with out:
            out.clear_output(wait=True)
            if d1.empty and d2.empty:
                print(f'No data for "{param}" at "{st1}" or "{st2}".')
                return

            fig, ax = plt.subplots(figsize=(12, 5))

            # Global x-limits
            xmin, xmax = _xlimits_from(d1['datum'], d2['datum'])
            ax.set_xlim(xmin, xmax)

            # Plot series
            if not d1.empty:
                ax.plot(d1['datum'], d1['meetwaarde_line'], linestyle='-', label=f'{st1} ({unit1})' if unit1 else f'{st1}', color='blue')
                ax.plot(d1['datum'], d1['meetwaarde'], marker='o', linestyle='None', color='cyan')

            if not d2.empty:
                ax.plot(d2['datum'], d2['meetwaarde_line'], linestyle='-', label=f'{st2} ({unit2})' if unit2 else f'{st2}', color='green')
                ax.plot(d2['datum'], d2['meetwaarde'], marker='s', linestyle='None', color='red')

            # Y-axis padding
            all_vals = pd.concat([d1['meetwaarde'], d2['meetwaarde']], ignore_index=True) if (not d1.empty or not d2.empty) else pd.Series(dtype=float)
            _pad_ylim(all_vals, ax)

            ylabel = f'Value ({unit1})' if unit1 and (unit1 == unit2) else 'Value'
            ax.set_title(f'{param} — time series')
            ax.set_xlabel('Date'); ax.set_ylabel(ylabel)
            ax.legend(); ax.grid(True, alpha=0.3)
            fig.tight_layout()
            plt.show()

            if unit1 and unit2 and unit1 != unit2:
                print(f'Note: units differ: {st1}={unit1}, {st2}={unit2}')

    def _on_change(_):
        _plot(station1_dd.value, station2_dd.value, param_dd.value)

    # Init
    if station_options and param_options:
        station1_dd.value = station_options[0]
        station2_dd.value = station_options[1] if len(station_options) > 1 else station_options[0]
        param_dd.value    = param_options[0]
        _plot(station1_dd.value, station2_dd.value, param_dd.value)

    station1_dd.observe(_on_change, names='value')
    station2_dd.observe(_on_change, names='value')
    param_dd.observe(_on_change, names='value')

    return VBox([HBox([station1_dd, station2_dd]), param_dd, out])


# ---------- Viewer B: Two stations, potentially different parameters ----------
def create_viewer_two_params_two_stations(df: pd.DataFrame, max_gap_days: int = 365):
    """
    Interactive viewer: select two stations and (optionally different) parameters.
    Uses dual y-axes when params/units differ and both series exist.
    Returns a VBox widget you can display().
    """
    df = _coerce_df(df)

    station_options = sorted(df['locatiecode'].dropna().unique().tolist())
    param_options   = sorted(df['fewsparameternaam'].dropna().unique().tolist())

    station1_dd = Dropdown(options=station_options, description='Station 1:', layout=Layout(width='45%'))
    station2_dd = Dropdown(options=station_options, description='Station 2:', layout=Layout(width='45%'))
    param1_dd   = Dropdown(options=param_options,   description='Param 1:',   layout=Layout(width='45%'))
    param2_dd   = Dropdown(options=param_options,   description='Param 2:',   layout=Layout(width='45%'))

    out = Output(layout=Layout(border='1px solid #ddd'))

    def _plot(st1, p1, st2, p2):
        d1 = df[(df['locatiecode']==st1) & (df['fewsparameternaam']==p1)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])
        d2 = df[(df['locatiecode']==st2) & (df['fewsparameternaam']==p2)][['datum','meetwaarde','eenheid']].dropna(subset=['datum'])

        d1 = _break_gaps(d1, max_gap_days)
        d2 = _break_gaps(d2, max_gap_days)

        unit1, unit2 = _unit_of(d1), _unit_of(d2)
        use_dual = (p1 != p2 or unit1 != unit2) and (not d1.empty and not d2.empty)

        with out:
            out.clear_output(wait=True)
            if d1.empty and d2.empty:
                print('No data for the selected combinations.')
                return

            fig, ax = plt.subplots(figsize=(12, 5))
            ax2 = ax.twinx() if use_dual else None

            # X limits
            xmin, xmax = _xlimits_from(d1['datum'], d2['datum'])
            ax.set_xlim(xmin, xmax)

            # First series on left axis
            if not d1.empty:
                ax.plot(d1['datum'], d1['meetwaarde_line'], linestyle='-', label=f'{st1} — {p1}', color = 'blue')
                ax.plot(d1['datum'], d1['meetwaarde'], marker='o', linestyle='None', color = 'cyan')
                _pad_ylim(d1['meetwaarde'], ax)
                ax.set_ylabel(f'{p1}' + (f' ({unit1})' if unit1 else ''))

            # Second series on right (or left if single axis)
            if not d2.empty:
                target_ax = ax2 if use_dual else ax
                target_ax.plot(d2['datum'], d2['meetwaarde_line'], linestyle='-', label=f'{st2} — {p2}', color = 'green')
                target_ax.plot(d2['datum'], d2['meetwaarde'], marker='s', linestyle='None', color = 'red')
                _pad_ylim(d2['meetwaarde'], target_ax)
                if use_dual:
                    target_ax.set_ylabel(f'{p2}' + (f' ({unit2})' if unit2 else ''))

            # Legend
            handles, labels = ax.get_legend_handles_labels()
            if use_dual and ax2 is not None:
                h2, l2 = ax2.get_legend_handles_labels()
                handles += h2; labels += l2
            if handles:
                ax.legend(handles, labels, loc='best')

            ax.set_title('Time series')
            ax.set_xlabel('Date')
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            plt.show()

    def _on_change(_):
        _plot(station1_dd.value, param1_dd.value, station2_dd.value, param2_dd.value)

    # Init
    if station_options and param_options:
        station1_dd.value = station_options[0]
        station2_dd.value = station_options[1] if len(station_options) > 1 else station_options[0]
        param1_dd.value   = param_options[0]
        param2_dd.value   = param_options[min(1, len(param_options)-1)]
        _plot(station1_dd.value, param1_dd.value, station2_dd.value, param2_dd.value)

    for w in (station1_dd, station2_dd, param1_dd, param2_dd):
        w.observe(_on_change, names='value')

    return VBox([HBox([station1_dd, station2_dd]), HBox([param1_dd, param2_dd]), out])
