#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib.request
import urllib.parse
import re
import os
import configparser
import xml.etree.ElementTree as ET
import string

class NewsProcessor:
    def __init__(self,link):
        """Initialize obj: send req, get data,req status ..."""
        self.link = link
        #connect and check the request status
        ## req = urllib2.Request(self.link)
        ## res = urllib2.urlopen(req)
        res = urllib.request.urlopen(self.link)
        ## self.dataEnc = res.info().getparam("charset")
        self.status = res.code
        self.path = ""
        self.basedir = ""
        if(self.status == 200):
            self.config = configparser.ConfigParser()
            self.config.read("process.cfg")
            #fix the data read from remote source and filter/format it
            self.data = res.read()
            #tree = ET.fromstring(self.data)
            #root = tree.getroot()
            self.filterData()
            self.formatData()
            for b in self.data:

            self.data = str.join([])self.data.encode("ascii")
            f = open("temp","w")
            f.write(self.data)
            if len(self.data)>0:
                #save data if anything left after processing
                self.formPath()
                self.conserveData()
        #handle http error codes
        elif (self.status >= 400 and self.status < 500):
            print ("Got a client error while accessing " + self.link)
        elif (self.status >= 500):
            print ("Got a server error at " + self.link)
        else:
            pass
    def filterData(self):
        #initial filter
        rule = r'(?is)(?:<body[^>]*>)(?P<data>.*)(?:</body>)'
        sData = self.searchByRule(rule,"data")
        self.data = sData["group"]
        grN = "cont"
        #include data according to the config
        inclPttrn = r"(?is)<(?P<"+grN+">[^>]+)\s+(id|class)=[^>]*?("+self.config["filter"]["include"].replace(",","|")+")[^>]*>"
        sData = self.searchByRule(inclPttrn,grN)
        self.data = self.data[sData["end"]:]
        self.data = self.data[:self.getClosingTagPos(sData["group"],self.data)]
        #exclude text according to the config
        exclPttrn = r"(?is)<(?P<"+grN+">[^>]+)\s+(id|class)=[^>]*?("+self.config["filter"]["exclude"].replace(",","|")+")[^>]*?>"
        sData = self.searchByRule(exclPttrn,grN)
        while sData:
            exclPart = self.data[sData["start"]:self.getClosingTagPos(sData["group"],self.data[sData["end"]:])+sData["end"]]
            self.data = self.data.replace(exclPart,"")
            sData = self.searchByRule(exclPttrn,grN)

    def searchByRule(self,rule,gr=None):
        #search the text by a regexp rule and get a dict with data
        res = re.search(rule,str(self.data))
        ret = {}
        if res:
            ret["full"] = res.group()
            ret["start"] = res.start()
            ret["end"] = res.end()
            if gr:
                ret["group"] = res.groupdict()[gr]
        else:
            ret = None
        return ret
    def getClosingTagPos(self,tag,text):
        """Text must not content the opening tag"""
        #find the closing tag by >tag< argument in the >text<
        count = 0
        i = 0
        while i < len(text):
            found = "."
            if text[i]=="<":
                if i+len(tag)+2 < len(text):
                    stag = text[i+1:i+len(tag)+1]
                    etag = text[i+1:i+len(tag)+2]
                    if stag==tag:
                        count = count + 1
                        found = "<"+stag+">"
                    elif etag=="/"+tag:
                        count = count - 1
                        found = "<"+etag+">"
            i+=len(found)
            if count < 0:
                break
        return i

    def formatData(self):
        #replace tags from >isolate< config key with whitespaces
        search = r"(?is)<[/]?("+self.config["format"]["isolate"].replace(",","|")+")[^>]*>"
        replace = r"\n\n"
        self.data = re.sub(search,replace,self.data)
        #replace >a< tags with title and href
        self.data = re.sub(r'<a[^>]href=["|\'](.+?)["|\'][^>]*?>(.*?)</a>',r"\2 [\1]",self.data,re.I|re.S)
        #exclude all the left tags
        self.data = re.sub(r'<[/]?[^>]+>',r"",self.data,re.I|re.S)
        #make a column in 80 symbols
        #keeping in mind invisible symbols
        self.data = re.sub(r'(.{150,}?)[\b\s]',r"\1\n",self.data,re.S|re.U)
        #clean up 3 and more breaks going together
        self.data = re.sub("\n{3,}",r"\n\n",self.data).strip()

    def formPath(self):
        """Form the path to save the file with the filtered and formatted data in accordance with the link provided"""
        #cut the protocol and unnecessary www string
        pttrn = r"(?is)(?:http://(www|))"
        path = re.sub(r"(?is)http[s]?://(www\.|)",r"",self.link)
        #add .txt at the end
        path = re.sub(r"(?is)(\.\w+|/|)$",r".txt",path)
        #check if basedir is set in the config file and set current if not
        if(self.config["save"]["basedir"] == ""):
            self.config["save"]["basedir"] = os.getcwd()
        self.path = self.config["save"]["basedir"]+"/"+path
        res = re.search(r"(?is)(?P<basedir>.*/)(?P<fname>[^/]+\.txt)$",self.path)
        #fix the basedir from the root
        self.basedir = res.groupdict()["basedir"]
    def conserveData(self):
        """Save the filtered and formatted data"""
        #make path if doesn't exist
        if(not os.path.exists(self.basedir)):
            os.makedirs(self.basedir)
        f = open(self.path,"w")
        f.write(self.data)
        pass

if(len(sys.argv) > 1):
    np = NewsProcessor(sys.argv[1])
    pass
else:
    print ("Please provide a URL")
