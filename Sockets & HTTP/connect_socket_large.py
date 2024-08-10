'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 4-18-22
Program: Sockets & HTTP: Large File
Description: This is a simple program that does large GET requests from a server
'''

# IMPORTS
import socket

'''
GET the data for a large file
'''
# Creating the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
 
# Connecting the client
host = "gaia.cs.umass.edu" 
port = 80 
client.connect((host, port))  

# Sending request
request = "GET /wireshark-labs/HTTP-wireshark-file3.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
client.send(request.encode())  
 
# Recieving data from request (loops until no more data is recieved)
response_length = 0
response = b""

while True:
    # Combining all the chunks together in one loop
    chunk = client.recv(4096)
    if len(chunk) == 0:     # No more data received, quitting
        break
    response = response + chunk

    # Adding up the length of the chunk sizes together
    response_length = response_length + len(repr(chunk))

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

