#!/usr/bin/python

import socket

# create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server (in this case on the same machine)
s.connect(("localhost", 8888))

# send "hello" to server
msg="hello world! (from client :)"
# Adding header (msg length+|)
msg=str(len(msg))+"|"+msg
len_send=0
# Call s.send() until all is send
while len_send<len(msg):
	len_send += s.send(msg[len_send:])
	# print whatever server sends back.
	viesti=""
	while True:
		viesti=viesti+s.recv(1024)
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

# close the socket and exit the program
s.close()

