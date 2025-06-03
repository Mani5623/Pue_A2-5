# Datei: power_curve.py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"


def load_data(path: str) -> pd.Series:
    """
    Lädt Leistungsdaten aus einer CSV-Datei und gibt die Power-Spalte zurück.
    """
    df = pd.read_csv(path)
    if 'PowerOriginal' not in df.columns:
        raise ValueError("Die CSV-Datei muss eine Spalte 'PowerOriginal' enthalten.")
    return df['PowerOriginal']


def find_best_effort(power: pd.Series, duration: int) -> float:
    """
    Gibt die höchste durchschnittliche Leistung über ein Zeitfenster (Samples) zurück.
    """
    if duration > len(power):
        return np.nan
    return power.rolling(window=duration).mean().max()


def create_power_curve(power: pd.Series, durations: list[int]) -> pd.DataFrame:
    """
    Berechnet die Power Curve für eine Liste von Zeitdauern in Sekunden.
    Gibt ein DataFrame mit Spalten: 'duration_s', 'best_power_watt'
    """
    best_efforts = [find_best_effort(power, d) for d in durations]
    return pd.DataFrame({
        'duration_s': durations,
        'best_power_watt': best_efforts
    })


def plot_power_curve(df: pd.DataFrame):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['duration_s'],
        y=df['best_power_watt'],
        mode='lines+markers',
        name='Power Curve',
        fill='tozeroy'
    ))

    # Dauer in Sekunden → Tick-Werte und passende Labels definieren
    tickvals = [
        1, 2, 5, 10, 20, 30,
        60, 120, 300, 600, 1200, 1800,
    ]
    ticktext = [
        "1 sec", "2 sec", "5 sec", "10 sec", "20 sec", "30 sec",
        "1 min", "2 min", "5 min", "10 min", "20 min", "30 min",
    ]

    fig.update_layout(
        title="Power Curve",
        xaxis=dict(
            title="Interval Length",
            type='log',
            tickvals=tickvals,
            ticktext=ticktext
        ),
        yaxis=dict(title='Power (W)'),
        template='plotly_dark'
    )

    fig.show()


if __name__ == "__main__":
    # Daten laden
    power_series = load_data("data/activities/activity.csv")

    # Liste an Zeitintervallen in Sekunden – orientiert am Beispielbild
    durations = [
    5, 10, 15, 30, 60,
    120, 300, 600, 1200, 1800
    ]

    # Power Curve berechnen und plotten
    power_df = create_power_curve(power_series, durations)
    plot_power_curve(power_df)
