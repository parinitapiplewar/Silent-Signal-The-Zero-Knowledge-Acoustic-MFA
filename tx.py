import numpy as np
import sounddevice as sd
import time
from config import RATE, BIT_DURATION, FREQ
from codec import encode

def tone(freq):
    t = np.linspace(0, BIT_DURATION, int(RATE * BIT_DURATION), False)
    return 0.5 * np.sin(2 * np.pi * freq * t).astype(np.float32)

def send(data):
    encoded = encode(data)
    print("[TX]", data)

    for bit in encoded:
        freq = FREQ[bit] if bit in FREQ else FREQ['0']
        sd.play(tone(freq), RATE)
        sd.wait()
        time.sleep(0.01)