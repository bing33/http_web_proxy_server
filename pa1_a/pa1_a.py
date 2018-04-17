# ############################################################################## #
# Assignment: HTTP Web Proxy Server                                              #
# Class: CS 4480 Computer Networks						 #
# Program: pa1_b.py 								 #
# By: xrawlinson								 #
# Last Update Date: 2/7/2016							 #
#										 #
# A web proxy that is capable of accepting HTTP GET requests, forwarding the 	 #
# requests to remote (origin) servers, and returning response data to a client.  #
# The proxy server can handle up to 100 clients' rquests concurrently.           #
# ############################################################################## #

import socket 
import sys
import re

# main()
def main():
	proxy_server()
# end of main()

# proxy_server sets up a connection from the client, and it calls the function handlesRequest 
def proxy_server():

	try:
		# port number needs to be specified from the command line, if not specified will use default: 8000
		if(len(sys.argv) > 2):
			print "Invalid input. Please enter one argument for a port number or none to use the default port number."
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
			print 'Got a socket:', sock_for_proxy.fileno()       # <------ used for testing
			
			# uses the socket to bind the host and port
			sock_for_proxy.bind((HOST,PORT))
			print 'Bound to:', sock_for_proxy.getsockname()	  # <------ used for testing
			
			# starts listening for connections
			sock_for_proxy.listen(1)

			print "Ready to connect!"

		except socket.error as details:
			# socket opened in error, closes it
			if sock_for_proxy:                      
				sock_for_proxy.close()
			# print the details, exits the program
			print "Issue opening socket: ", details
			sys.exit(1)

		# proxy server accepts connection from the client, calls the function handlesRequest
		while(1):
			conn_sock_for_proxy, client_addr = sock_for_proxy.accept()
			print "conn_sock_for_proxy: ", conn_sock_for_proxy
			print "client_addr: ", client_addr

			# first part of the assignment only requires one client:
			handlesRequest(conn_sock_for_proxy, client_addr)

		sock_for_proxy.close()
		sys.exit(1)

	# if command line enters CTRL+C, prints a message to advise and exist	
	except KeyboardInterrupt:
		print "\nYou requested to close. Bye!"
		sys.exit(1)
# end of proxy_server

# function handlesRequest receives the data from a client, put the data to the needed format for sending to the remote server,
# after receiving the returned data from the remote server, sends it back to the client who sends in the request
def handlesRequest(client_conn, client_addr):   
	# request from the client will be saved to rqst_from_client
	rqst_from_client = ""

	# receiving action stops when sees "\r\n" followed by next line with only "\r\n"
	while(1):
		# receives requests from the client
		rcv = client_conn.recv(1024)
		## print "Got from client: ", rcv 	# <------ used for testing
		
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
		# if the request was from command line
		else:
			## print "firefox"	# <------ used for testing
			break		

	print "Got from client: ", rqst_from_client

	# splits the received data to pieces base on new lines
	splitted_data = rqst_from_client.split("\r\n")
	
	## print "splitted data: ", splitted_data		# <------ used for testing
	## print "length of splitted data: ", len(splitted_data)		# <------ used for testing

	# first line 
	first_line = splitted_data[0]
	correct_first_line_header = re.findall("^[A-Z]{3,} (https?:\/\/)?(([\da-z\.-]+)\.([a-z\.]{2,6}))*([\/\w \.-~]*)\/? HTTP\/1.0$", first_line)
	
	if(not correct_first_line_header): 
		print "Incorrect HTTP Header(s).\n"
		client_conn.sendall("Incorrect HTTP Header(s).\n")
		client_conn.close()
	else:
	
		## print "first line: ", first_line  		# <------ used for testing

		# splits the first line to pieces base on spaces
		splitted_from_first_line = first_line.split(' ')

		# extracts the method from the firstline, which is the first element
		method = splitted_from_first_line[0]
		
		http_version = splitted_from_first_line[2]

		# check if first line contains ://
		if_contains_it = first_line.find("://") 
		
		# if method is GET, handles as either relative url or absolute url
		if method != "GET":
			print "501 Not Implemented\n"
			client_conn.sendall("501 Not Implemented\n")
			client_conn.close()
		else:
			# checks the second header, it should be Host: ... if not, prints a message
			correct_secline_header = re.findall("^Host: .*$", splitted_data[1])
			if(not correct_secline_header and splitted_data[1] != ""):
				print "Incorrect HTTP Header(s).\n"
				client_conn.sendall("Incorrect HTTP Header(s).\n")
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
					##print "HHHHHHL ", host_after_take_out_end		# <------ used for testing
					##print "Port Number: ", port_num		# <------ used for testing

				# stores the remaining header 
				remaining_header = ""

				##close = False

				if(len(splitted_data) != 3):
					##print "here!!!!!!!! ", len(splitted_data)
					
					for s in splitted_data[2:(len(splitted_data))]:
						# checks the rest of headers, if wrong format, prints an error and close the connection
						##print "s, ***************, ", s 		# <------ used for testing

						##correct_rest_header = re.findall("^(([A-Z][\w\-\/]*)+:? ?.*)*$", s)
						##if(not correct_rest_header and len(splitted_data) != 3):
							##print "Incorrect HTTP Header(s).\n"
							##client_conn.sendall("Incorrect HTTP Header(s).\n")
							##close = True
							##break
						##else: 
						remaining_header += str(s) + "\r\n"	
					##if(close == True):	
						##client_conn.close()	

					# if from command line, only GET ... and Host: ... are provided
					if(len(splitted_data) == 4):
						rqst_to_real_server = splitted_data[0] + "\r\nHost: "+ host_after_take_out_end + "\r\nConnection: close\r\n" + "\r\n"
					else:
						# replaces "Connection: keep-alive" with "Connection: close"
						remaining_header = remaining_header.replace("Connection: keep-alive", "Connection: close")
						rqst_to_real_server = method + " " + rest_of_data + " " + http_version + "\r\nHost: "+ host_after_take_out_end + "\r\n" + remaining_header + "\r\n" + "\r\n"
				else:
					# request that to be sent to the real server
					rqst_to_real_server = method + " " + rest_of_data + " " + http_version + "\r\nHost: " + host_after_take_out_end + "\r\nConnection: close\r\n" + "\r\n"   	
			
				# below socket handles that part of passing the request through to the original(real) server
				# and then passing the server's response to the client
				try:
					# creates a socket, use SOCK_STREAM for TCP 
					sock_for_real_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					# print 'Bound to socket for server: (after socket call)', sock_for_real_server.getsockname()         # <------ used for testing

					# connect the host and port number
					sock_for_real_server.connect((host_after_take_out_end,int(port_num)))
					#print int(port_num), "HEHHHHHH"
					#sock_for_real_server.connect(('127.0.0.1',5001))				# <------ used for testing

					# print "HOST: ", host_after_take_out_end						# <------ used for testing
					# print 'Bound to socket for server: (after connect call)', sock_for_real_server.getsockname() 		 # <------ used for testing

					print "Sending to server: ", rqst_to_real_server				# <------ used for testing

					# send all the data that was received from the client to the real server
					sock_for_real_server.sendall(rqst_to_real_server)
					host_after_take_out_end = ""

					# receives server's response and sends it to client if the response is not empty
					while 1:
						receive_from_server = sock_for_real_server.recv(1024)
						# print "Got from server: ", receive_from_server
						if(len(receive_from_server)>0):								# <------ used for testing
							print "Sending to client: ", receive_from_server		# <------ used for testing
							client_conn.sendall(receive_from_server)
						else:
							break
					# done with everything, closes the sockets
					sock_for_real_server.close()
					client_conn.close()
					print "DONE!"

				except socket.error as details:
					# sockets opened in error, closes them
					if sock_for_real_server:
						sock_for_real_server.close()
					if client_conn:
						client_conn.close()
					# print the details, exits the program
					print "Resetting: ", details
					sys.exit(1)
# end of handlesRequest

if __name__ == '__main__':
    main()





