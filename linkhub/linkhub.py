# -*- coding: utf-8 -*-
import sys
import json
import datetime
import base64

try:
    import http.client as httpclient
except ImportError:
    import httplib as httpclient
import io
from cStringIO import StringIO
from hashlib import sha1
from hashlib import md5
import hmac
from collections import namedtuple

LINKHUB_ServiceURL = "auth.linkhub.co.kr"
LINKHUB_APIVersion = "1.0"


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
    def __init__(self):
        self.__conn = None
        # self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL);

    def __getconn(self):
        if self.__conn == None:
            self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL)
            return self.__conn
        else:
            try:
                self.__conn.request("GET", "/Time")
                res = self.__conn.getresponse()
                _ = res.read()
            except httpclient.HTTPException:
                self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL)
                return self.__conn
            return self.__conn

    def get(self, LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP=None):
        postData = json.dumps({"access_id": AccessID, "scope": Scope})
        callDT = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        uri = '/' + ServiceID + '/Token'

        hmacTarget = StringIO()
        hmacTarget.write("POST\n")
        hmacTarget.write(Utils.b64_md5(postData) + "\n")
        hmacTarget.write(callDT + "\n")
        if forwardIP != None: hmacTarget.write(forwardIP + "\n")
        hmacTarget.write(LINKHUB_APIVersion + "\n")
        hmacTarget.write(uri)

        hmac = Utils.b64_hmac_sha1(SecretKey, hmacTarget.getvalue())

        headers = {'x-lh-date': callDT, 'x-lh-version': LINKHUB_APIVersion}
        if forwardIP != None: headers['x-lh-forwarded'] = forwardIP
        headers['Authorization'] = 'LINKHUB ' + LinkID + ' ' + hmac
        headers['Content-Type'] = 'Application/json'

        conn = self.__getconn()

        conn.request('POST', uri, postData, headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString)

    def balance(self, Token):
        conn = self.__getconn()

        conn.request('GET', '/' + Token.serviceID + '/Point', '', {'Authorization': 'Bearer ' + Token.session_token})

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)

    def partnerBalance(self, Token):
        conn = self.__getconn()

        conn.request('GET', '/' + Token.serviceID + '/PartnerPoint', '',
                     {'Authorization': 'Bearer ' + Token.session_token})

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)


class LinkhubException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Utils:
    @staticmethod
    def b64_md5(input):
        return base64.b64encode(md5(input.encode('utf-8')).digest()).decode()

    @staticmethod
    def b64_hmac_sha1(keyString, targetString):
        return base64.b64encode(hmac.new(base64.b64decode(keyString.encode('utf-8')), targetString.encode('utf-8'),
                                         sha1).digest()).decode().rstrip('\n')

    @staticmethod
    def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

    @staticmethod
    def json2obj(data):
        if (type(data) is bytes): data = data.decode()
        return json.loads(data, object_hook=Utils._json_object_hook)
