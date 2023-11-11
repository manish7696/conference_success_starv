import socket
import pyaudio
import threading
import tkinter as tk

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12397     # Port for sender
RECEIVER_IP = '192.168.41.208'  # Receiver's IP address
RECEIVER_PORT = 12397   # Port for receiver
port = 12346
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet
server_ip = '192.168.41.208'  # Raspberry Pi's IP address
server_port = 12356
sending =  True
# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((SENDER_HOST, port))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ptt_active = False


def send_audio():
	while True:
		data = sender_stream.read(CHUNK)
		for i in range(0, len(data), MAX_PACKET_SIZE):
			chunk = data[i:i+MAX_PACKET_SIZE]
			sender_socket.sendto(chunk, (RECEIVER_IP, RECEIVER_PORT))

def receive_audio():
    while True:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_thread = threading.Thread(target=receive_audio)
sender_thread.start()
receiver_thread.start()

def key_pressed(event):
    if event.keysym == 'p':
        client_socket.sendto(b'high', (server_ip, server_port))
    global ptt_active
    if event.keysym == 'p':
        ptt_active = True
        print("Talking...")

def key_released(event):
    if event.keysym == 't':
        client_socket.sendto(b'low', (server_ip, server_port))

    global ptt_active
    if event.keysym == 't':
        ptt_active = False
        print("Not talking...")

root = tk.Tk()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
root.mainloop()
