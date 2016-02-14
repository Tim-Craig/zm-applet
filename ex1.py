import socket

sock = socket.socket()
sock.connect(('localhost', 1234))
sock.send('foo\n' * 10 * 1024 * 1024)