# Dial7_server and switch (Central office)
# audio freq bands
# narrow 300-3.4khz
# wide   50-7khz
# superwide 50-14khz
# full 20-20khz
import numpy as np
from scipy.io import wavfile
from dtmf report detect # pip install dtmf
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


#        zero           one        two        three        four        five        six        seven        eight       nine        star        pound        
DTMF = [(941,1336), (697,1209), (697,1336), (697,1477), (770,1209), (770,1336), (770,1477), (852,1209), (852,1336), (852,1477), (941,1209), (941,1477)] # [(low,high)]
#           0           1           2           3           4           5           6           7           8           9           10          11


def server_rx(HOST,PORT):
    global frames
    global DTMF
    with socket.socket() as server_socket_rx:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        conn, address = server_socket.accept()
        print("New Client Connection: " + address[0] + ":" + str(address[1]))
        tick = 0
        
        inf = [1,0,0,0,0,0,0,"none"] # [dialtone,isdialing?,ringing,busy,fastbusy,offhook,iscallconnected?,connectednumber]
        #                                  0        1        2       3        4       5            6             7
        
        while True:
            tick = tick + 1
            # logic
            try:
                data = conn.recv(2048)
                if inf[0] == 1:
                    # Party just connected, Dial active
                    # listen for dtmf
                    results = detect(data, 8000)
                    for result in results:
                        print(f"{result.start:<3d} - {result.end:>5d} : {result.tone!s}")
            except socket.error as error_message:
                break
          
rx = threading.Thread(target=server_rx, args = (HOST,PORT))
#rx.daemon = True
rx.start()
print("Dial7 - Server online")
