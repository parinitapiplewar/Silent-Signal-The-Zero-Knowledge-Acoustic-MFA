import numpy as np
import sounddevice as sd
import time

FS = 44100
BIT_DURATION = 0.2

FREQ_ONE = 18000
FREQ_ZERO = 16000
FREQ_PREAMBLE = 17000


def generate_tone(freq, duration=BIT_DURATION):
    t = np.linspace(0, duration, int(FS * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * freq * t)
    return np.float32(tone)


def encode_data(data):
    return ''.join(format(ord(c), '08b') for c in data)


def play_tone(freq):
    tone = generate_tone(freq)
    sd.play(tone, FS)
    sd.wait()


def send_signal(data):
    binary = encode_data(data)

    print(f"[TX] Sending: {data}")

    # PREAMBLE
    for _ in range(5):
        play_tone(FREQ_PREAMBLE)
        time.sleep(0.02)

    # DATA
    for bit in binary:
        freq = FREQ_ONE if bit == '1' else FREQ_ZERO
        play_tone(freq)
        time.sleep(0.02)