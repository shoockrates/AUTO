import socket

HOST = '0.0.0.0'
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Listening on port {PORT}...")

conn, addr = server.accept()
print(f"Connected by {addr}")

data = conn.recv(1024)
print(f"Received: {data.decode()}")

conn.sendall(b"ack: got your message")
conn.close()
