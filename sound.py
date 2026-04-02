import numpy as np
import sounddevice as sd
import time
FS = 44100
freq_one = 8000

freq_zero = 6000
freq_start = 4000
freq_end = 2000
BIT_DURATION = 0.04
MARKER_DURATION = 0.2

def generate_tone(freq, duration=BIT_DURATION):
    t = np.linspace(0,duration,int(FS * duration), False)
    return np.float32(1.0 * np.sin(2 * np.pi * freq * t))
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
    
    full_signal = []
    
    # Send Preamble (Start Marker)
    print(f"[TX] Generating START marker at {freq_start} Hz")
    full_signal.append(generate_tone(freq_start, MARKER_DURATION))
    
    # Gap between start and bits
    full_signal.append(np.zeros(int(FS * 0.02), dtype=np.float32))

    for bit in binary:
        freq = freq_one if bit == '1' else freq_zero
        full_signal.append(generate_tone(freq, BIT_DURATION))
        # Small bit gap
        full_signal.append(np.zeros(int(FS * 0.005), dtype=np.float32))

    # Send Terminator (End Marker)
    print(f"[TX] Generating END marker at {freq_end} Hz")
    full_signal.append(generate_tone(freq_end, MARKER_DURATION))
    
    # Play everything at once
    combined = np.concatenate(full_signal)
    print(f"[TX] Playing full signal ({len(combined)/FS:.2f}s)")
    sd.play(combined, FS)
    sd.wait()


