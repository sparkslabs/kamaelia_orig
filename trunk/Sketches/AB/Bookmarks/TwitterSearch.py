#! /usr/bin/python

# Interface to Twitter search API
# - Returns results of people searches as a dictionary

import urllib2
import urllib
import time
import os
import cjson
import string
from datetime import datetime,timedelta

import urlparse
import oauth2 as oauth

from Axon.Component import component

class PeopleSearch(component):
    Inboxes = {
        "inbox" : "Receives string indicating a person's name",
        "control" : ""
    }
    Outboxes = {
        "outbox" : "Outputs raw search output from Twitter people search in JSON",
        "signal" : ""
    }

    def __init__(self, username, consumerkeypair, keypair, proxy = False):
        super(PeopleSearch, self).__init__()
        self.proxy = proxy
        self.consumerkeypair = consumerkeypair
        self.keypair = keypair
        self.username = username
        self.ratelimited = datetime.today() - timedelta(minutes=15)

    def finished(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            if isinstance(msg, producerFinished) or isinstance(msg, shutdownMicroprocess):
                self.send(msg, "signal")
                return True
        return False

    def getOAuth(self, consumer_key, consumer_secret):
        # Perform OAuth authentication
        request_token_url = 'http://api.twitter.com/oauth/request_token'
        access_token_url = 'http://api.twitter.com/oauth/access_token'
        authorize_url = 'http://api.twitter.com/oauth/authorize'

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)

        resp, content = client.request(request_token_url, "POST")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(urlparse.parse_qsl(content))

        print "Request Token:"
        print "     - oauth_token        = %s" % request_token['oauth_token']
        print "     - oauth_token_secret = %s" % request_token['oauth_token_secret']
        print

        # The user must confirm authorisation so a URL is printed here
        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
        print

        accepted = 'n'
        # Wait until the user has confirmed authorisation
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        oauth_verifier = raw_input('What is the PIN? ')

        token = oauth.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer,token)

        resp, content = client.request(access_token_url, "POST", body="oauth_verifier=%s" % oauth_verifier)
        access_token = dict(urlparse.parse_qsl(content))

        # Access tokens retrieved from Twitter
        print "Access Token:"
        print "     - oauth_token        = %s" % access_token['oauth_token']
        print "     - oauth_token_secret = %s" % access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."
        print

        save = False
        # Load config to save OAuth keys
        try:
            homedir = os.path.expanduser("~")
            file = open(homedir + "/twitter-login.conf",'r')
            save = True
        except IOError, e:
            print ("Failed to load config file - not saving oauth keys: " + str(e))

        if save:
            raw_config = file.read()

            file.close()

            # Read config and add new values
            config = cjson.decode(raw_config)
            config['key'] = access_token['oauth_token']

            config['secret'] = access_token['oauth_token_secret']

            raw_config = cjson.encode(config)

            # Write out the new config file
            try:
                file = open(homedir + "/twitter-login.conf",'w')
                file.write(raw_config)
                file.close()
            except IOError, e:
                print ("Failed to save oauth keys: " + str(e))
        
        return [access_token['oauth_token'], access_token['oauth_token_secret']]

    def main(self):
        twitterurl = "http://api.twitter.com/1/users/search.json"

        # Check if OAuth has been done before - if so use the keys from the config file
        if self.keypair == False:
            self.keypair = self.getOAuth(self.consumerkeypair[0], self.consumerkeypair[1])

        if self.proxy:
            proxyhandler = urllib2.ProxyHandler({"http" : self.proxy})
            twitopener = urllib2.build_opener(proxyhandler)
            urllib2.install_opener(twitopener)

        #headers = {'User-Agent' : "BBC R&D Grabber"}
        #data = ""
        

        while not self.finished():
            # TODO: Implement backoff algorithm in case of connection failures - watch out for the fact this could delay the requester component
            if self.dataReady("inbox"):
                # Retieve keywords to look up
                person = self.recv("inbox")

                # Ensure we're not rate limited during the first request - if so we'll wait for 15 mins before our next request
                if (datetime.today() - timedelta(minutes=15)) > self.ratelimited:
                    requesturl = twitterurl + "?q=" + urllib.quote(person) + "&per_page=5"

                    params = {
                        'oauth_version': "1.0",
                        'oauth_nonce': oauth.generate_nonce(),
                        'oauth_timestamp': int(time.time()),
                        'user': self.username
                    }

                    token = oauth.Token(key=self.keypair[0],secret=self.keypair[1])
                    consumer = oauth.Consumer(key=self.consumerkeypair[0],secret=self.consumerkeypair[1])

                    params['oauth_token'] = token.key
                    params['oauth_consumer_key'] = consumer.key

                    req = oauth.Request(method="GET",url=requesturl,parameters=params)

                    signature_method = oauth.SignatureMethod_HMAC_SHA1()
                    req.sign_request(signature_method, consumer, token)

                    requesturl = req.to_url()

                    # Connect to Twitter
                    try:
                        #conn1 = urllib2.Request(requesturl,data,headers)
                        conn1 = urllib2.urlopen(requesturl)
                    except urllib2.HTTPError, e:
                        self.send("HTTP Error: " + str(e.code),"outbox") # Errors get sent back to the requester
                        conn1 = False
                    except urllib2.URLError, e:
                        self.send("Connect Error: " + e.reason,"outbox") # Errors get sent back to the requester
                        conn1 = False

                    if conn1:
                        # Check rate limiting here and print current limit
                        headers = conn1.info()
                        headerlist = string.split(str(headers),"\n")
                        for line in headerlist:
                            splitheader = line.split()
                            if splitheader[0] == "X-FeatureRateLimit-Remaining:" or splitheader[0] == "X-RateLimit-Remaining:":
                                print splitheader[0] + " " + str(splitheader[1])
                                if int(splitheader[1]) < 5:
                                    self.ratelimited = datetime.today()
                        # Grab json format result of people search here
                        try:
                            data = conn1.read()
                            try:
                                content = cjson.decode(data)
                                self.send(content,"outbox")
                            except cjson.DecodeError, e:
                                self.send(dict(),"outbox")
                        except IOError, e:
                            self.send("Read Error: " + str(e),"outbox") # TODO: FIXME - Errors get sent back to the requester
                        conn1.close()
                else:
                   print "Twitter search paused - rate limited"
                   self.send(dict(),"outbox")
            self.pause()
            yield 1
