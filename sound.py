import numpy as np
import sounddevice as sd
fs = 44100
duration =2
frequency = 21000
t = np.linspace(0,duration,int(fs * duration), False)
tone = 0.8 * np.sin(2 * np.pi * frequency * t)
print("Playing 1000Hz tone...")
sd.play(tone, fs)
sd.wait()
print("Done.") 