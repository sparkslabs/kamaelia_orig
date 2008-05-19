#!/usr/bin/python
#
# (C) 2004 British Broadcasting Corporation and Kamaelia Contributors(1)
#     All Rights Reserved.
#
# You may only modify and redistribute this under the terms of any of the
# following licenses(2): Mozilla Public License, V1.1, GNU General
# Public License, V2.0, GNU Lesser General Public License, V2.1
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://kamaelia.sourceforge.net/AUTHORS - please extend this file,
#     not this notice.
# (2) Reproduced in the COPYING file, and at:
#     http://kamaelia.sourceforge.net/COPYING
# Under section 3.5 of the MPL, we are using this text since we deem the MPL
# notice inappropriate for this file. As per MPL/GPL/LGPL removal of this
# notice is prohibited.
#
# Please contact us via: kamaelia-list-owner@lists.sourceforge.net
# to discuss alternative licensing.
# -------------------------------------------------------------------------

import unittest
import Kamaelia.requestLine

class requestLineTestCase(unittest.TestCase):
	def test_Method_FullURL_UsernamePasswordCGIArgs_Protocol(self):
		"Accepted URL Format"
		r = "BIBBLE foo://toor:letmein@server.bigcompany.com/bla?this&that=other PROTO/3.3"
		try:
			foo=requestLine(r)
		except "BadRequest":
			foo= "Line is not parseable - does not match:\nMETHOD proto://(user(:passwd)?@)?domain/url proto/ver"
		print foo

	def test_Method_FullURL_Username_BlankPasswordCGIArgs_Protocol(self):
		"Accepted URL Format"
		r = "BIBBLE foo://toor@server.bigcompany.com/bla?this&that=other PROTO/3.3"

	def test_Method_FullURL_noauth_CGIArgs_Protocol(self):
		"Accepted URL Format"
		r = "BIBBLE foo://server.bigcompany.com/bla?this&that=other PROTO/3.3"

	def test_Method_FullURL_noauth_noCGI_Protocol(self):
		"Accepted URL Format"
		r = "BIBBLE foo://server.bigcompany.com/ PROTO/3.3"

	def test_NoMethod_FullURL_noauth_noCGI_Protocol(self):
		"Accepted URL Format"
		r = "foo://server.bigcompany.com/ PROTO/3.3"

        # =====================================================================
	def test_http09_minimal(self):
		"Rejected URL Format"
		r = "/"
                foo=requestLine(r)
                except "BadRequest":

		
	def test_http09_typical(self):
		"Rejected URL Format"
		r = "/some/file/on/server"

	def test_http09_SemiFullURL(self):
		"Rejected URL Format"
		r = "http://server.bigcompany.com/some/file/on/server"

	def test_AcceptedForms(self):
		requests = [
			
			
			 ]
		for REQ in requests:
			print "Parsing request:", REQ
			try:
				foo=requestLine(REQ)
			except "BadRequest":
				foo= "Line is not parseable - does not match:\nMETHOD proto://(user(:passwd)?@)?domain/url proto/ver"
			print foo
			print

	def __init__(self,request):
		try:
			[self.method, rest] = request.split(" ",1)
			[self.reqprotocol, rest] = rest.split("://",1)
			[userdomain, rest] = rest.split("/",1)
			rest = "/" + rest # The leading / is significant
			try:
				[userpass,self.domain] = userdomain.split("@",1)
			except ValueError:
				[userpass,self.domain] = ["", userdomain]
			try:
				[self.user,self.passwd] = userpass.split(":",1)
			except ValueError:
				[self.user,self.passwd] = [userpass, ""]
			[self.url, protocolandver] = rest.split(" ", 1) # !!!! May well need changing due to Microsoft
			[self.protocol, self.version] = protocolandver.split("/",1)
		except:
			raise "BadRequest"

	def debug__str__(self):
		result =  "METHOD  \t:" + self.method + "\n" +\
			"PROTOCOL\t:" + self.protocol + "\n" +\
			"VERSION \t:" + self.version + "\n" +\
			"Req Type\t:" + self.reqprotocol + "\n" +\
			"USER    \t:" + self.user + "\n" +\
			"PASSWORD\t:" + self.passwd + "\n" +\
			"DOMAIN  \t:" + self.domain + "\n" +\
			"URL     \t:" + self.url
		return result

	def __str__(self):
		result = ""
		result =  result + self.method + " "
		result =  result + self.reqprotocol + "://"
		if self.user:
			result =  result + self.user
			if self.passwd:
				result =  result + ":" + self.passwd
			result = result + "@"
		result =  result + self.domain
		result =  result + self.url +" "
		result =  result + self.protocol + "/"
		result =  result + self.version
		return result

if __name__ =="__main__":
		# These are the only format requests we accept.
		# All others are rejected
		requests = [
			"BIBBLE foo://toor:letmein@server.bigcompany.com/bla?this&that=other PROTO/3.3",
			"BIBBLE foo://toor@server.bigcompany.com/bla?this&that=other PROTO/3.3",
			"BIBBLE foo://server.bigcompany.com/bla?this&that=other PROTO/3.3",
			"BIBBLE foo://server.bigcompany.com/ PROTO/3.3",
			"foo://server.bigcompany.com/ PROTO/3.3"
			 ]
		for REQ in requests:
			print "Parsing request:", REQ
			try:
				foo=requestLine(REQ)
			except "BadRequest":
				foo= "Line is not parseable - does not match:\nMETHOD proto://(user(:passwd)?@)?domain/url proto/ver"
			print foo
			print
