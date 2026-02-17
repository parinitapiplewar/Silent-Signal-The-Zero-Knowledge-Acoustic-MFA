import numpy as np
import sounddevice as sd
def tonality(fs = 44100,duration =2,frequency = 21000):
    t = np.linspace(0,duration,int(fs * duration), False)
    return np.float32(0.8 * np.sin(2 * np.pi * frequency * t)),fs
tone,fs= tonality()
if __name__ == "__main__":
    # This only runs if you play sound.py directly
    tone, fs = tonality()
    sd.play(tone, fs)

