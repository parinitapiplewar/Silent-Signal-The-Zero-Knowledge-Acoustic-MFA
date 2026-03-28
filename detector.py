import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq
import time

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024


def detect_freq(signal):
    fft_data = rfft(signal)
    freqs = rfftfreq(len(signal), 1/RATE)
    mag = np.abs(fft_data)
    return freqs[np.argmax(mag)]


def classify(freq):
    # Detection ranges based on task specs:
    if 7500 <= freq <= 9000:
        return '1'
    elif 5500 <= freq <= 7000:
        return '0'
    elif 3500 <= freq <= 5000:
        return 'S'  # Start marker
    elif 1500 <= freq <= 3000:
        return 'E'  # End marker
    else:
        return None  # Overlap or intermediate gaps


def binary_to_string(binary):
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def receive_signal(duration=60):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("[RX] Listening...")

    bits = []
    detected_freqs = []
    detected_bits = []

    # States
    STATE_WAITING = 0
    STATE_RECEIVING = 1
    STATE_COMPLETED = 2
    state = STATE_WAITING
    print("STATE \u2192 WAITING")

    # Buffer for sliding window
    symbol_buffer = []
    N = 4

    CHUNKS_PER_SEC = RATE / CHUNK
    last_bit_time = 0
    BIT_GATE_SEC = 0.25  # time-based gating min distance

    for _ in range(int(CHUNKS_PER_SEC * duration)):
        if state == STATE_COMPLETED:
            break

        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        window = np.hanning(len(signal))
        signal = signal * window

        freq = detect_freq(signal)
        
        # Ignore frequencies < 1000 Hz and > 10000 Hz
        if freq < 1000 or freq > 10000:
            symbol = None
        else:
            symbol = classify(freq)
        
        detected_freqs.append(int(freq))
        
        if symbol is not None:
            detected_bits.append(symbol)
        else:
            detected_bits.append("None")

        symbol_buffer.append(symbol)
        if len(symbol_buffer) > N:
            symbol_buffer.pop(0)

        if len(symbol_buffer) < N:
            continue

        # Smoothing: only accept if all elements in buffer are the same
        is_stable = all(s == symbol_buffer[0] for s in symbol_buffer)
        stable_symbol = symbol_buffer[0] if is_stable else None

        current_time = time.time()

        if state == STATE_WAITING:
            if stable_symbol == 'S':
                print("START detected")
                print("STATE \u2192 RECEIVING")
                state = STATE_RECEIVING

        elif state == STATE_RECEIVING:
            if stable_symbol == 'E':
                print("END detected")
                state = STATE_COMPLETED

            elif stable_symbol in ['0', '1']:
                if current_time - last_bit_time > BIT_GATE_SEC:
                    print(f"Stable {int(freq)} Hz \u2192 Bit {stable_symbol}")
                    bits.append(stable_symbol)
                    last_bit_time = current_time
            
            elif stable_symbol == 'S':
                pass # Ignore further START detections
            
            elif stable_symbol is None:
                pass # Treat as gap, DO NOT append bit

    stream.stop_stream()
    stream.close()
    p.terminate()

    binary = ''.join(bits)
    message = binary_to_string(binary)

    print(f"[RX] Received: {message}")

    return message, binary, detected_freqs, detected_bits