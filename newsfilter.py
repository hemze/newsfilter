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
                self.config = Cfg("process.cfg")
                self.data = res.read()
                res = re.search(r'(?is)(?:<body[^>]*>)(?P<data>.*)(?:</body>)',self.data)
                if (res):
                    self.data = res.groupdict()["data"]
                inclPttrn = r"(?is)(?:<[^>]+\s+(id|class)=\S*("+self.config["filter"]["include"].replace(",","|")+")[^>]*>)"
                res = re.search(inclPttrn,self.data)
                #print self.data
                if(res):
                    self.data=self.data[res.start():]
                    print self.data[:50]
                exit
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

    def formPath(self):
        """Form the path to save the file with the filtered and formatted data in accordance with the link provided"""
        pass
    def formatData(self):
        """Format the filtered data"""
        pass
    def conserveData(self):
        """Save the filtered and formatted data"""
        pass

class Cfg(dict):
    def __init__(self,pathToFile):
        try:
            fINI = open(pathToFile)
        except IOError:
            print pathToFile+" не открывается, нет такого или прав нехватает"
            sys.exit()
        lconf = fINI.readlines()
        chars = (";", "#", "\n")
        lconf = filter((lambda x: not x[0] in chars), lconf)
        lconf = map((lambda x: x.strip()) ,lconf)
        dconf = {}
        for each in lconf:
            if each[0] == "[":
                base = each[1:][:-1]
                self[base] = {}
            else:
                each = each.split("#")[0].strip()
                each = each.split(";")[0].strip()
                key, value = each.split("=", 1)
                if("|" in value):
                    self[base][key.strip()] = {}
                    pars = value.strip().split("|")
                    i = 0
                    for item in pars:
                        if(i+1 < len(pars) and i % 2 == 0):
                            self[base][key.strip()][pars[i]]=pars[i+1]
                        i=i+1
                else:
                    self[base][key.strip()] = value.strip()


if(len(sys.argv) > 1):
    np = NewsProcessor(sys.argv[1])

else:
    print "Please provide a URL"
