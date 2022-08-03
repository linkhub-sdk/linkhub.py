# -*- coding: utf-8 -*-
import sys
import json
import base64

try:
    import http.client as httpclient
except ImportError:
    import httplib as httpclient
import io
from time import time as stime
from datetime import datetime
from hashlib import sha256
import hmac
from collections import namedtuple

LINKHUB_ServiceURL = "auth.linkhub.co.kr"
LINKHUB_ServiceURL_Static = "static-auth.linkhub.co.kr"
LINKHUB_ServiceURL_GA = "ga-auth.linkhub.co.kr"
LINKHUB_APIVersion = "2.0"


def __with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Token(__with_metaclass(Singleton)):
    def __init__(self,timeOut = 15):
        self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL);
        self.__connectedAt = stime()
        self.__timeOut = timeOut

    def _getconn(self, UseStaticIP=False, UseGAIP=False):
        if(UseGAIP) :
            self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL_GA)
        elif(UseStaticIP) :
            self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL_Static)
        else :
            self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL)
        self.__connectedAt = stime()

        return self.__conn

    def get(self, LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP=None, UseStaticIP=False, UseLocalTimeYN=True, UseGAIP=False):
        postData = json.dumps({"access_id": AccessID , "scope" : Scope})
        callDT = self.getTime(UseStaticIP, UseLocalTimeYN, UseGAIP)
        uri = '/' + ServiceID + '/Token'

        #Ugly Code.. StringIO is better but, for compatibility.... need to enhance.
        hmacTarget = ""
        hmacTarget += "POST\n"
        hmacTarget += Utils.b64_sha256(postData) + "\n"
        hmacTarget += callDT + "\n"
        if forwardIP != None : hmacTarget += forwardIP + "\n"
        hmacTarget += LINKHUB_APIVersion + "\n"
        hmacTarget += uri

        hmac = Utils.b64_hmac_sha256(SecretKey, hmacTarget)

        headers = {'x-lh-date':callDT , 'x-lh-version':LINKHUB_APIVersion}
        if forwardIP != None : headers['x-lh-forwarded'] = forwardIP
        headers['Authorization'] = 'LINKHUB ' + LinkID + ' ' + hmac
        headers['Content-Type'] = 'Application/json'
        headers["User-Agent"] = "PYTHON LINKHUB SDK"

        conn = self._getconn(UseStaticIP, UseGAIP)

        conn.request('POST', uri, postData, headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString)

    def balance(self, Token, UseStaticIP=False, UseGAIP=False):
        conn = self._getconn(UseStaticIP, UseGAIP)

        headers = {'Authorization':'Bearer ' + Token.session_token}
        headers['User-Agent'] = 'PYTHON LINKHUB SDK'

        conn.request('GET','/' + Token.serviceID + '/Point','',headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)

    def partnerBalance(self, Token, UseStaticIP=False, UseGAIP=False):
        conn = self._getconn(UseStaticIP, UseGAIP)

        headers = {'Authorization':'Bearer ' + Token.session_token}
        headers['User-Agent'] = 'PYTHON LINKHUB SDK'

        conn.request('GET','/' + Token.serviceID + '/PartnerPoint','',headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)

    # 파트너 포인트충전 팝업 URL 추가 - 2017/08/29
    def getPartnerURL(self, Token, TOGO, UseStaticIP=False, UseGAIP=False):
        conn = self._getconn(UseStaticIP, UseGAIP)

        headers = {'Authorization':'Bearer ' + Token.session_token}
        headers['User-Agent'] = 'PYTHON LINKHUB SDK'

        conn.request('GET','/' + Token.serviceID + '/URL?TG='+TOGO,'',headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString).url

    def getTime(self, UseStaticIP=False, UseLocalTimeYN=True, UseGAIP=False):
        if(UseLocalTimeYN == True):
            return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        conn = self._getconn(UseStaticIP, UseGAIP)

        conn.request('GET', '/Time','',{'User-Agent':'PYTHON LINKHUB SDK'})

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return responseString.decode('utf-8')

class LinkhubException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Utils:
    @staticmethod
    def b64_sha256(input):
        return base64.b64encode(sha256(input.encode('utf-8')).digest()).decode('utf-8')

    @staticmethod
    def b64_hmac_sha256(keyString, targetString):
        return base64.b64encode(hmac.new(base64.b64decode(keyString.encode('utf-8')), targetString.encode('utf-8'), sha256).digest()).decode('utf-8').rstrip('\n')

    @staticmethod
    def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

    @staticmethod
    def json2obj(data):
        if(type(data) is bytes): data = data.decode('utf-8')
        return json.loads(data, object_hook=Utils._json_object_hook)
