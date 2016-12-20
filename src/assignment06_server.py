#!/usr/bin/python

# !!! NOTE !!!
# There is bug at file handling which occurs if it is emptied by hand after it 
# is created by server. Bug leads to creation of one empty-named task when 
# another task is created later. Task can be easily deleted with client 
# application and it's solved with that (file gets repaired with this 
# operation).

from threading import Thread
from time import sleep
from os.path import isfile
import socket
import sys

class TodoFile():
    # Class to handle the TODO-file and its locking during read/write
    # operations.
    def __init__(self, filePath):
        self.__releaseLock()
        self.filePath = filePath
        
    def __setLock(self):
        # "Private" method to handle te locking of file. If file is locked 
        # blocks until it's released and acquires lock again.
        while self.lock:
            sleep(1)
            
        self.lock = True
        
    def __releaseLock(self):
        # Method used to release the lock.
        self.lock = False
        
    def write(self, data):
        if len(data) <= 0:
            return False, "Item name not specified!"
            
        try:
            self.__setLock()
            # Opening file for reading and writing.
            fiile = open(self.filePath,"a+")
            insides = fiile.read()
            if len(insides) > 0:
                for line in insides.split("\n"):
                    if line == data:
                        fiile.close()
                        self.__releaseLock()
                        return False, "Item already exists!"
                if insides[len(insides)-1] != "\n" and len(insides) > 1:
                    data = "\n"+data
                
            fiile.write(data)
            fiile.close()
            self.__releaseLock()
            return True, "Task \""+data+"\" added succesfully"
        except Exception as e:
            return False, str(e)
        
    def read(self):
        try:
            self.__setLock()
            # Reading the todo-file to variable and replacing newline-characters
            # with vertical-bar-characters.
            fiile = open(self.filePath)
            insides = fiile.read().replace("\n\n","\n").replace("\n","|")
            # Close the file and release file-lock.
            fiile.close()
            self.__releaseLock()
            # If insides is empty there are no items in list.
            if len(insides) < 1:
                return False, "No items in list"
            # If last character is vertical bar, lets strip it out.
            while True:
                if insides[len(insides)-1] == "|":
                    insides = insides[:len(insides)-1]
                else:
                    break
            # Close the file and return success and the formatted listing of 
            # todo-items.
            return True, insides
        except Exception as e:
            # Release the file-lock.
            self.__releaseLock()
            return False, str(e)
        
    def deleteEntry(self, entry):
        if len(entry) <= 0:
            return False, "Index not specified!"
        
        try:
            entry = int(entry)
        except ValueError:
            return False, "Index must be integer!"
            
        try:
            self.__setLock()
            # Opening file for reading only first and splitting at newlines.
            fiile = open(self.filePath)
            insides = fiile.read().split("\n")
            if entry not in range(0, len(insides)):
                fiile.close()
                self.__releaseLock()
                return False, "Index out of range!"
            fiile.close()
            # Opening file for writing again and writing all but the one 
            # specified for deletion back.
            fiile = open(self.filePath, "w")
            i = 0
            while i < len(insides):
                if (i+1) != entry:
                    fiile.write(insides[i]+"\n")
                    
                i+=1
                 
            fiile.close()
            self.__releaseLock()
            return True, "Entry deleted succesfully"
        except Exception as e:
            return False, str(e)

def sendResponse(client, reqType, message):
    if reqType in ("ADD", "DONE"):
        respType = "SUCC"
    else:
        respType = reqType
    client.sendall(respType+" "+message+"\n")
    
def clientHandler(client, todo):
    # Handles one client request and returns.
    request=""
    # Loop to wait for complete message.
    while True:
        request=request+client.recv(1024)
        if len(request) >= 1:
            if request[len(request)-1] == "\n":
                break
    
    # Stripping the last character (should be newline).
    request = request[:len(request)-1]
    
    # Splitting the request at first and first only space-character.
    request = request.split(" ",1)
    if request[0] == "LIST":
        status, msg = todo.read()
    elif request[0] == "ADD":
        status, msg = todo.write(request[1])
    elif request[0] == "DONE":
        status, msg = todo.deleteEntry(request[1])
    else:
        status = False
        msg = "Command not implemented"
        
    if status:
        sendResponse(client, request[0], msg)
    else:
        sendResponse(client, "ERR", msg)

    client.close()

def main():
    arguments = sys.argv
    if len(arguments)<4:
        # Checking if there is enough arguments provided to start the server.
        sys.exit("Not enough arguments!\nUsage: "
                 +arguments[0]+
                 " [interface] [port] [todo file]")

    address = arguments[1]
    port = arguments[2]
    todoFile = arguments[3]
    if not isfile(todoFile):
        open(todoFile, "w").close()
        print "Todo-file created"
        
    try:
        # Try to convert port number to integer.
        port = int(port)
    except ValueError:
        sys.exit("Port number must be INTEGER!")
        
    todo = TodoFile(todoFile)
    # Starting the server.
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((address, port))
            server.listen(5)
            print "Bind succesfull"
            break
        except:
            print "Could not bind! Trying again after 5 seconds..."
            sleep(5)
    
    # Server main loop. Handles new connections and gives them to their own
    # threads for handling.
    while True:
        client, addr = server.accept()
        print "New connection from "+str(addr[0])+":"+str(addr[1])
        clientThread = Thread(
                target=clientHandler,
                args=[client, todo]
        )
        # Specify client threads as daemon thread so that they are killed as
        # well if the main-thread is killed.
        clientThread.daemon = True
        clientThread.start()
        
if __name__ == "__main__":
    main()

