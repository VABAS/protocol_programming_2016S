#!/usr/bin/python

'''
This is the server component for imlementation of SimFTP-protocol
Edit settings below to customize server for your environment
'''

import socket,sys,os,time,hashlib,mimetypes

# Start of settings
addr="localhost"
port=8888
server_root='files'
list_announcement="Listing of files at server files.example.com"
# End of settings

# Start of function definitions
def strip_slashes(to_strip):
	# Removes duplicate slashes from input and returns it
	to_strip=to_strip.split("/")
	final=""
	for step in to_strip:
		if step != "":
			final+="/"+step
	return final
def directory_traversal(data):
	# Checks for directory traversal attempt
	# Returns True if directory traversal was detected
	data=strip_slashes(data).split("/")
	if ".." in data:
		return True
	else:
		return False
def send_response(client,header,response):
	# Sends response as defined by specification
	client.sendall(header+"\n\n"+response)
def parse_request(client):
	# Parses request received from client
	# Returns tuple consisting of header and data
	# Header returned is dict
	request=""
	# Loop to wait for complete message
	while True:
		request=request+client.recv(1024)
		request_split=request.split("\n\n",1)
		# Check if header is received
		if len(request_split)==2:
			# If so, check if all is received
			if len(request_split[1])==int(request_split[0].split("\n")[1].split(":")[1]):
				request=request_split[1]
				# Break if all is received
				break
	header={}
	for line in request_split[0].split("\n"):
		header[line.split(":")[0]]=line.split(":")[1]
	data=request_split[1]
	return header,data
def generate_error(err):
	# Generated ERR type response
	# Returns tuple with header and data
	errors={
		"ENDNOTEXPECTED":"REQMALFORMED\nENDNOTEXPECTED",
		"HEADER_MALFORMED":"REQMALFORMED\nUNKNOWN",
		"FILENOTFOUND":"FILE\nNOTFOUND",
		"FILENOTDOWNLOADABLE":"FILE\nNOTDOWNLOADABLE",
		"FILEISDIR":"FILE\nISDIRECTORY",
		"FILENOTDIR":"FILE\nNOTDIRECTORY",
		"FILEPERM":"FILE\nPERMISSIONS",
		"FILEUNKNOWN":"FILE\nUNKNOWN",
		"UNKNOWN":"ERR\nUNKNOWN"
	}
	if err in errors:
		data=errors[err]+"\n"+err
	else:
		data=errors["UNKNOWN"]+"\n"+err
	header="TYPE:ERR\nDLEN:"+str(len(data))
	return header,data
def generate_list_response(data):
	# Generated LIST type response
	# Returns tuple with header and data
	# Lets prevent directory traversal
	if directory_traversal(data):
		print "Directory traversal detected! Details: "+data
		return generate_error("FILENOTFOUND")
	list_formatted=""
	try:
		listing=os.listdir(server_root+data)
	except OSError as e:
		print e
		if e.errno==2:
			return generate_error("FILENOTFOUND")
		elif e.errno==13:
			return generate_error("FILEPERM")
		elif e.errno==20:
			return generate_error("FILENOTDIR")
		else:
			return generate_error("FILEUNKNOWN")
	for item in listing:
		fpath=server_root+data+"/"+item
		if os.path.isdir(fpath):
			list_formatted+="\nD"+item
		elif os.path.isfile(fpath):
			list_formatted+="\nF"+item+"/"+str(os.path.getsize(fpath))
	dir_path=data
	data=list_announcement+"\n"+dir_path+"\n"+list_formatted[1:]
	header="TYPE:LIST\nDLEN:"+str(len(data))
	return header,data
def generate_file_response(data):
	# Generated FILE type response
	# Returns tuple with header and data
	# Lets prevent directory traversal
	if directory_traversal(data):
		print "Directory traversal detected! Details: "+data
		return generate_error("FILENOTFOUND")
	# Get file name
	fname=data.split("/")[len(data.split("/"))-1]
	mime=mimetypes.MimeTypes()
	fmime=mime.guess_type(data)[0]
	try:	
		data=open(server_root+data).read()
	except IOError as e:
		print e
		if e.errno==2:
			return generate_error("FILENOTFOUND")
		elif e.errno==13:
			return generate_error("FILEPERM")
		elif e.errno==21:
			return generate_error("FILEISDIR")
		else:
			return generate_error("FILEUNKNOWN")
	header="TYPE:FILE\nDLEN:"+str(len(data))+"\nFNAME:"+str(fname)+"\nFSHAS:"+hashlib.sha512(data).hexdigest().upper()+"\nFMIME:"+fmime
	return header,data
# End of function definitions
# Start of Exception class definitions
class RootDirNotReadable(Exception):
	pass

# End of Exception class definitions
# Main program starts here
# Trying if server root is readable
try:
	os.listdir(server_root)
except OSError as e:
	raise RootDirNotReadable(e)
print "Server root set to "+server_root
# create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to an address and port
print "Trying to bind..."
i=1
while True:
	try:
		sock.bind((addr, port))
		break
	except:
		i+=1
		if i in (10,20,30,40,50,100,200,300,400,500,600,700,800,900):
			print "Bind has failed "+str(i)+" times!"
		elif i>=1000:
			sys.exit("Could not bind!")
		time.sleep(1)
print "Bind succeeded, "+str(i)+" attempts made"
		
# start listening for new connections
sock.listen(5)
print "Listening at "+addr+":"+str(port)
# Main loop
while True:
	(client,addr)=sock.accept()
	print "Received a connection from "+str(addr[0])+":"+str(addr[1])
	(header,data)=parse_request(client)
	try:
		if header['TYPE']=="LIST":
			(header,data)=generate_list_response(data)
			send_response(client,header,data)
		elif header['TYPE']=="DOWNLOAD":
			(header,data)=generate_file_response(data)
			send_response(client,header,data)
		else:
			(header,data)=generate_error("TYPE_NOTIMPLEMENTED")
			send_response(client,header,data)
	except KeyError:
		(header,data)=generate_error("HEADER_MALFORMED")
		send_response(client,header,data)
