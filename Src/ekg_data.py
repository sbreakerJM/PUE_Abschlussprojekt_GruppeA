import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
FILE_PATH = "data/person_db.json"

class Ekg_tests:
    def __init__(self, id: int, date: str, result_link: str):
        self.id = id
        self.date = date
        self.result_link = result_link
        self.load_df_ekg()
        

    def get_reslult_link(self):
        return self.result_link
    
    def load_df_ekg(self):
        self.df_ekg = pd.read_csv(self.result_link, sep = "\t", names=["Voltage in [mV]", "Time in [ms]"])
        #self.df_ekg = self.df_ekg.iloc[0:5000]

    def find_peaks(self, threshold = 340, min_peak_distance = 10):
        list_of_index_of_peaks = []
        last_peaks_index = 0
        for index, row in self.df_ekg.iterrows():
            if index < self.df_ekg.index.max() -1:
            #wenn row größer als das vorhegehende und das nachfolgende Element
            #dann füge den aktuellen Index der Liste hinzu
                if row["Voltage in [mV]"] >= self.df_ekg.iloc[index-1]["Voltage in [mV]"] and row["Voltage in [mV]"] > self.df_ekg.iloc[index+1]["Voltage in [mV]"]:
                    
                    if row["Voltage in [mV]"] > threshold and index - last_peaks_index > min_peak_distance:
                        list_of_index_of_peaks.append(index)
                        last_peaks_index = index
        self.list_of_index_of_peaks = list_of_index_of_peaks
        return list_of_index_of_peaks
    
    def estimate_hr(self):
        hr = []
        i = 0
        for peak in self.list_of_index_of_peaks:
            if i >= len(self.list_of_index_of_peaks) - 1:
                break
            else:
                time_hr = self.list_of_index_of_peaks[i+1] - self.list_of_index_of_peaks[i]
                time_hr = time_hr * 2
                puls = 60000 / time_hr
                hr.append(puls)
                i += 1

            #time_diff = self.df_ekg.iloc[peak]["Time in [ms]"] - self.df_ekg.iloc[list_of_index_of_peaks[0]]["Time in [ms]"]
            #hr = 60000 / time_diff
        self.hr = hr
        return self.hr
  
    def plot_time_series(self):
        
        # Y-Werte
        y_vals = pd.Series(self.hr).rolling(window=100).mean()

        x_vals = list(range(len(y_vals)))

        # Dynamische Y-Achsen-Grenzen
        y_min = min(y_vals) - 5
        y_max = max(y_vals) + 5

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers'))

        fig1.update_layout(
            title="Geschätzte Herzfrequenz über Zeit",
            xaxis_title="Messpunkt (Peak-Index)",
            yaxis_title="Herzfrequenz (bpm)",
            yaxis=dict(range=[y_min, y_max]),
            template="plotly_white"
            )

        self.fig1 = fig1
        return fig1

if __name__ == "__main__":

    unser_ekg = Ekg_tests(1, "10.2.2023", "data/ekg_data/01_Ruhe.txt")
    unser_ekg.find_peaks()
    list_of_hr = unser_ekg.estimate_hr()

    #plt.plot(list_of_hr)
    #plt.show()
    unser_ekg.plot_time_series(list_of_hr)