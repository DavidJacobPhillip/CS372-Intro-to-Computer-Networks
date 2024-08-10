'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 4-18-22
Program: Sockets & HTTP: Small File
Description: This is a simple program that does GET requests from a server
'''

# IMPORTS
import socket

'''
Using a socket to GET a file
'''
# Creating the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
 
# Connecting the client
host = "gaia.cs.umass.edu" 
port = 80 
client.connect((host, port))  

# Sending request
request = "GET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
client.send(request.encode())  
 
# Recieving data from request (up to 4096 bytes)
response = client.recv(4096)  
response_length = len(repr(response))

# Printing response
print("Request: ", request)
print("[RECV] - length: %d" % response_length)
print(response.decode())

# Closing connetion
client.close()


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

