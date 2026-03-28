import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import butter, lfilter
import time

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

BANDS = {
    '1': (7500, 9000),
    '0': (5000, 6500),
    'S': (3500, 5000),
    'E': (1500, 3000)
}

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass(data, fs):
    b, a = butter_bandpass(1000.0, 10000.0, fs, order=5)
    return lfilter(b, a, data)

def detect_band(signal):
    filtered = apply_bandpass(signal, RATE)
    fft_data = rfft(filtered)
    freqs = rfftfreq(len(filtered), 1/RATE)
    mag = np.abs(fft_data)
    
    total_energy = np.sum(mag)
    
    band_energies = {}
    for sym, (low, high) in BANDS.items():
        mask = (freqs >= low) & (freqs <= high)
        band_energies[sym] = np.sum(mag[mask])
        
    return band_energies, total_energy


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
    detected_energies = []
    detected_bits = []

    # States
    STATE_WAITING = 0
    STATE_RECEIVING = 1
    STATE_COMPLETED = 2
    state = STATE_WAITING
    print("STATE \u2192 WAITING")

    # Buffer for sliding window
    symbol_buffer = []

    CHUNKS_PER_SEC = RATE / CHUNK
    waiting_for_gap = False

    noise_history = []
    frames_processed = 0
    baseline_frames = 10
    adaptive_threshold = 0

    for _ in range(int(CHUNKS_PER_SEC * duration)):
        if state == STATE_COMPLETED:
            break

        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        window = np.hanning(len(signal))
        signal = signal * window

        band_energies, total_energy = detect_band(signal)
        frames_processed += 1

        sym = None
        if frames_processed <= baseline_frames:
            noise_history.append(total_energy)
            if frames_processed == baseline_frames:
                adaptive_threshold = max(np.mean(noise_history) * 3, 1000)
                print(f"[DEBUG] Adaptive Threshold set to: {adaptive_threshold:.0f}")
        else:
            if total_energy >= adaptive_threshold:
                # Normalize energy
                norm_energies = {k: v / (total_energy + 1e-6) for k, v in band_energies.items()}
                best_sym = max(norm_energies, key=norm_energies.get)
                
                if norm_energies[best_sym] > 0.3:
                    sym = best_sym
                    print(f"[DEBUG] Thr: {adaptive_threshold:.0f} | Norms: { {k: round(v,2) for k,v in norm_energies.items()} } | Chosen: {best_sym}")

        detected_energies.append(int(total_energy))
        detected_bits.append(sym if sym else "None")

        symbol_buffer.append((sym, total_energy))
        if len(symbol_buffer) > 15:
            symbol_buffer.pop(0)

        # N=4 Bit Stability
        recent_4 = symbol_buffer[-4:] if len(symbol_buffer) >= 4 else symbol_buffer
        symbols_4 = [s[0] for s in recent_4]
        is_stable_4 = len(symbols_4) == 4 and all(s == symbols_4[0] for s in symbols_4)
        
        # N=9 Marker Stability (approx 200ms)
        recent_9 = symbol_buffer[-9:] if len(symbol_buffer) >= 9 else symbol_buffer
        symbols_9 = [s[0] for s in recent_9]
        is_stable_9 = len(symbols_9) == 9 and all(s == symbols_9[0] for s in symbols_9)

        stable_symbol = None
        if is_stable_4 and symbols_4[0] is not None:
            max_e = max(s[1] for s in recent_4)
            min_e = min(s[1] for s in recent_4)
            is_energy_stable = (max_e - min_e) / (max_e + 1e-6) < 0.5
            if is_energy_stable:
                stable_symbol = symbols_4[0]
                
        if is_stable_4 and symbols_4[0] is None:
            stable_symbol = None

        if stable_symbol is None:
            waiting_for_gap = False

        if state == STATE_WAITING:
            if is_stable_9 and symbols_9[0] == 'S':
                print("START detected (\u2265 200ms stability)")
                print("STATE \u2192 RECEIVING")
                state = STATE_RECEIVING
                waiting_for_gap = True

        elif state == STATE_RECEIVING:
            if is_stable_9 and symbols_9[0] == 'E':
                print("END detected (\u2265 200ms stability)")
                state = STATE_COMPLETED

            elif stable_symbol in ['0', '1']:
                if not waiting_for_gap:
                    print(f"Stable Band \u2192 Bit {stable_symbol}")
                    bits.append(stable_symbol)
                    waiting_for_gap = True
            
            elif stable_symbol == 'S':
                pass # Ignore further START markers

    stream.stop_stream()
    stream.close()
    p.terminate()

    binary = ''.join(bits)
    message = binary_to_string(binary)

    print(f"[RX] Received: {message}")

    return message, binary, detected_energies, detected_bits