import numpy as np
import sounddevice as sd
import time
FS = 44100
DURATION =0.2
freq_one = 21000
freq_zero=19000
def generate_tone(freq, duration=DURATION):
    t = np.linspace(0,duration,int(FS * duration), False)
    return np.float32(0.5 * np.sin(2 * np.pi * freq * t))
def encode_data(data):
    """
    Converts string to binary
    """
    binary=''.join(format(ord(c),'08b') for c in data)
    return binary
def send_signal(data):
    """
    Encodes data and transmits as ultrasonic tones
    """
    binary=encode_data(data)
    print(f"[TX] Sending binary: {binary}")
    for bit in binary:
        freq=freq_one if bit=='1' else freq_zero
        tone=generate_tone(freq)
        sd.play(tone,FS)
        sd.wait()
        time.sleep(0.01)