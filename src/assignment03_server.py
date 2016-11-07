#!/usr/bin/python

import socket,sys

def main():
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
	# create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# bind the socket to an address and port
	sock.bind((address, port))
	# start listening for new connections
	sock.listen(5)
	# Start main loop that runs 'forever'
	while True:
		# wait for a client using accept()
		# accept() returns a client socket and the address from which
		# the client connected
		(client, addr) = sock.accept()
		print "Received a connection from", addr
		# read and print whatever the client sends us
		print client.recv(1024)
		# send "hello world!" back to the client
		client.send("hello world!\n")

if __name__ == "__main__":
	main()
