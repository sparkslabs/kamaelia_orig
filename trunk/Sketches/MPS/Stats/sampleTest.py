#!/usr/bin/env python
#
#

from random import random
import time
targetSample = 22
target = targetSample/100.

def likelihood(numSamples, targetSample, numRequests=1): # This can return > 1.0
   try:
      currentRate= numSamples/float(numRequests)
      result = 100*   ((target-currentRate)/target)
      return result
   except ZeroDivisionError:
      return 1

def test_sampler():
   numRequests = 0
   numSamples = 0
   while 1:
      numRequests += 1
      l = likelihood(numSamples, targetSample, numRequests)
      if random() <= l:
         numSamples += 1
      if 1:
         if int((numSamples/float(numRequests))*100)<=targetSample:
            break
      else:
         print "reqs", numRequests,
         print "samples", numSamples,
         print "size",((numSamples/float(numRequests))*100),
         print "likelyhood", l
   return numRequests, int((numSamples/float(numRequests))*100)


sampleSize=1000
p5 = int(sampleSize*.05)
p25 = int(sampleSize*.25)
p50 = int(sampleSize*.50)
p75 = int(sampleSize*.75)
p95 = int(sampleSize*.95)
p97 = int(sampleSize*.97)
p99 = int(sampleSize*.99)
print p5,p25,p50,p75,p97,p99
for skew in xrange(1,20):
   results=[]
   rates=[]
   for i in xrange(sampleSize):
      x,y=test_sampler()
      results.append(x)
      rates.append(y)

   results.sort()
   print "5,25,50,75,95,97,99 : ", results[p5],results[p25],results[p50],results[p75],results[p95],results[p97],results[p99]
   print "5,25,50,75,95,97,99 : ", rates[p5],rates[p25],rates[p50],rates[p75],rates[p95],rates[p97],rates[p99]





