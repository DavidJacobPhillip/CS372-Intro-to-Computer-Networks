'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 4-18-22
Program: Sockets & HTTP: HTTP Server
Description: This is a simple server program that sends some HTML
'''

# IMPORTS
import socket


'''
The world’s simplest HTTP server
'''
# Binding to IP address and port
host = "127.0.0.1" 
port = 1048  

# Creating server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
connection, address = server.accept()

# Sending and recieving data
recieved_data = connection.recv(1024)
sent_data = "HTTP/1.1 200 OK\r\n"\
    "Content-Type: text/html; charset=UTF-8\r\n\r\n"\
    "<html>Congratulations! You've downloaded the first Wireshark lab file!</html>\r\n"
connection.sendall(sent_data.encode())

# Printing Information
print("Connected by", address, "\n")
print("Recieved: ", recieved_data, "\n")
print("Sending>>>>>>>>>>")
print(sent_data)
print(">>>>>>>>>>")

# SOURCES
'''
[1] https://www.geeks3d.com/hacklab/20190110/python-3-simple-http-request-with-the-socket-module/
    - Helps identify how to make certain socket related connections
[2] https://www.internalpointers.com/post/making-http-requests-sockets-python
    - More resources on making socket related connections
    - Also has information on how to deal with recieving more than 4096 bytes
[3] https://realpython.com/python-sockets/
    - Information regarding how to create a simple Python server
'''