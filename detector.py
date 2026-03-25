import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 8192

FREQ_ONE = 18000
FREQ_ZERO = 16000
FREQ_PREAMBLE = 17000

TOLERANCE = 1500


def detect_freq(signal):
    fft_data = rfft(signal)
    freqs = rfftfreq(len(signal), 1 / RATE)
    magnitude = np.abs(fft_data)
    return freqs[np.argmax(magnitude)]


def classify(freq):
    if abs(freq - FREQ_ONE) < TOLERANCE:
        return '1'
    elif abs(freq - FREQ_ZERO) < TOLERANCE:
        return '0'
    elif abs(freq - FREQ_PREAMBLE) < TOLERANCE:
        return 'P'
    return None


def binary_to_string(binary):
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i + 8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def receive_signal(duration=4):
    p = pyaudio.PyAudio()
    print("[RX] Waiting for valid signal...")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("[RX] Listening...")

    bits = []
    preamble_count=3
    PREAMBLE_REQUIRED=3
    preamble_detected = False

    for _ in range(int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        window = np.hanning(len(signal))
        signal = signal * window

        freq = detect_freq(signal)
        symbol = classify(freq)

        if symbol == 'P':
            preamble_count+=1
            if preamble_count>=PREAMBLE_REQUIRED:
                preamble_detected=True
                print("[RX] Preamble detected")

                continue
            else:
                preamble_count=0
        print("[RX] Starting data capture...")
        if preamble_detected and symbol in ['0', '1']:
            bits.append(symbol)

    stream.stop_stream()
    stream.close()
    p.terminate()

    binary = ''.join(bits)
    message = binary_to_string(binary)

    print(f"[RX] Received: {message}")

    return message