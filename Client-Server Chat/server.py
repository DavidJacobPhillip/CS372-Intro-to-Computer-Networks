'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 6-6-22
Program: Client-Server Chat
Description: This is a program (server-side) that allows for communication between a server and a client through the game "hangman"
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
import random


# GLOBALS
PORT = 1025
bank = ["apple", "breadwinner", "cs372", "networks"]                            # Bank of words
word = ""                                                                       # Holds the word itself that is to be guessed
l_word = ""                                                                     # Holds an underlined version of the word
parts = 5                                                                       # Gives the user "4 body parts" or chances


# FUNCTIONS
# Chooses a random word and sets up the program for hangman
def startup():
    global bank, word, l_word

    # Choosing a random word from the bank of words
    word = random.choice(bank)

    # Creating a version of the word to send to the client that only has lines
    for letter in word: l_word += "_"

# Updating the word based on alphanumeric guesses
def update(guess):
    global bank, word, l_word
    current = 0
    existence = 0                                                               # Keeps track of whether the letter existed to add body parts for the hangman

    # Replacing letters based on the guess
    for letter in word: 
        if letter == guess:
            l_word = l_word[:current] + guess + l_word[current+1:] 
            existence = 1
        current += 1

    # Checks whether the word has been completely found
    if "_" not in l_word:
        existence = 2

    # Returns whether or not it found the word
    return existence

# Tells the user how many chances they have left
def chances(existence):
    global parts

    # If word has been found
    if existence == 2:
        message = "You have found the word! Good job! /q"
        print("Guessed the word!")

    # If a correct letter has been found
    elif existence == 1:
        message = "That letter exists in the word!"
        print("Guessed a letter! Currently found: ", l_word)

    # If an incorrect letter has been found
    else:
        print("Incorrect guess! Currently found: ", l_word, "   Guesses Remaining: ", parts)
        parts -= 1
        if parts == 4:
            message = "No more arms..."
        elif parts == 3:
            message = "No more legs..."
        elif parts == 2:
            message = "No more torso..."
        elif parts == 1:
            message = "No more chest"
        else:
            message = "No more head... Good try, play again sometime! The word was \"" + word + "\"    /q"

    return message


# MAIN
def main():
    startup()
    
    # Creating the socket connection and binding it to a public host and port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                  # Create an INET, STREAMing socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                # Allows for the reuse of the socket
    server.bind((socket.gethostname(), PORT))                                   # Bind the socket to a public host, and a well-known port
    server.listen(5)                                                            # Listens to at most 5 connections before stopping

    # Listening and accepting client connections
    connection, address = server.accept()

    # Sending data to the client
    with connection:
        # Printing messages
        print("Server listening on: local host on port:", PORT)
        print(f"Connected by {address}")
        print("Waiting for message...")
        print()
        print("Chosen Word: ", word)

        # Recieving data while the connection exists
        while True:
            # Recieving message
            data = connection.recv(1024)                                        # Recieves up to 1024 bytes at a time and reads it in
            message = chances(update(data.decode('ascii')))

            # Sending message to end game if "/q" is preemptively detected
            if "/q" in data.decode('ascii'):
                print("Ending preemptively because user typed in /q")
                connection.sendall(b'/q')
                break

            # Sending message otherwise
            else:
                send = "Letters Found: " + l_word + "   " + "Message: " + message
                connection.sendall(send.encode('ascii'))

                # Ending game if either user guessed word or if they are out of body parts
                if "/q" in send:
                    print("Ending Game")
                    break


# CALLING MAIN
if __name__ == "__main__":
    main()
