import numpy as np
from scipy.signal import find_peaks

def find_peaks_custom(signal, threshold=350, min_peak_distance=10):
    signal = np.asarray(signal).flatten() 
    peaks, _ = find_peaks(signal, height=threshold, distance=min_peak_distance)
    return peaks.tolist()