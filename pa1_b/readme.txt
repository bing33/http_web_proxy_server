# ############################################################################## #
# Assignment: HTTP Web Proxy Server                                              #
# Class: CS 4480 Computer Networks						 #
# File: readme.txt								 #
# By: xrawlinson							         #
# Last Update Date: 2/7/2016						         #
#										 #
# A web proxy that is capable of accepting HTTP GET requests, forwarding the 	 #
# requests to remote (origin) servers, and returning response data to the 	 #
# requested clients. It can handle multiple clients’ requests concurrently.	 #
# ############################################################################## #

This is the second stage of the program, which supports multiple clients’ requests concurrently to be connected to the proxy server.

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

