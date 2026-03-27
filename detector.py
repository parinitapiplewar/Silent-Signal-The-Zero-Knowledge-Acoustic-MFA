import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 8192

FREQ_ONE = 21000
FREQ_ZERO = 19000
FREQ_PREAMBLE = 20000

TOLERANCE = 1500


def detect_freq(signal):
    fft_data = rfft(signal)
    freqs = rfftfreq(len(signal), 1/RATE)
    mag = np.abs(fft_data)
    return freqs[np.argmax(mag)]


def classify(freq):
    # Tolerance-based classification into ranges for framing and data
    if 16000 <= freq <= 18500:
        return '1'
    elif 14000 <= freq < 16000:
        return '0'
    elif 12500 <= freq < 14000:
        return 'S'  # Start marker
    elif 10000 <= freq < 12500:
        return 'E'  # End marker
    else:
        return None  # Ignore noise outside valid ranges


def binary_to_string(binary):
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def receive_signal(duration=30):
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

    # State variables for stability check
    consecutive_symbol = None
    consecutive_count = 0
    last_accepted_symbol = None
    
    # State tracking for framing
    has_started = False
    CHUNKS_PER_SEC = RATE / CHUNK

    for _ in range(int(CHUNKS_PER_SEC * duration)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        window = np.hanning(len(signal))
        signal = signal * window

        freq = detect_freq(signal)
        symbol = classify(freq)
        
        detected_freqs.append(int(freq))
        
        if symbol:
            detected_bits.append(symbol)
            print(f"Detected: {freq:.0f} Hz -> Candidate {symbol} (inside valid range)")
            
            # Ensure frequency remains stable for a short duration
            if symbol == consecutive_symbol:
                consecutive_count += 1
            else:
                consecutive_symbol = symbol
                consecutive_count = 1
                
            # Accept if stable for 2 chunks and it is a new symbol (gap detected before)
            if consecutive_count >= 2 and symbol != last_accepted_symbol:
                print(f"Classified Stable Marker/Bit: {symbol}")
                last_accepted_symbol = symbol
                
                if symbol == 'S':
                    print("[RX] Start marker verified. Accumulating signal...")
                    has_started = True
                elif symbol == 'E':
                    if has_started:
                        print("[RX] End marker verified. Terminating listening early.")
                        break
                elif has_started and symbol in ['0', '1']:
                    print(f"Classified Stable Bit -> Append: {symbol}")
                    bits.append(symbol)
        else:
            detected_bits.append("None")
            # If frequency is outside bounds, reset the stability tracker
            # This allows identical consecutive bits like "00" to be detected safely
            consecutive_symbol = None
            consecutive_count = 0
            last_accepted_symbol = None

    stream.stop_stream()
    stream.close()
    p.terminate()

    binary = ''.join(bits)
    message = binary_to_string(binary)

    print(f"[RX] Received: {message}")

    return message, binary, detected_freqs, detected_bits