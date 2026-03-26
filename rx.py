import pyaudio
import numpy as np
from config import RATE, CHUNK, BIT_DURATION
from dsp import detect_symbol
from codec import decode

def receive(duration=6):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    symbols = []
    total = int(duration / BIT_DURATION)

    print("[RX] Listening...")

    for _ in range(total):
        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)

        result = detect_symbol(signal)
        if result:
            sym, powers = result
            symbols.append(sym)

            print(f"[DBG] {sym} → {powers}")

    stream.close()
    p.terminate()

    bitstream = ''.join('1' if s == '1' else '0' for s in symbols)

    message = decode(bitstream)
    print("[RX] Message:", message)

    return message