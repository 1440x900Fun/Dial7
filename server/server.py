# Dial7_server and switch (Central office)
# audio freq bands
# narrow 300-3.4khz
# wide   50-7khz
# superwide 50-14khz
# full 20-20khz
import numpy as np


# number database
numbers = {
    "0":          "192.168.0.1",
    "1921680143": "192.168.0.143",
    "1921680148": "192.168.0.148",
    "7166338367": "192.168.0.145"
}

nextroute = "192.168.0.150" # IP of server with other number database if local network database is not suffciant, contact other router
# If no number is found, Reject it.





# pip install dtmf
# from dtmf import detect
from typing import Iterable
from typing import NamedTuple
from typing import Tuple
from typing import Callable


_freqs = [
    697.0,
    770.0,
    852.0,
    941.0,
    1209.0,
    1336.0,
    1477.0,
    1633.0
]

_freq_map = {
    "1": [697.0, 1209.0],
    "2": [697.0, 1336.0],
    "3": [697.0, 1477.0],
    "A": [697.0, 1633.0],
    "4": [770.0, 1209.0],
    "5": [770.0, 1336.0],
    "6": [770.0, 1477.0],
    "B": [770.0, 1633.0],
    "7": [852.0, 1209.0],
    "8": [852.0, 1336.0],
    "9": [852.0, 1477.0],
    "C": [852.0, 1633.0],
    "*": [941.0, 1209.0],
    "0": [941.0, 1336.0],
    "#": [941.0, 1477.0],
    "D": [941.0, 1633.0]
}

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
HOST = socket.gethostname()
PORT = 8080

import math

from math import cos
from math import exp
from math import pi



#        zero           one        two        three        four        five        six        seven        eight       nine        star        pound        
DTMF = [(941,1336), (697,1209), (697,1336), (697,1477), (770,1209), (770,1336), (770,1477), (852,1209), (852,1336), (852,1477), (941,1209), (941,1477)] # [(low,high)]
#           0           1           2           3           4           5           6           7           8           9           10          11

import time
def server_rx(HOST,PORT):
    global frames
    global DTMF
    global numbers
    global nextroute
    with socket.socket() as server_socket:
        keypads = ""
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print("Waiting for client...")
        conn, address = server_socket.accept()
        print("New Client Connection: " + address[0] + ":" + str(address[1]))
        tick = 0
        inf = [1,0,0,0,0,0,0,"none"] # [dialtone,isdialing?,ringing,busy,fastbusy,offhook,iscallconnected?,connectednumber]
        #                                  0        1        2       3        4       5            6             7
        infstr = f"{inf[0]},{inf[1]},{inf[2]},{inf[3]},{inf[4]},{inf[5]},{inf[6]}" # 13 bytes
        rx = threading.Thread(target=server_rx, args = (HOST,PORT))
        time.sleep(1)
        todial = 100000 # added tick to start a call
        tries = 0
        while True:
            tick = tick + 1
            infstr = f"{inf[0]},{inf[1]},{inf[2]},{inf[3]},{inf[4]},{inf[5]},{inf[6]}" # 13 bytes
            print(tick)
            print(todial)
            # logic
            try:
                #print("sending infstring")
                conn.send(infstr.encode('utf-8'))
                #print("waiting for keypad")
                data = conn.recv(1)
                if inf[2] == 1:
                    # alert the other party
                    print("Ringing: " + keypads)
                    try:
                        print("Attempting to contact:")
                        print(numbers[keypads])
                        if tries == 6:
                            inf[2] = 0 # End
                            # Go to voice mail?
                        tries = tries + 1
                    except:
                        # Contact external server?
                        # The number you dialed is not in service, Please check the number and try your call again. Thank you
                        
                        
                    
                    time.sleep(6)

                
                if inf[0] == 0 and inf[1] == 0 and inf[6] == 0 and inf[2] == 0:
                    print("DISCONNECTED CALL")
                    inf[4] = 1
                if inf[1] == 1:
                    #print("Client is dialing!")
                    dec = data.decode('utf-8')
                    if dec != " ":
                        keypads = f"{keypads}{dec}"
                        print("New Digit Recivied")
                        print(keypads)
                        if len(keypads) > 0:
                            todial = tick + 100000
                        
                if inf[0] == 1: 
                    # dial tone active
                    # the too long checkd
                    if tick > 68000:
                        inf[0] = 0 # Turn off the dial tone
                    print("waiting for hook response...")
                    if data != b' ':
                        print("Recived key from a client!")
                        inf[0] = 0 # Turn off the dial tone
                        inf[1] = 1 # Start parsing digits
                        todial = tick + 100000
                        dec = data.decode('utf-8')
                        keypads = f"{keypads}{dec}"
                        print(keypads)
                if inf[1] == 1:
                    # make call check
                    if tick > todial:
                        # Connect the calling party to the destination party
                        print("Connecting the calling party...")
                        inf[1] = 0
                        inf[2] = 1
                        

                    
                
                    
                        
            except socket.error as error_message:
                break
          
rx = threading.Thread(target=server_rx, args = (HOST,PORT))
rx.start()
print("Dial7 - Server online")
