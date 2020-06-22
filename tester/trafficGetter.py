import socket
HOST = 'google.com'    # The remote host
PORT = 80              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('GET / HTTP/1.1\r\nHost: google.com\r\n\r\n'.encode())
data = s.recv(1024)
s.close()
print('Received', repr(data))