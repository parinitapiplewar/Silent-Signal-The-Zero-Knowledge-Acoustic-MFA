import numpy as np
import sounddevice as sd
import time
FS = 44100
DURATION = 0.3
freq_one = 8000
freq_zero = 6000
freq_start = 4000
freq_end = 2000
def generate_tone(freq, duration=DURATION):
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
    
    # Send Preamble (Start Marker)
    print(f"[TX] Sending START marker at {freq_start} Hz")
    sd.play(generate_tone(freq_start), FS)
    sd.wait()
    time.sleep(0.2)

    for bit in binary:
        freq = freq_one if bit == '1' else freq_zero
        print(f"[TX] Sending bit {bit} at {freq} Hz")
        tone = generate_tone(freq)
        sd.play(tone, FS)
        sd.wait()
        time.sleep(0.2)

    # Send Terminator (End Marker)
    print(f"[TX] Sending END marker at {freq_end} Hz")
    sd.play(generate_tone(freq_end), FS)
    sd.wait()
    time.sleep(0.2)