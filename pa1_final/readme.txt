# ############################################################################## #
# Assignment: HTTP Web Proxy Server                                              #
# Class: CS 4480 Computer Networks						 #
# Program: readme.txt for pa1_final.py						 #
# By: xrawlinson							         #
# Last Update Date: 2/21/2016							 #
#										 #
# A web proxy that is capable of accepting HTTP GET requests, forwarding the 	 #
# requests to remote (origin) servers, checking the responses from the servers   #
# to filter malware from reaching clients' systems, and returning the responses  #
# to the requested clients if not malware. 					 #
# The proxy server can handle multiple clients' requests concurrently. 	         # 
# It allows HTTP/1.0 requests only, other version is not supported. 	         #         
# ############################################################################## #

This is the final stage of the program.


***** An example of testing malware filtering, in Command Line *****

1. telnet localhost 8000 (note: port # can change depends on the port number chosen for the proxy server)
2. GET localhost:7890/f1/test1.rtf HTTP/1.0 (note: on port 7890 I have a SimpleHTTPServer set up, f1 is a folder, test1.rtf is a file stored in the folder and it will be checked if containing malware)

******************************************************************************************

* To run the proxy server in command line, you can do the following: 

1. python pa1_b.py
	
   Note: this option will use the default port 8000

2. python pa1_b.py port#

   Note: this option will use the port number that you specify, eg: python pa1_b.py 6789

* To test the connection to the proxy server from firefox, please set the port number accordingly


* In firefox, it works for both: 

1. http://www.cs.utah.edu:80/~kobus/simple.html 
2. http://www.cs.utah.edu/~kobus/simple.html 

* With telnet, it works for both absolute url and relative url: 

1. GET http://www.cs.utah.edu/~kobus/simple.html HTTP/1.0
2. GET http://www.cs.utah.edu:80/~kobus/simple.html HTTP/1.0
3. GET /~kobus/simple.html HTTP/1.0
   Host: www.cs.utah.edu:80

* Also, with telnet, the following return 501 Not Implemented error: 

1. POST http://www.cs.utah.edu/~kobus/simple.html HTTP/1.0
2. HEAD http://www.cs.utah.edu/~kobus/simple.html HTTP/1.0
3. DELETE http://www.cs.utah.edu/~kobus/simple.html HTTP/1.0
…

* Invalid entry will receive 400 Bad Request error, such as invalid headers.