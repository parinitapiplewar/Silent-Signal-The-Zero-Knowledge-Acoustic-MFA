import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 8192
THRESHOLD = 500

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Listening up to 20kHz...")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        if np.max(np.abs(signal)) < THRESHOLD:
            continue

        # Apply window
        window = np.hanning(CHUNK)
        signal = signal * window

        fft_data = rfft(signal)
        frequencies = rfftfreq(CHUNK, 1/RATE)
        magnitude = np.abs(fft_data)

        peak_index = np.argmax(magnitude)
        dominant_freq = frequencies[peak_index]
        peak_amp = (2 / CHUNK) * magnitude[peak_index]

        if 10 < dominant_freq < 20000:
            print(f"{dominant_freq:.2f} Hz")

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

