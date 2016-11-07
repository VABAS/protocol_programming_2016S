#!/usr/bin/python

import socket,sys

args=sys.argv
script=args[0]
if len(args)<3:
	# If there is not enough arguments, exit with error
	sys.exit("Not enough arguments!\nUsage: "+script+" <address> <port>")
elif len(args)>3:
	print "More than two arguments detected. Only first two arguments parsed."
address=args[1]
# Verify, that port provided is integer
try:
	port=int(args[2])
except ValueError:
	sys.exit("'"+str(args[2])+"' is not valid port! You must provide integer for port value.")
try:
	# create socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# connect to server (in this case on the same machine)
	s.connect((address, port))
except socket.error as e:
	# Handle exceptions
	sys.exit("Could not connect to server: "+str(e))

try:
	# send "hello" to server
	s.send("hello world")
except socket.error as e:
	# Handle exceptions
	sys.exit("Could not send data to server: "+str(e))

# print whatever server sends back.
print s.recv(1024),

# close the socket and exit the program
s.close()
