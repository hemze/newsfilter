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
        #try:
        req = urllib2.Request(self.link)
        res = urllib2.urlopen(req)
        self.dataEnc = res.info().getparam("charset")
        self.status = res.code
        self.path = ""
        self.basedir = ""
        if(self.status == 200):
            self.config = Cfg("process.cfg")
            self.data = res.read()
            self.filterData()
            self.formatData()
            f = open("temp","w")
            f.write(self.data)
            f.close()
            f = open("temp","r").read()
            f = f.decode(self.dataEnc)
            open("temp","w").write(f)
            if len(self.data)>0:        
                self.formPath()
                self.conserveData()
        elif (self.status >= 400 and self.status < 500):
            print "Got a client error while accessing ", self.link
        elif (self.status >= 500):
            print "Got a server error at ", self.link
        else:
            pass
        #except:
        #    print "Got an error, please check the address provided: ", self.link
    def filterData(self):
        res = re.search(r'(?is)(?:<body[^>]*>)(?P<data>.*)(?:</body>)',self.data)
        if (res):
            self.data = res.groupdict()["data"]
            inclPttrn = r"(?is)<(?P<cont>[^>]+)\s+(id|class)=\S*("+self.config["filter"]["include"].replace(",","|")+")[^>]*>"
            res = re.search(inclPttrn,self.data)
            if(res):
                cont = res.groupdict()["cont"]
                self.data=self.data[res.start():]
                count = 0
                for i in range(len(self.data)):
                    if self.data[i]=="<":
                        if i+4 < len(self.data):
                            stag = self.data[i+1]+self.data[i+2]+self.data[i+3]
                            etag = self.data[i+1]+self.data[i+2]+self.data[i+3]+self.data[i+4]
                            if stag==cont:
                                count = count + 1
                            elif etag=="/"+cont:
                                count = count - 1
                    if count < 0:
                        break
                self.data = self.data[:i]
                    #re.sub(r'<a[^>]href=("|\')(?P<href>.*)[^>]>(?P<title>.*?)</a>',r"(?P=title) \[(?P=href)\]",self.data,re.I|re.S)
                    #res = re.search(r'<a[^>]href=(["\'])(?P<href>[^\1]*?)\1[^>]>(?P<title>.*?)</a>',self.data,re.I|re.S)
                    #res = re.search(r'(?is)(["\'])(?P<href>[^\1]*?)\1',self.data,re.I|re.S)                     
    def formatData(self):
        search = r"(?is)<[/]?("+self.config["format"]["isolate"].replace(",","|")+")[^>]*>"
        replace = r"\n\n"
        #self.data = re.sub(search,replace,self.data)
        #self.data = re.sub("\n{3,}",r"\n\n",self.data).strip()
                
    def formPath(self):
        """Form the path to save the file with the filtered and formatted data in accordance with the link provided"""
        pttrn = r"(?is)(?:http://(www|))"
        path = re.sub(r"(?is)http[s]?://(www\.|)",r"",self.link) 
        path = re.sub(r"(?is)(\.\w+|/|)$",r".txt",path) 
        if(self.config["save"]["basedir"] == ""):
            self.config["save"]["basedir"] = os.getcwd()
        self.path = self.config["save"]["basedir"]+"/"+path
        res = re.search(r"(?is)(?P<basedir>.*/)(?P<fname>[^/]+\.txt)$",self.path)
        self.basedir = res.groupdict()["basedir"]
    def conserveData(self):
        """Save the filtered and formatted data"""
        if(not os.path.exists(self.basedir)):
            os.makedirs(self.basedir)            
        f = open(self.path,"w")
        f.write(self.data)
        pass

class Cfg(dict):
    def __init__(self,pathToFile):
        try:
            f = open(pathToFile)
        except IOError:
            print pathToFile+" Error opening file: "+pathToFile
            sys.exit()
        lconf = f.readlines()
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
    pass
else:
    print "Please provide a URL"
