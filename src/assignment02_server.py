#!/usr/bin/python

import socket

def main():
	# create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# bind the socket to an address and port
	sock.bind(("localhost", 8888))
	# start listening for new connections
	sock.listen(5)
	# wait for a client using accept()
	# accept() returns a client socket and the address from which
	# the client connected
	(client, addr) = sock.accept()
	print "Received a connection from", addr
	# read and print whatever the client sends us
	viesti=""
	while True:
		viesti=viesti+client.recv(1024)
		# Split at first, and first only, |-character (vertical-bar) occurence
		viesti_split=viesti.split("|",1)
		# Check if header is received
		if len(viesti_split)==2:
			# If so, check if all is received
			if len(viesti_split[1])==int(viesti_split[0]):
				viesti=viesti_split[1]
				# Break if all is received
				break
	print viesti
	# send "hello world!" back to the client
	msg="hello world! (from server :)"
	# Adding header (msg length+|)
	msg=str(len(msg))+"|"+msg
	len_send=0
	# Call client.send() until all is send
	while len_send<len(msg):
		len_send += client.send(msg[len_send:])
	# the server proram terminates after sending the reply
	sock.close()

if __name__ == "__main__":
	main()

