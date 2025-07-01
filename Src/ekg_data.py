import numpy as np
from Src.find_peaks import find_peaks_custom
import plotly.graph_objects as go

class Ekg_tests:
    def __init__(self, id, date, result_link, max_length=None, sampling_rate=100):
        self.id = id
        self.date = date
        self.result_link = result_link
        self.max_length = max_length
        self.sampling_rate = sampling_rate
        self.signal = self.load_signal()
        self.peaks = []
        self.hr = []


    def load_signal(self):
        try:
            with open(self.result_link, "r") as file:
                data = []
                for line in file:
                    if line.strip():
                        parts = line.strip().split()  # Trennung z. B. bei Tab
                        try:
                            value = float(parts[0])    # Nur erste Spalte (Signalwert)
                            data.append(value)
                        except ValueError:
                            continue  # Ungültige Zeile überspringen

            if self.max_length is not None and len(data) > self.max_length:
                data = data[:self.max_length]
                print(f"⚠️ Signal gekürzt auf {self.max_length} Werte")

            print(f"📦 {self.result_link}: {len(data)} Werte geladen")
            return data

        except Exception as e:
            print(f"❌ Fehler beim Laden von {self.result_link}: {e}")
            return []


    def find_peaks(self, threshold=360):
        from Src.find_peaks import find_peaks_custom
        self.peaks = find_peaks_custom(self.signal, threshold=threshold)



    def estimate_hr(self):
        hr = []
        if not hasattr(self, 'sampling_rate'):
            self.sampling_rate = 100  # Fallback-Wert

        for i in range(len(self.peaks) - 1):
            t1 = self.peaks[i]
            t2 = self.peaks[i + 1]
            time_diff_sec = (t2 - t1) / self.sampling_rate

            if time_diff_sec > 0:
                bpm = 60 / time_diff_sec
                hr.append(bpm)

        self.hr = hr
        return self.hr


    def plot_time_series(self):
        """Plottet das vollständige Signal mit Peak-Markierung."""
        x_axis = [i / self.sampling_rate for i in range(len(self.signal))]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=self.signal,
            mode="lines",
            name="EKG-Signal"
        ))

        if self.peaks:
            fig.add_trace(go.Scatter(
                x=[i / self.sampling_rate for i in self.peaks],
                y=[self.signal[i] for i in self.peaks],
                mode="markers",
                marker=dict(color="red", size=6),
                name="Peaks"
            ))

        fig.update_layout(
            title="EKG-Zeitreihe",
            xaxis_title="Zeit (s)",
            yaxis_title="Amplitude",
            height=400
        )
        return fig
    
