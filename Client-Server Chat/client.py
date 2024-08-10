'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 6-6-22
Program: Client-Server Chat
Description: This is a program (client-side) that allows for communication between a server and a client through the game "hangman"
Resources:
- https://docs.python.org/3/howto/sockets.html
- https://docs.python.org/3/library/socket.html
- https://realpython.com/python-sockets/
- https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
- https://stackoverflow.com/questions/4394145/picking-a-random-word-from-a-list-in-python
- http://net-informations.com/python/basics/contains.htm#:~:text=Using%20Python's%20%22in%22%20operator,%2C%20otherwise%2C%20it%20returns%20false%20.
- https://favtutor.com/blogs/replace-character-string-python
'''

# IMPORTS
import socket


# GLOBALS
PORT = 1025


# MAIN
def main():
    # Creating Socket Connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((socket.gethostname(), PORT))
    data = b""

    # Sending/recieving messages from server
    with client:
        # Printing messages
        print("Connected to: local host on port:", PORT)
        print()
        print("Welcome to hangman! Enter in a letter to start guessing (enter /q to quit at anytime)")
        print("Waiting for message...")

        # Sending & Recieving in a loop
        while True:
            # Breaking loop if previous message has the quit symbol
            if "/q" in data.decode('ascii'):
                break

            # Sending message
            message = input("> ")
            client.sendall(message.encode('ascii'))

            # Recieving message
            data = client.recv(1024)      
            print(data.decode('ascii'))                                  
            # client.sendall(b"\q")


# CALLING MAIN
if __name__ == "__main__":
    main()
