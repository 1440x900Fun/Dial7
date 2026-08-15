# Dial7_server and switch (Central office)
# audio freq bands
# narrow 300-3.4khz
# wide   50-7khz
# superwide 50-14khz
# full 20-20khz
import numpy as np
from scipy.io import wavfile
import wave
import pyaudio, socket, threading

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


import math
# https://gist.github.com/sebpiq/4128537
def goertzel(samples, sample_rate, *freqs):
    """
    Implementation of the Goertzel algorithm, useful for calculating individual
    terms of a discrete Fourier transform.
    `samples` is a windowed one-dimensional signal originally sampled at `sample_rate`.
    The function returns 2 arrays, one containing the actual frequencies calculated,
    the second the coefficients `(real part, imag part, power)` for each of those frequencies.
    For simple spectral analysis, the power is usually enough.
    Example of usage :
        freqs, results = goertzel(some_samples, 44100, (400, 500), (1000, 1100))
    """
    window_size = len(samples)
    f_step = sample_rate / float(window_size)
    f_step_normalized = 1.0 / window_size
    # Calculate all the DFT bins we have to compute to include frequencies
    # in `freqs`.
    bins = set()
    for f_range in freqs:
        f_start, f_end = f_range
        k_start = int(math.floor(f_start / f_step))
        k_end = int(math.ceil(f_end / f_step))
        if k_end > window_size - 1: raise ValueError('frequency out of range %s' % k_end)
        bins = bins.union(range(k_start, k_end))
    # For all the bins, calculate the DFT term
    n_range = range(0, window_size)
    freqs = []
    results = []
    for k in bins:
        # Bin frequency and coefficients for the computation
        f = k * f_step_normalized
        w_real = 2.0 * math.cos(2.0 * math.pi * f)
        w_imag = math.sin(2.0 * math.pi * f)
        # Doing the calculation on the whole sample
        d1, d2 = 0.0, 0.0
        for n in n_range:
            y  = samples[n] + w_real * d1 - d2
            d2, d1 = d1, y
        # Storing results `(real part, imag part, power)`
        results.append((
            0.5 * w_real * d1 - d2, w_imag * d1,
            d2**2 + d1**2 - w_real * d1 * d2)
        )
        freqs.append(f * sample_rate)
    return freqs, results





def audiosine(f=440.0, t=3.0, s=8000, v=0.5, fn="s.wav"):
  total = np.linspace(0, t, int(s*t), endpoint=False)
  wave = np.sin(2 * np.pi * f * total)
  #  audio = (wave * v * 32767).astype(np.int16) 16bit
  audio = (wave * v * 255).astype(np.int16) # 8bit
  wavfile.write(fn, s, audio)

HOST = socket.gethostname()
PORT = 100
FORMAT = pyaudio.paInt8
CHANNELS = 1
RATE = 8000 #44100
WAVE_OUTPUT_FILENAME = "srvoutput.wav"
frames = []

def server_rx(HOST,PORT):
    global frames
    
    with socket.socket() as server_socket_rx:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        conn, address = server_socket.accept()
        print("New Client Connection: " + address[0] + ":" + str(address[1]))
        tick = 0
        inf = [1,0,0,0,0,0,"none"] # [dialtone,isdialing?,busy,fastbusy,offhook,iscallconnected?,connectednumber]
        #                                0        1        2       3        4            5            6
        while True:
            tick = tick + 1
            # logic
            data = conn.recv(2048)
            frames.append(data)
            if inf[0] == 1:
                # Party just connected, Dial active
                # listen for dtmf
                freqs, results = goertzel(some_samples, 8000, (400, 500), (1000, 1100))
            try:
            except socket.error as error_message:
                break
          


rx = threading.Thread(target=server_rx, args = (HOST,PORT))
#rx.daemon = True
rx.start()

print(frames)

with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
