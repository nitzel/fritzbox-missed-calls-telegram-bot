# -*- coding: utf-8 -*-
# dependencies
#  lxml
#  fritzconnection

# Call-Types
# 1-2 incoming?
#   3 out
#   10 blocked
#   11 call running at the moment

import urllib.request
import html
import time

from fritzconnection import (FritzConnection)
from lxml import etree

class Phonebook:
    phonebook = {}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    @staticmethod
    def nameFromTellowsBasic(phonenumber):
        try:
            req = urllib.request.Request('http://www.tellows.de/basic/num/'+phonenumber, headers=Phonebook.headers)
            with urllib.request.urlopen(req) as response:
                START = '<span id ="name">\n'
                STOP = '('
                htmlContent = str(response.read().decode('utf-8'))
                posA = htmlContent.find(START) + len(START) # find start of name
                posB = htmlContent.find(STOP, posA) # find end of name
                # print("telo len: ",len(START),"posA: ",posA," posB",posB)
                if posA - len(START) < 0 or posB == -1:
                    raise Exception('Not found in tellows basic answer')
                name = htmlContent[posA:posB] # get name
                name = name[:min(len(name),10)]
                # we unescape html escape sequences like &ouml etc.
                return html.unescape(str(name))
        except urllib.error.HTTPError as e:
            raise Exception('Not found in tellows')
        except:
            raise

    @staticmethod
    def nameFromTellows(phonenumber):
        try:
            req = urllib.request.Request('http://www.tellows.de/num/'+phonenumber, headers=Phonebook.headers)
            with urllib.request.urlopen(req) as response:
                START = 'Inhaber und Adresse: </strong><br/>'
                STOP = '<br>'
                htmlContent = str(response.read().decode('utf-8'))
                posA = htmlContent.find(START) + len(START) # find start of name
                posB = htmlContent.find(STOP, posA) # find end of name
                # print("telo len: ",len(START),"posA: ",posA," posB",posB)
                if posA - len(START) < 0 or posB == -1:
                    raise Exception('Not found in tellows answer')
                name = htmlContent[posA:posB] # get name
                name = name[:min(len(name),10)]
                # we unescape html escape sequences like &ouml etc.
                return html.unescape(str(name))
        except urllib.error.HTTPError as e:
            raise Exception('Not found in tellows')
        except:
            raise

    @staticmethod
    def nameFromDastelefonbuch(phonenumber):
        # now try to find that number with an reverse lookup
        try:
            with urllib.request.urlopen('http://www.dastelefonbuch.de/R%C3%BCckw%C3%A4rts-Suche/'+phonenumber) as response:
                START = '<div class="name" title="'
                STOP = '">'
                htmlContent = str(response.read().decode('utf-8'))
                posA = htmlContent.find(START) + len(START) # find start of name
                posB = htmlContent.find(STOP, posA) # find end of name
                # print("dast len: ",len(START),"posA: ",posA," posB",posB)
                if posA - len(START) < 0 or posB == -1:
                    raise Exception('Not found in dastelefonbuch')
                name = htmlContent[posA:posB] # get name
                name = name[:min(len(name),10)]
                # we unescape html escape sequences like &ouml etc.
                return html.unescape(str(name))
        except urllib.error.HTTPError as e:
            raise Exception('Not found in dastelefonbuch')
        except:
            raise

    @staticmethod
    def nameFromNumberLookup(phonenumber):
        phonenumber = str(phonenumber)
        if phonenumber not in Phonebook.phonebook:
            # now try to find that number with an reverse lookup
            try:
                # add new entry to our reverse lookup phonebook
                Phonebook.phonebook[phonenumber] = Phonebook.nameFromDastelefonbuch(phonenumber)
            except Exception as e:
                # try again with another service
                try:
                    # add new entry to our reverse lookup phonebook
                    Phonebook.phonebook[phonenumber] = Phonebook.nameFromTellowsBasic(phonenumber)
                except Exception as e:
                    # try again with another service
                    try:
                        # add new entry to our reverse lookup phonebook
                        Phonebook.phonebook[phonenumber] = Phonebook.nameFromTellows(phonenumber)
                    except BaseException as f:
                        # print("2 reverse lookup exceptions: \n1.", e, "and \n2. ", f)
                        # create pseudo entry to avoid repeated unsuccessful lookup attempts
                        Phonebook.phonebook[phonenumber] = '?'
        return Phonebook.phonebook[phonenumber]


class Call:
    def __init__(self, phonenumber, date, duration, name=None):
        self.phonenumber = phonenumber
        self.date = date
        self.duration = duration+'m' # for minutes
        self.duration = self.duration.replace(':','h ') # for hours
        if name is not None:
            self.name = name
        else:
            self.name = Phonebook.nameFromNumberLookup(self.phonenumber)
    def __str__(self):
        return "{0} called us on {1} for {2}\n\tPhone: {3}".\
                format(self.name, self.date, self.duration, self.phonenumber)
    def toMd(self):
        """ to markdown """
        return "*{0}* called us on *{1}* for *{2}*\n\t*Phone:* `{3}`".\
                format(self.name, self.date, self.duration, self.phonenumber)

class CheckCallList:
    def __init__(self, address='192.168.178.1',user='telegrambot',password='telegrambot314', knownCallId=5329):
        self.CHECKCALLLIST_INITDATA = {'address':address, 'user':user, 'password':password, 'knownCallId':knownCallId}
        self.connection = FritzConnection(address='192.168.178.1',user='telegrambot',password='telegrambot314')
        self.knownCallId = int(knownCallId)

    def getConfig(self):
            self.CHECKCALLLIST_INITDATA['knownCallId'] = self.knownCallId
            data = {'phonebook':Phonebook.phonebook, 'CHECKCALLLIST_INITDATA':self.CHECKCALLLIST_INITDATA}
            return data

    @staticmethod
    def loadFromConfig(data):
        Phonebook.phonebook = data['phonebook']
        return CheckCallList(**data['CHECKCALLLIST_INITDATA'])

    def checkForNewCalls(self, knownCallId=None):
        if knownCallId is not None:
            self.knownCallId = knownCallId
        # get the URL to the xml file with all calls
        calllisturl = self.connection.call_action('X_AVM-DE_OnTel', 'GetCallList')['NewCallListURL']
        # print(calllisturl)
        # downlod xml file, parse it and get root node
        root = etree.parse(calllisturl).getroot()

        def getChild(parent, attrname):
            """returns None if no child with that name or if the first is empty"""
            allattrs = parent.findall('.//'+attrname)
            if len(allattrs) > 0:
                return allattrs[0].text
            else:
                return None

        # list of all new/unprocessed incoming calls
        callerList = []
        # will later overwrite knownCallId
        maxKnownCallId = self.knownCallId
        for call in root.iter("Call"): # iterate through calls
            # new incoming call?
            callId = int(getChild(call, 'Id'))
            if  callId <= self.knownCallId:
                break # that's not a new call
            if getChild(call, 'Type') not in ["3","11"]:
                print("max",maxKnownCallId,"callid", callId)
                maxKnownCallId = max(maxKnownCallId, callId) # save highest id
                callerNumber   = getChild(call, 'Caller') # get caller-number
                callDate       = getChild(call, 'Date') # get date
                callDuration   = getChild(call, 'Duration') # get duration
                callerName     = None #getChild(call, 'Name') # get name from addressbook
                # callerName = "pupsie" if callerName is None else callerName # remove to trigger lookups
                # print(str(callChild(call, 'Name')) + " --> "+str(callerName))
                newcall = Call(callerNumber, callDate, callDuration, callerName)
                print("new call id(" + str(callId) + "): " + str(newcall))
                callerList.append(newcall)
        self.knownCallId = maxKnownCallId
        return callerList
