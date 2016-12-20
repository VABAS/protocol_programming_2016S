#!/usr/bin/python

import socket
import sys

def main():
    arguments = sys.argv
    commands=(
        "LIST",
        "DONE",
        "ADD"
    )
    additional=""
    if len(arguments) < 4:
        sys.exit("Not enough arguments!\nUsage: "
                +arguments[0]+
                "[server] [port] [command] [additional argument]")
                
    elif len(arguments) >= 5:
        additional = " ".join(arguments[4:])
        
    command = arguments[3].upper()
    if command not in commands:  
        sys.exit("Invalid command supplied!")
        
    if command in commands[1:] and len(additional) < 1:
        sys.exit("Additional parameter needed!")
        
    serverAddress = arguments[1]
    serverPort = arguments[2]

    try:    
        serverPort = int(serverPort)
    except TypeError:
        sys.exit("Port must be integer!")

    # Creating connection and trying to connect to server provided.
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Trying to connect to server specified.
        connection.connect((serverAddress, serverPort))
        # Setting connection timeout of sixty seconds.
        connection.settimeout(60)
    except socket.error as e:
        sys.exit("Could not connect to server: "+str(e))

    # Formatting the request.
    request = command    
    if command != "LIST":   
        request += " "+additional

    request += "\n"

    # Sending request to the server.
    connection.sendall(request)
    # Receiving server responce
    response=""
    # Loop to wait for complete message.
    while True:
        response=response+connection.recv(1024)
        if len(response) >= 1:
            if response[len(response)-1] == "\n":
                break

    # Stripping the last character (should be newline) and splitting at first 
    # space-character.
    response = response[:len(response)-1].split(" ", 1)
    if response[0] == "LIST":
        response[1] = response[1].split("|")
        print "Listing of TODO-items at server:"
        i = 1
        for item in response[1]:
          print "  "+str(i)+") "+item
          i+=1
    elif response[0] == "SUCC":
        print "Server reported that operation was succesfull."
        if len(response) >= 2:
            print "Additional information: "+response[1]
    elif response[0] == "ERR":
        print "Server responded with error \""+response[1]+"\""
    else:
        print "Server sent an unimplemented response of type "+str(response[0])
    
if __name__ == "__main__":
    main()

