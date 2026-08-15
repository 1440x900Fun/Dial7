# Client Subscription xd
import socket, pyaudio, sounddevice, os, queue, threading
# Socket
HOST = socket.gethostname()
PORT = 8080
import numpy as np
# Audio
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt8 # paInt16
CHANNELS = 1
RATE = 8000#44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "clioutput.wav"

def read_kbd_input(inputQueue):
    print('Use the keypad to input a number and press enter when ready')
    while (True):
        input_str = input()
        inputQueue.put(input_str)

pyAud = pyaudio.PyAudio()
foundUSBMic = False
dev_index = -1
for i in range(pyAud.get_device_count()):
    dev = pyAud.get_device_info_by_index(i)
    print((i, dev['name'], dev['maxInputChannels']))
    if dev['name'] == 'USB PnP Sound Device: Audio (hw:1,0)':
        foundUSBMic = True
        dev_index = i 
if foundUSBMic == False or dev_index == -1:
    print("USB MIC NOT FOUND")

keypad = ""
inputQueue = queue.Queue()
inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
inputThread.start()
#stream = p.open(format=FORMAT,
#                channels=CHANNELS,
#                rate=RATE,
#                input=True,
#                frames_per_buffer=CHUNK)
print("Recording...")
with socket.socket() as client_socket:
    client_socket.connect((HOST, PORT))
    while True:
        #print("waiting for infstring")
        infstr = client_socket.recv(14)
        infstr = infstr.decode('utf-8')
        inf = infstr.split(",")
        # inf = [1,0,0,0,0,0,0,"none"] # [dialtone,isdialing?,ringing,busy,fastbusy,offhook,iscallconnected?,incoming,connectednumber]
        #                                  0        1        2       3        4       5            6            7           8
        dialtone = int(inf[0])
        isdialing = int(inf[1])
        ringing = int(inf[2])
        busy = int(inf[3])
        fastbusy = int(inf[4])
        offhook = int(inf[5])
        iscallconnected = int(inf[6])
        #print(inf)
        if isdialing == 1:
            if (inputQueue.qsize() > 0):
                input_str = inputQueue.get()
                #print("Sending the value:")
                client_socket.send(input_str.encode('utf-8')) # Key pad
                #print(input_str)
            if (input_str == "hang up"):
                print("Hanging up...")
                break
            else:
                client_socket.send(b' ') # Key pad
            
        if dialtone == 1:
            if (inputQueue.qsize() > 0):
                input_str = inputQueue.get()
                print("Sending the value:")
                client_socket.send(input_str.encode('utf-8')) # Key pad
                #print(input_str)
            else:
                client_socket.send(b' ') # Key pad
        
        if ringing == 1:
            print("RINGING...")
            client_socket.send(b' ') # Key pad

        if incoming == 1:
            print("RING! Incoming call!")

        
        if (inputQueue.qsize() > 0):
                input_str = inputQueue.get()
                #print("Sending the value:")
                if input_str == "call":
                    print("Please wait...")
                    client_socket.send(input_str.encode('utf-8')) # Key pad
                
            #print(input_str)
                if (input_str == "hangup"):
                    print("Hanging up...")
                    client_socket.send(input_str.encode('utf-8')) # Key pad
                    
                break
            else:
                client_socket.send(b' ') # Key pad
            
            
