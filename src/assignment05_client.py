#!/usr/bin/python

'''
This is the client component for imlementation of SimFTP-protocol
Options for this client must be provided with command line parameters
Usage of this script is for example:
 ./client.py <server> <port> <LIST|DOWNLOAD> <path>
where
 <server> means the (ip)address of the server
 <port> means the port in which the server listens for connections
 <LIST|DOWNLOAD> means the command (request-type) to issue for server (either LIST or DOWNLOAD)
 <path> means the path to directory to LIST or file to DOWNLOAD

Additionally for DOWNLOAD to work correctly you must se the dl_root variable below to point into
folder you want the downloaded files to be saved. You must have write permissions to folder in 
question. 
'''


import socket,sys,hashlib,os
#Start of settings
dl_root="dls"
#End of settings

# Request and response types implemented as well with error-messages
request_types=(
	"LIST",
	"DOWNLOAD",
)
response_types=(
	"ERR",
	"LIST",
	"FILE",
)
error_messages={
	"REQMALFORMED":{
		"ENDNOTEXPECTED":"Server reported that request ended unexpectedly",
		"UNKNOWN":"Server reported that request for malformed",
	},
	"FILE":{
		"NOTFOUND":"File or directory you were trying to access was not found",
		"NOTDOWNLOADABLE":"File is not downloadable",
		"ISDIRECTORY":"File you were trying to DOWNLOAD was directory",
		"PERMISSIONS":"Permission error occured when trying to access the file or directory",
		"UNKNOWN":"Unknown error at file access",
	},
	"ERR":{
		"UNKNOWN":"Unknown error has happened at server",
	}
}
# Start of exception class definitions
class CommandNotImplemented(Exception):
	pass
# End of exception class definitions
# Start of function definitions
def send_request(server,port,req_type,data):
	# Sends request to server and returns response-type, -headers and -data as tuple
	# Must be provided with servers address and port along with request type and data to send
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((server,port))
	except socket.error as e:
		sys.exit("Could not connect to server: "+str(e))
	if req_type in request_types:
		request="TYPE:"+req_type+"\nDLEN:"+str(len(data))+"\n\n"+data
	else:
		raise CommandNotImplemented(req_type)
	s.sendall(request)
	response=""
	while True:
		response=response+s.recv(1024)
		# Check if header is received
		if len(response.split("\n\n",1))==2:
			resp_headers=response.split("\n\n",1)[0].split("\n")
			resp_type=resp_headers[0].split(":")[1]
			resp_len=int(resp_headers[1].split(":")[1])
			resp_data=response.split("\n\n",1)[1]
			# If so, check if all is received
			if len(resp_data)==resp_len:
				s.close()
				headers={}
				for header in resp_headers[2:]:
					headers[header.split(":")[0]]=header.split(":")[1]
				return (resp_type,headers,resp_data)
# End of function definitions
arguments=sys.argv
# Print error and exit if parameter count if invalid
if len(arguments)!=5:
	sys.exit("Wrong number of parameters provided!\nUsage: "+arguments[0]+" <server> <port> <LIST|DOWNLOAD> <path>")
server_addr=arguments[1]
try:
	server_port=int(arguments[2])
except ValueError:
	sys.exit("Invalid port \""+arguments[2]+"\" supplied!")
command=arguments[3].upper()
if command not in request_types:
	sys.exit("Unimplemented command \""+command+"\" supplied!")
path=arguments[4]
# Get response
resp_type,resp_headers,data=send_request(server_addr,server_port,command,path)
if resp_type not in response_types:
	# Check that we reseived response we are able to handle, exit if not
	sys.exit("Server returned invalid response!")
if resp_type=="ERR":
	# Handle ERR-response
	err_group=data.split("\n",3)[0]
	err_specifier=data.split("\n",3)[1]
	# If we have error message in our error_messages dict lets print it
	# Otherwise we print the "ERR_UNKNOWN" error
	try:
		print error_messages[err_group][err_specifier]
	except IndexError:
		print error_messages["ERR"]["UNKNOWN"]
elif resp_type=="LIST":
	# Handle LIST-response
	directories=[]
	files=[]
	announcement=data.split("\n")[0]
	# Go through the data section and sort files and directories into their own lists
	# File list contains list of lists of filenames and file sizes
	for item in data.split("\n")[2:]:
		if item[0]=="D":
			directories.append(item[1:].split("/")[0])
		elif item[0]=="F":
			fname=item[1:].split("/")[0]
			try:
				fsize=int(item[1:].split("/")[1])
			except IndexError:
				fsize="!"
			except ValueError:
				fsize="!"
			files.append((fname,fsize))
	# Print listing announcement
	print announcement
	# List directories first
	for directory in directories:
		print "\t"+directory+"/"
	# Then lets list files
	for f in files:
		print "\t"+f[0]+" ; Size: "+str(f[1])+"B"
elif resp_type=="FILE":
	file_path=dl_root+"/"+resp_headers["FNAME"]
	# Lets guess the hash used by server from the length of hexidigest
	# This is possible, becouse protocol allows only SHA-family hashes
	if len(resp_headers["FSHAS"])==128:
		hashtype="SHA512"
		fshas=lambda x: hashlib.sha512(x).hexdigest().upper()
	elif len(resp_headers["FSHAS"])==96:
		hashtype="SHA384"
		fshas=lambda x: hashlib.sha384(x).hexdigest().upper()
	elif len(resp_headers["FSHAS"])==64:
		hashtype="SHA256"
		fshas=lambda x: hashlib.sha256(x).hexdigest().upper()
	elif len(resp_headers["FSHAS"])==56:
		hashtype="SHA224"
		fshas=lambda x: hashlib.sha224(x).hexdigest().upper()
	elif len(resp_headers["FSHAS"])==40:
		hashtype="SHA1"
		fshas=lambda x: hashlib.sha1(x).hexdigest().upper()
	# Check if hash from header matches the one computed locally
	if fshas(data)==resp_headers["FSHAS"].upper():
		print hashtype+" hash of the file matches the one provided by server."
	else:
		print hashtype+" hash of the file doesn't match the one provided by server!"
	# Check if file exists and ask confirmation before overwriting
	# Exit if user doesn't want to overwrite
	if os.path.isfile(file_path):
		while True:
			answer=raw_input('File already exists do you want to overwrite it? [Y/n] ').upper()
			if answer in ("Y","N"):
				break
			print "Invalid answer!"
		if answer=="N":
			sys.exit("Could not save file! File already exists.")
	# Write the file to download-path
	f=open(file_path,"w")
	f.write(data)
	print "File succesfully saved to "+file_path
