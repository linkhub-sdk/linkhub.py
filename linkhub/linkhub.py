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
from time import time as stime
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
    def __init__(self,timeOut = 60):
        self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL);
        self.__connectedAt = stime()
        self.__timeOut = timeOut

    def _getConn(self, ForceReconnect=False):
        if ForceReconnect or self.__conn == None or stime() - self.__connectedAt >= self.__timeOut:
            self.__conn = httpclient.HTTPSConnection(LINKHUB_ServiceURL)
            self.__connectedAt = stime()
            return self.__conn
        else:
            return self.__conn

    def get(self,LinkID,SecretKey,ServiceID,AccessID,Scope,forwardIP = None):
        postData = json.dumps({"access_id" : AccessID , "scope" : Scope})
        callDT = self.getTime()
        uri = '/' + ServiceID + '/Token'

        # Ugly Code.. StringIO is better but, for compatibility.... need to enhance.

        # I suggest this strategy "Build a list of strings, then join it"
        # it's efficient and easy to implement.
        hmacTarget = []
        hmacTarget.append("POST\n")
        hmacTarget.append(Utils.b64_md5(postData) + "\n")
        hmacTarget.append(callDT + "\n")
        if forwardIP != None : hmacTarget.append(forwardIP + "\n")
        hmacTarget.append(LINKHUB_APIVersion + "\n")
        hmacTarget.append(uri)

        hmac = Utils.b64_hmac_sha1(SecretKey,"".join(hmacTarget))

        headers = {'x-lh-date':callDT , 'x-lh-version':LINKHUB_APIVersion}
        if forwardIP != None : headers['x-lh-forwarded'] = forwardIP
        headers['Authorization'] = 'LINKHUB ' + LinkID + ' ' + hmac
        headers['Content-Type'] = 'Application/json'

        # SEH 의 EXCEPTION_EXECUTE_HANDLER 를 모방해서, 한번의 실패에 한해 강제 재연결을 수행한다.
        # 그 후에 발생하는 에러에 대해서는 그냥 예외처리한다.
        for i in range(2):
            try:
                conn = self._getConn()
                conn.request('POST', uri, postData, headers)

                response = conn.getresponse()
                responseString = response.read()
                break
            except httpclient.HTTPException:
                if i == 0:
                    # 처음 예외가 발생했을 경우는 재연결을 시도한다.
                    try:
                        self._getConn(ForceReconnect=True)
                        continue
                    except Exception:
                        # 재연결에서 어떤 에러가 발생한다면?
                        # 처리할 수 없는 상황, 아마도 서버에의 초기 연결이 실패한경우
                        raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')
                else:
                    # 이미 한번 예외 처리를 했음에도 불구하고 에러가 난 경우.
                    raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString)

    def balance(self,Token):
        # SEH 의 EXCEPTION_EXECUTE_HANDLER 를 모방해서, 한번의 실패에 한해 강제 재연결을 수행한다.
        # 그 후에 발생하는 에러에 대해서는 그냥 예외처리한다.
        for i in range(2):
            try:
                conn = self._getConn()
                conn.request('GET', '/' + Token.serviceID + '/Point', '',
                             {'Authorization': 'Bearer ' + Token.session_token})

                response = conn.getresponse()
                responseString = response.read()
                break
            except httpclient.HTTPException:
                if i == 0:
                    # 처음 예외가 발생했을 경우는 재연결을 시도한다.
                    try:
                        self._getConn(ForceReconnect=True)
                        continue
                    except Exception:
                        # 재연결에서 어떤 에러가 발생한다면?
                        # 처리할 수 없는 상황, 아마도 서버에의 초기 연결이 실패한경우
                        raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')
                else:
                    # 이미 한번 예외 처리를 했음에도 불구하고 에러가 난 경우.
                    raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code),err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)

    def partnerBalance(self,Token):
        # SEH 의 EXCEPTION_EXECUTE_HANDLER 를 모방해서, 한번의 실패에 한해 강제 재연결을 수행한다.
        # 그 후에 발생하는 에러에 대해서는 그냥 예외처리한다.
        for i in range(2):
            try:
                conn = self._getConn()
                conn.request('GET', '/' + Token.serviceID + '/PartnerPoint', '',
                             {'Authorization': 'Bearer ' + Token.session_token})

                response = conn.getresponse()
                responseString = response.read()
                break
            except httpclient.HTTPException:
                if i == 0:
                    # 처음 예외가 발생했을 경우는 재연결을 시도한다.
                    try:
                        self._getConn(ForceReconnect=True)
                        continue
                    except Exception:
                        # 재연결에서 어떤 에러가 발생한다면?
                        # 처리할 수 없는 상황, 아마도 서버에의 초기 연결이 실패한경우
                        raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')
                else:
                    # 이미 한번 예외 처리를 했음에도 불구하고 에러가 난 경우.
                    raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code),err.message)
        else:
            return float(Utils.json2obj(responseString).remainPoint)

    def getTime(self):
        # SEH 의 EXCEPTION_EXECUTE_HANDLER 를 모방해서, 한번의 실패에 한해 강제 재연결을 수행한다.
        # 그 후에 발생하는 에러에 대해서는 그냥 예외처리한다.
        for i in range(2):
            try:
                conn = self._getConn()
                conn.request('GET', '/Time')

                response = conn.getresponse()
                responseString = response.read()
                break
            except httpclient.HTTPException:
                if i == 0:
                    # 처음 예외가 발생했을 경우는 재연결을 시도한다.
                    try:
                        self._getConn(ForceReconnect=True)
                        continue
                    except Exception:
                        # 재연결에서 어떤 에러가 발생한다면?
                        # 처리할 수 없는 상황, 아마도 서버에의 초기 연결이 실패한경우
                        raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')
                else:
                    # 이미 한번 예외 처리를 했음에도 불구하고 에러가 난 경우.
                    raise LinkhubException(int(-99999999), 'UNEXPECTED EXCEPTION')

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise LinkhubException(int(err.code),err.message)
        else:
            return responseString.decode('utf-8')

class LinkhubException(Exception):
    def __init__(self,code,message):
        self.code = code
        self.message = message


class Utils:
    @staticmethod
    def b64_md5(input):
        return base64.b64encode(md5(input.encode('utf-8')).digest()).decode()

    @staticmethod
    def b64_hmac_sha1(keyString,targetString):
        return base64.b64encode(hmac.new(base64.b64decode(keyString.encode('utf-8')),targetString.encode('utf-8'),sha1).digest()).decode().rstrip('\n')

    @staticmethod
    def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

    @staticmethod
    def json2obj(data):
        if(type(data) is bytes): data = data.decode()
        return json.loads(data, object_hook=Utils._json_object_hook)
