# ############################################################################## #
# Assignment: HTTP Web Proxy Server                                              #
# Class: CS 4480 Computer Networks						 #						 
# Program: pa1_final.py 							 #						     
# By: xrawlinson							         #							
# Last Update Date: 2/21/2016							 #						
#										 #										
# A web proxy that is capable of accepting HTTP GET requests, forwarding the 	 #
# requests to remote (origin) servers, checking the responses from the servers   #
# to filter malware from reaching clients' systems, and returning the responses  #
# to the requested clients if not malware. 			                 #
# The proxy server can handle multiple clients' requests concurrently.           # 
# It allows HTTP/1.0 requests only, other version is not supported.              #         
# ############################################################################## #

import socket 
import sys
import re
import multiprocessing 
from hashlib import md5

# main()
def main():
	# calls the function proxy_server 
	proxy_server()	
# end of main()

# proxy_server sets up a connection from the client, and it calls the function handlesRequest 
def proxy_server():

	try:
		# port number needs to be specified from the command line, if not specified will use default: 8000
		if(len(sys.argv) > 2):
			print "Invalid input. Please enter one argument for a port number or none to use the default port number 8000."
			sys.exit(1)
		if(len(sys.argv) < 2):
			PORT = 8000
		else:
			PORT = int(sys.argv[1])

		# host 
		HOST = ''

		try:
			# creates a socket for the proxy server, use SOCK_STREAM for TCP 
			sock_for_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			## print 'Got a socket:', sock_for_proxy.fileno()       # <------ used for testing
			
			# uses the socket to bind the host and port
			sock_for_proxy.bind((HOST,PORT))
			## print 'Bound to:', sock_for_proxy.getsockname()	  # <------ used for testing
			
			# starts listening for connections
			sock_for_proxy.listen(1)

			print "Ready to connect!\n"

		except socket.error as details:
			# socket opened in error, closes it
			if sock_for_proxy:                      
				sock_for_proxy.close()
			# print the details, exits the program
			print "Issue opening socket: ", details
			sys.exit(1)

		# proxy server accepts connection from the client, calls the function handlesRequest
		while 1:
			conn_sock_for_proxy, client_addr = sock_for_proxy.accept()
			## print "conn_sock_for_proxy: ", conn_sock_for_proxy	# <------ used for testing
			print "CLIENT_ADDR: ", client_addr 		# <------ used for testing

			## handlesRequest(conn_sock_for_proxy, client_addr)		# <------ used for testing, this was for handling only one client at a time
			
			# handles multiple requests concurrently
			p = multiprocessing.Process(target=handlesRequest, args=(conn_sock_for_proxy, client_addr))
			
			print "BEFORE: ", p, p.is_alive() 	# <------ used for testing

			# start the thread
			p.start()
			
			print "DURING: ", p, p.is_alive()	# <------ used for testing		

		sock_for_proxy.close()
		sys.exit(1)	

	# if command line enters CTRL+C, prints a message to advise and exist	
	except KeyboardInterrupt:
		print "\nYou requested to close. Bye!"
		sys.exit(1)

	# after all done, terminate the process
	finally:
		for p in multiprocessing.active_children():
			p.terminate()
			p.join()
		print "Process is terminated."	
# end of proxy_server

# function handlesRequest receives the data from a client, put the data to the needed format for sending to the remote server,
# after receiving the returned data from the remote server, sends it back to the client who sends in the request if not malware
def handlesRequest(client_conn, client_addr):
	# request from the client will be saved to rqst_from_client
	rqst_from_client = ""

	# receiving action stops when sees "\r\n" followed by next line with only "\r\n"
	while 1:
		# receives requests from the client
		rcv = client_conn.recv(1024)
		
		# saves the received data
		rqst_from_client += rcv

		# if find new line and "User-Agent" (for browser)
		new_line = rcv.find("\r\n")
		user_agent = rcv.find("User-Agent")

		# if "User-Agent" is not found to check if the request was from a browser, check if ends with new line
		if(user_agent == -1):
			if(new_line == 0):
				## print"relative url" # <------ used for testing
				break
		# if the request was from a browser
		else:
			## print "firefox"	# <------ used for testing
			break		

	print "Got from client: ", rqst_from_client		# <------ used for testing

	# splits the received data to chunks based on new lines
	splitted_data = rqst_from_client.split("\r\n")
	
	## print "splitted data: ", splitted_data		# <------ used for testing
	## print "length of splitted data: ", len(splitted_data)		# <------ used for testing

	# first line 
	first_line = splitted_data[0]
	# checks the first header, it should be <Method> <URL> <HTTP Version> 
	correct_first_line_header = re.findall("^[A-Z]{3,} (https?:\/\/)?(([\da-z\.-]+)\.([a-z\.]{2,6}))*([\/\w \.-~]*)\/? HTTP\/1.0|1.1$", first_line)
	
	# if the first line HTTP header is invalid, sends a message back to the client
	if(not correct_first_line_header): 
		## print "Incorrect HTTP Header(s).\n"		# <------ used for testing
		client_conn.sendall("400 Bad Request.\n")
		client_conn.close()
	else:
		# splits the first line to pieces base on spaces
		splitted_from_first_line = first_line.split(' ')

		# extracts the method from the firstline, which is the first element
		method = splitted_from_first_line[0]
		
		# extracts the HTTP version from the firstline, which is the third element
		http_version = splitted_from_first_line[2]
		# we use HTTP 1.0 per assignment's requirement
		if (http_version != "HTTP/1.0"):
			http_version = "HTTP/1.0"

		# check if first line contains ://
		if_contains_it = first_line.find("://") 
		
		# if method is GET, handles as either relative url or absolute url
		if method != "GET":
			## print "501 Not Implemented\n"	# <------ used for testing
			client_conn.sendall("501 Not Implemented\n")
			client_conn.close()
		else:
			# checks the second header, it should be Host: ... 
			correct_secline_header = re.findall("^Host: .*$", splitted_data[1])
			
			# if relative url but second header line is invalid (not blank)
			if(not correct_secline_header and splitted_data[1] != ""):
				## print "Incorrect HTTP Header(s).\n"		# <------ used for testing
				client_conn.sendall("400 Bad Request.\n")
				client_conn.close()
			# if currect header, finds the url
			else: 
				if (if_contains_it  == -1 and len(splitted_data) != 3):
					second_line = splitted_data[1]
					url = second_line[6:]								
				else:
					# extracts the url from the firstline, which is the second element
					url = splitted_from_first_line[1]

				# takes out http:// if it exists
				with_http = url.find("://")
				if (with_http == -1):
					after_takes_out_front = url[:]
				else:
					after_takes_out_front = url[7: ]

				# if the port number is given, it would have : in front of it
				port_given = after_takes_out_front.find(":")

				# finds the first "/" to find the host and the rest that is after the host, 
				# here finds rest_of_data, a little below will find host_after_take_out_end that is the host
				finds_first_slash = after_takes_out_front.find('/')
				rest_of_data = after_takes_out_front[finds_first_slash: ]

				# initialize port number to -1
				port_num = -1

				# if no port number being specified in the request, use 80
				if (port_given == -1):
					port_num = 80
					if (if_contains_it  == -1 and len(splitted_data) != 3):
						# find the host for relative url
						host_after_take_out_end = after_takes_out_front[:]
					else:
						# find the host for absolute url
						host_after_take_out_end = after_takes_out_front[ : finds_first_slash]
				# if port is specified, use the given port number
				else:
					if (if_contains_it  == -1 and len(splitted_data) != 3):
						port_num = after_takes_out_front[(port_given+1) : ]
					else:
						port_num = after_takes_out_front[(port_given+1) : finds_first_slash]
					# find the host
					host_after_take_out_end = after_takes_out_front[ : port_given] 

					##print "Port Number: ", port_num		# <------ used for testing

				# stores the remaining header 
				remaining_header = ""

				if(len(splitted_data) != 3):				
					# check the rest of headers to ensure correct format: <Header Name>: <Header Value>
					for s in splitted_data[2:(len(splitted_data))]:
						correct_rest_of_headers = re.findall("^([A-Z](\w*-*)*: .*)*$", s)
						if(not correct_rest_of_headers):
							## print "Incorrect HTTP Header(s).\n"		# <------ used for testing
							client_conn.sendall("400 Bad Request.\n")
							client_conn.close()
							return
						# if currect header, put it in the remaining_header
						else: 
							remaining_header += str(s) + "\r\n"	

						# if from command line, only GET ... and Host: ... are provided
						if(len(splitted_data) == 4):
							rqst_to_real_server = splitted_data[0] + "\r\nHost: "+ host_after_take_out_end + "\r\nConnection: close\r\n" + "\r\n"
						else:
							# when use telnet or firefox:
							# replaces "Connection: keep-alive" with "Connection: close"
							remaining_header = remaining_header.replace("Connection: keep-alive", "Connection: close")
							rqst_to_real_server = method + " " + rest_of_data + " " + http_version + "\r\nHost: "+ host_after_take_out_end + "\r\n" + remaining_header + "\r\n" + "\r\n"
								
							# when use curl:
							# replaces "Proxy-Connection: Keep-Alive" with "Proxy-Connection: Close"
							remaining_header = remaining_header.replace("Proxy-Connection: Keep-Alive", "Proxy-Connection: Close")
							rqst_to_real_server = method + " " + rest_of_data + " " + http_version + "\r\nHost: "+ host_after_take_out_end + "\r\n" + remaining_header + "\r\n" + "\r\n"
				else:
					# request that to be sent to the real server
					rqst_to_real_server = method + " " + rest_of_data + " " + http_version + "\r\nHost: " + host_after_take_out_end + "\r\nConnection: close\r\n" + "\r\n"   	
			
				# below socket handles that part of passing the request through to the original(real) server
				# and then passing the server's response to the client
				try:
					# creates a socket, use SOCK_STREAM for TCP 
					sock_for_real_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					## print 'Bound to socket for server: (after socket call)', sock_for_real_server.getsockname()         # <------ used for testing

					# connect the host and port number
					sock_for_real_server.connect((host_after_take_out_end,int(port_num)))
					
					## sock_for_real_server.connect(('127.0.0.1',7890))				# <------ used for testing
					## print "HOST: ", host_after_take_out_end						# <------ used for testing
					## print 'Bound to socket for server: (after connect call)', sock_for_real_server.getsockname() 		 # <------ used for testing
					print "Sending to server: ", rqst_to_real_server				# <------ used for testing

					# send all the data that was received from the client to the real server
					sock_for_real_server.sendall(rqst_to_real_server)
					host_after_take_out_end = ""

					# buffer to store data being received from the real server
					receive_from_server = ""
					while 1:
						recv = sock_for_real_server.recv(1024)
						
						# if no more data to be received, break the while loop
						if not recv:
							break
						else:
							receive_from_server += recv

					# if the response is not empty
					if(len(receive_from_server)>0):

						# split the data that was received from the server based on first doubled new lines
						split_data_from_server = receive_from_server.split("\r\n\r\n", 1)

						# when correct-formatted but invalid port number or host info being provided by a client, 
						# proxy couldn't telll so would still have sent to server, then server would return an error
						error = re.findall(".*404 Not Found|400 Bad Request.*", split_data_from_server[0])
						if(error):
							client_conn.sendall("400 Bad Request.\n")
							client_conn.close()
							return

						# stores the actual object that will be hashed, received data minus headers
						obj = ""
						for data in split_data_from_server[1:]:
							obj += data

						# covert to MD5 hash by calling covertMD5
						converted_data = convertMD5(obj)

						print "MD5 HASH: ", converted_data	# <------ used for testing

						## if(notMalware("a8ef5ccebd2e3babdd243a2861673c26")):		# <------ used for testing

						# if not malware, sends everything received from the real server to the client
						if (notMalware(converted_data)):					
							client_conn.sendall(receive_from_server)
						# else send a normal 200 OK HTTP response message with a simple HTML page to advise the issue
						else:
							client_conn.sendall(split_data_from_server[0])
							# user triple quotation marks for HTML
							client_conn.sendall("""\n\n<!DOCTYPE html>\n<html>\n<body>\n\n<h1>The content is blocked because it is suspected of containing malware.</h1>\n\n</body>\n</html>\n\n""")

					# done with everything, closes the sockets
					sock_for_real_server.close()
					client_conn.close()

					##time.sleep(1)		# <------ used for testing

					print "DONE!"	

				except socket.error as details:
					# sockets opened in error, closes them
					if sock_for_real_server:
						sock_for_real_server.close()
					if client_conn:
						client_conn.close()
					# print the details, exits the program
					print "Resetting: ", details
					sys.exit(0)
# end of handlesRequest

# convert the received object to MD5 hash
def convertMD5(revObj):
  m = md5()
  m.update(revObj)
  return m.hexdigest()
# end of convertMD5

# return true if not a malware, otherwise, return false
def notMalware(receivedFromServer):
	try:
		# creates a socket, use SOCK_STREAM for TCP 
		socket_to_send_to_cymru = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# connects to cymru
		socket_to_send_to_cymru.connect(('hash.cymru.com',43))

		# send hash to cymru
		socket_to_send_to_cymru.sendall("begin\n\n"+receivedFromServer+"\nend\n")		

		# stores data received from Cymru
		rec_from_cymru = ""

		while 1:
			# receive response from Cymru
			rc = socket_to_send_to_cymru.recv(1024)	
			# if no more data to be received, break the while loop
			if not re:
				break
			else:
				rec_from_cymru += rc

			if(len(rec_from_cymru)>0):
				print "Recevied FROM Cymru: ",rec_from_cymru		# <------ used for testing

				# split the response from cymru based on new line
				split_rspns_from_cymru = rec_from_cymru.split("\r\n")

				# only need the last piece of the response
				## last_piece = split_rspns_from_cymru[2]		# <------ used for testing
				last_piece = split_rspns_from_cymru[-1].strip()
			
				# check the returned message from Cymru, if the last element says "NO_DATA" then not malware
				split_last_piece = last_piece.split(' ')
				## if(split_last_piece[2] == "NO_DATA"):	# <------ used for testing
				if(split_last_piece[-1] == "NO_DATA"):
					return True
				else:
					return False							
					
	except socket.error as details:
		# sockets opened in error, closes them
		if socket_to_send_to_cymru:
			socket_to_send_to_cymru.close()
		# print the details, exits the program
		print "Resetting: ", details
		sys.exit(0)		
# end of function notMarware

if __name__ == '__main__':
    main()





