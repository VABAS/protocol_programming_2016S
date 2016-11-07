#!/usr/bin/python
import socket
def send_all(soc,data):
	msg=data
	len_sent=0
	while len_sent<len(msg):
		len_sent += soc.send(msg[len_sent:])
