import numpy as np
from scipy.signal import butter, lfilter
from config import RATE, FREQ, ENERGY_THRESHOLD

def bandpass(signal, low=17000, high=20000):
    nyq = 0.5 * RATE
    b, a = butter(4, [low/nyq, high/nyq], btype='band')
    return lfilter(b, a, signal)

def goertzel(samples, freq):
    N = len(samples)
    k = int(0.5 + (N * freq) / RATE)
    omega = (2.0 * np.pi * k) / N
    coeff = 2.0 * np.cos(omega)

    s_prev = s_prev2 = 0
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s

    return s_prev2**2 + s_prev**2 - coeff * s_prev * s_prev2

def detect_symbol(signal):
    signal = bandpass(signal)
    signal = signal / (np.max(np.abs(signal)) + 1e-6)

    powers = {k: goertzel(signal, f) for k, f in FREQ.items()}
    symbol = max(powers, key=powers.get)

    if powers[symbol] < ENERGY_THRESHOLD:
        return None

    return symbol, powers