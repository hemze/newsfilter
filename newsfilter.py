#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib2
import re
import os

class NewsProcessor:
    def __init__(self,link):
        """Initialize obj: send req, get data,req status ..."""
        self.link = link
        try:
            req = urllib2.Request(self.link)
            res = urllib2.urlopen(req)
            self.status = res.code
            if(self.status == 200):
                self.readConfig()
                #self.data = res.read()

            elif (self.status >= 400 and self.status < 500):
                print "Got a client error while accessing ", self.link
            elif (self.status >= 500):
                print "Got a server error at ", self.link
            else:
                pass
        except:
            print "Got an error, please check the address provided: ", self.link
    def applyRule(self, rule, text):
        """Apply the given rule to the _text_ arg"""
        pass
    def readConfig(self):
        """Read the config file, fix the settings"""
        pass
    def formPath(self):
        """Form the path to save the file with the filtered and formatted data in accordance with the link provided"""
        pass
    def formatData(self):
        """Format the filtered data"""
        pass
    def conserveData(self):
        """Save the filtered and formatted data"""
        pass

if(len(sys.argv) > 1):
    np = NewsProcessor(sys.argv[1])
else:
    print "Please provide a URL"
