import pandas as pd

def analyze_hr_data(max_hr):
     # HR in Tabelle
    PATH = "data/activity.csv"
    df = pd.read_csv(PATH)
    df

    hr_zones = {}
    counter = 1
    for percent in range(50,100,10):
        print(percent/100)
        hr_zones["Zone"+str(counter)] = max_hr * (percent/100)
        counter += 1
    hr_zones

    current_zone = []

    for index, row in df.iterrows():
        #print(row["HeartRate"])
        current_hr = row["HeartRate"]

        if current_hr > hr_zones["Zone5"]:
            current_zone.append("Zone 5")
        elif current_hr > hr_zones["Zone4"]:
            current_zone.append("Zone 4")
        elif current_hr > hr_zones["Zone3"]:
            current_zone.append("Zone 3")
        elif current_hr > hr_zones["Zone2"]:
            current_zone.append("Zone 2")
        else:
            current_zone.append("Zone 1")

    current_zone

    df["Zone"] = current_zone
    df["Zone"].value_counts()

    df_zone5 = df.groupby("Zone").mean()
    df_zone5

    df["Time"] = df.index
    from plotly import express as px
    fig = px.line(df, x="Time", y="HeartRate")
    fig.update_layout(
        title="Heart Rate over Time by Zone",
        xaxis_title="Time",
        yaxis_title="Heart Rate (bpm)")

    #fig.add_shape(type="rect", y0=0, y1 = 120, fillcolor="green", opacity=0.2)
    fig.add_shape(type="rect", x0=0, x1=len(df), y0=80, y1=hr_zones["Zone2"], fillcolor="green", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=len(df), y0=hr_zones["Zone2"], y1=hr_zones["Zone3"], fillcolor="blue", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=len(df), y0=hr_zones["Zone3"], y1=hr_zones["Zone4"], fillcolor="orange", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=len(df), y0=hr_zones["Zone4"], y1=hr_zones["Zone5"], fillcolor="red", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=len(df), y0=hr_zones["Zone5"], y1=max_hr, fillcolor="purple", opacity=0.2, line_width=0)

    # Value Counts (Anzahl der Werte pro Zone)
    zone_counts = df["Zone"].value_counts().sort_index()

    # Durchschnittlicher Puls pro Zone
    zone_avg_hr = df.groupby("Zone")["HeartRate"].mean()

    # Umrechnung: Sekunden zu Minuten:Sekunden als String
    dauer_formatiert = [
        f"{int(sek // 60)}:{int(sek % 60):02d}" for sek in zone_counts.values
    ]

    # Neuer DataFrame
    df_zonen_statistik = pd.DataFrame({
        "Zone": zone_counts.index,
        "Zeit [Min:Sek]": dauer_formatiert,
        "Durchschnitt_HR [bpm]": zone_avg_hr.values
    }).reset_index(drop=True)

    # Ausgabe ohne Index
    return fig, df_zonen_statistik
