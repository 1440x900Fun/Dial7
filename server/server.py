# Dial7_server and switch (Central office)
# audio freq bands
# narrow 300-3.4khz
# wide   50-7khz
# superwide 50-14khz
# full 20-20khz
import numpy as np
from scipy.io import wavfile
import wave
import pyaudio

p = pyaudio.PyAudio()
# needs bi-dir full dupe comms
# progress tones
# tone = (lowFhz,highFhz) | -1 N/A
busy = (480,620)
fastbusy = 0.25
slowbusy = 0.50
dial = (350,440)
ring = (440,480)
zip = (440,-1)
def audiosine(f=440.0, t=3.0, s=8000, v=0.5, fn="s.wav"):
  total = np.linspace(0, t, int(s*t), endpoint=False)
  wave = np.sin(2 * np.pi * f * total)
  #  audio = (wave * v * 32767).astype(np.int16) 16bit
  audio = (wave * v * 255).astype(np.int16) # 8bit
  wavfile.write(fn, s, audio)

HOST = ""
PORT = 100
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000 #44100
WAVE_OUTPUT_FILENAME = "output.wav"
frames = []

with socket.socket() as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    conn, address = server_socket.accept()
    print("New Client Connection: " + address[0] + ":" + str(address[1]))
    while True:
        try:
            data = conn.recv(2048)
            frames.append(data)
        except socket.error as error_message:
            break

print(frames)

with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
