import pandas as pd

def find_peaks(df_ekg, threshold, min_peak_distance):
    list_of_index_of_peaks = []
    last_peaks_index = 0
    for index, row in df_ekg.iterrows():
        if index < df_ekg.index.max() -1:
        #wenn row größer als das vorhegehende und das nachfolgende Element
        #dann füge den aktuellen Index der Liste hinzu
            if row["Voltage in [mV]"] >= df_ekg.iloc[index-1]["Voltage in [mV]"] and row["Voltage in [mV]"] > df_ekg.iloc[index+1]["Voltage in [mV]"]:
                
                if row["Voltage in [mV]"] > threshold and index - last_peaks_index > min_peak_distance:
                    list_of_index_of_peaks.append(index)
                    last_peaks_index = index
    return list_of_index_of_peaks