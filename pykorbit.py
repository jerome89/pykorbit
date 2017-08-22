# -*- coding: utf-8 -*-
## Usage Example
## 1. Run python
## 2. In python shell, import pykorbit(this file)
## 3. Initialize class with your given credential file(csv). e.g., korbitApi = pykorbit.KorbitApi('myCredential.csv')
## 4. To get authentication information, call method makeAuth(). e.g., korbitApi.makeAuth()

import requests
import getpass
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import time
import os

class KorbitApi():
    def __init__(self, keyFileName, key = None, secret = None, postData = None, version = "v1", timeout = 20):
        self.keyFileName = keyFileName
        self.secret = secret
        self.host = "https://api.korbit.co.kr/%s/" % version
        self.timeout = timeout
        self.key = key
        self.secret = secret
        self.authToken = None
        self.timeStamp = None
        self.constants = None
        if self.checkIfKeyFileExistsOrNot(keyFileName):
            self.keyFile = open(self.keyFileName, 'r').readlines()[1].split(',')
            self.key = self.keyFile[0]
            self.secret = self.keyFile[1]
            self.authToken = self.makeAuth()
            self.constants = self.getConstants()
    
    # Common Utilities #
    
    @property
    def headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': "{} {}".format(self.authToken['token_type'], self.authToken['access_token'])
        }
        
    def requestPost(self, path, headers = None, data = None):
        response = requests.post(urljoin(self.host, path), headers = headers, data = data, timeout = self.timeout)
        return response.json()
    
    def requestGet(self, path, headers = None, data = None):
        response = requests.get(urljoin(self.host, path), headers = headers, data = data, timeout = self.timeout)
        return response.json()
    
    def getConstants(self):
        return self.requestGet(path = "constants")
    
    # End of Common Utilities #
    
    def makeAuth(self):
        userName = raw_input("Account : ")
        password = getpass.getpass("Password : ")
        postData = {
            'client_id': self.key,
            'client_secret': self.secret,
            'username': userName,
            'password': password,
            'grant_type': "password"
        }
        self.authToken = self.requestPost(path = "oauth2/access_token", data = postData)
        self.timeStamp = time.time()
        return self.authToken
    
    def refreshToken(self):
        postData = {
            'client_id': self.key,
            'client_secret': self.secret,
            'refresh_token': self.authToken['refresh_token'],
            'grant_type': "refresh_token"
        }
        self.authToken = self.requestPost(path = "oauth2/access_token", data = postData)
        self.timeStamp = time.time()
        return self.authToken
    
    def checkIfKeyFileExistsOrNot(self, keyFileName):
        if os.path.exists(keyFileName):
            return True
        else:
            return False
    
    # Returns current User Information
    def getUserInfo(self):
        return self.requestGet(path="user/info", headers=self.headers)
    
    # Returns current CurrencyPair (currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw') 
    # 기본값 : currencyPair = 'btc_krw'
    def getCurrencyPair(self, currencyPair = 'btc_krw'):
        return self.requestGet(path="ticker/detailed?currency_pair={}".format(currencyPair))
    
    # 매도 / 매수 호가 조회 (currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw')
    # 기본값 : currencyPair = 'btc_krw'
    def getOrderbook(self, currencyPair = 'btc_krw'):
        return self.requestGet(path="orderbook?currency_pair={}".format(currencyPair))
   
    # 체결 내역 조회 
    # currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw'
    # time : 'hour'(최근 1시간 체결 내역), 'minute'(최근 1분 체결 내역), 'day'(최근 하루 체결 내역)
    # 기본값 : currencyPair = 'btc_krw', time = 'hour'
    def getTransactions(self, currencyPair = 'btc_krw', time = 'hour'):
        return self.requestGet(path="transactions?currency_pair={}&time={}".format(currencyPair, time))