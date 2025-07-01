
import pandas as pd
import numpy as np
import plotly.graph_objs as go
   
df_power = pd.read_csv("data/activity.csv", sep=",")

#array aus df_power["PowerOriginal"]
power_array = np.array(df_power["PowerOriginal"])
import matplotlib.pyplot as plt

plt.plot(power_array)
plt.title("Power over Time")
plt.xlabel("Time")
plt.ylabel("Power (W)")
plt.show()


def power_curve_2(power_array=None):
    clean_arr = power_array[~np.isnan(power_array)]
    max_power = np.max(clean_arr)
        
    # Leistungsschwellen definieren (z. B. 100 bis 600 W in 10-W-Schritten)
    thresholds = np.arange(0, max_power, 10)
    times_over_threshold = []

    # Für jede Schwelle: wie viele Sekunden lag power_array drüber?
    for t in thresholds:
        duration = np.sum(power_array > t)
        times_over_threshold.append(duration)

    # CSV einlesen
    df_power = pd.read_csv("data/activity.csv", sep=",")
    power_array = np.array(df_power["PowerOriginal"])


    #Zeit zwischen Messungen aus Duration spalte ziehen
    time_zw_mp = df_power["Duration"][1]
    #time_zw_mp = 2

    df_threshold = pd.DataFrame({
        'Power (W)': thresholds,
        'Time over Threshold (s)': times_over_threshold
        
    })

    df_threshold.iloc[:, 1] = df_threshold.iloc[:, 1]*time_zw_mp
    df_threshold

    import plotly.graph_objs as go

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_threshold["Time over Threshold (s)"],
        y=df_threshold["Power (W)"],
        mode='lines+markers',
        name='Time over Threshold'
    ))

    fig.update_layout(
        title='Zeit über Leistungsschwelle',
        xaxis_title='Zeit (s)',
        yaxis_title='Leistung (W)',
        hovermode='x unified'
    )

    fig.show()
    return df_threshold

power_curve_2(power_array)