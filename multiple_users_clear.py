import socket
import pyaudio
import threading
import tkinter as tk
import RPi.GPIO as GPIO
import time

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345     # Port for sender
RECEIVER_IPS = ['192.168.41.137', '192.168.41.219', '192.168.41.155']  # List of receiver IP addresses
RECEIVER_PORTS = [12386, 12397, 12348]  # List of receiver ports
RECEIVER_PORT = 12346   # Port for receiver

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet

last_time = time.time()

GPIO.setmode(GPIO.BCM)
gpio_pin = 17  # Change this to the actual GPIO pin number you're using
GPIO.setup(gpio_pin, GPIO.OUT)
sending = True
GPIO.output(gpio_pin, GPIO.HIGH)

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_streams = [audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
                    for _ in RECEIVER_IPS]

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in RECEIVER_IPS]

receiver_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in RECEIVER_PORTS]
for i, port in enumerate(RECEIVER_PORTS):
    receiver_sockets[i].bind((SENDER_HOST, port))

ptt_active = False

def send_audio():
	while True:
		data = sender_stream.read(CHUNK)
		for i, receiver_ip in enumerate(RECEIVER_IPS):
			#print(data)
			for j in range(0, len(data), MAX_PACKET_SIZE):
				chunk = data[j:j+MAX_PACKET_SIZE]
				sender_sockets[i].sendto(chunk, (receiver_ip, RECEIVER_PORT))
				print(RECEIVER_PORT, ' ', receiver_ip)

def receive_audio(receiver_socket, receiver_stream):
    global sending, last_time
    while True:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)
        #print(data)

def checktime():
    global last_time, sending
    while True:
        time_elapsed = time.time() - last_time
        if time_elapsed >= 1:
            GPIO.output(gpio_pin, GPIO.HIGH)
            sending = True
            print("sending")
        time.sleep(0.1)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_threads = [threading.Thread(target=receive_audio, args=(receiver_sockets[i], receiver_streams[i]))
                    for i in range(len(RECEIVER_IPS))]
check_thread = threading.Thread(target=checktime)

sender_thread.start()
for thread in receiver_threads:
    thread.start()
check_thread.start()

def key_pressed(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = True
        print("Talking...")

def key_released(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = False
        print("Not talking...")

root = tk.Tk()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
root.mainloop()
