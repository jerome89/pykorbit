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
    
    ##################### 조회 API ########################
    
    # Returns current User Information
    def getUserInfo(self):
        return self.requestGet(path = "user/info", headers = self.headers)
    
    # Returns current CurrencyPair (currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw') 
    # 기본값 : currencyPair = 'btc_krw'
    def getCurrencyPair(self, currencyPair = 'btc_krw'):
        return self.requestGet(path = "ticker/detailed?currency_pair={}".format(currencyPair))
    
    # 매도 / 매수 호가 조회 (currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw')
    # 기본값 : currencyPair = 'btc_krw'
    def getOrderbook(self, currencyPair = 'btc_krw'):
        return self.requestGet(path = "orderbook?currency_pair={}".format(currencyPair))
   
    # 체결 내역 조회 
    # currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw'
    # time : 'hour'(최근 1시간 체결 내역), 'minute'(최근 1분 체결 내역), 'day'(최근 하루 체결 내역)
    # 기본값 : currencyPair = 'btc_krw', time = 'hour'
    def getTransactions(self, currencyPair = 'btc_krw', time = 'hour'):
        return self.requestGet(path = "transactions?currency_pair={}&time={}".format(currencyPair, time))
    
    ######################################################
    
    
    
    ##################### 주문 API ########################
    
    # 매수 주문
    # Returns orderId, status, currency_pair Fields
    # currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw'
    # orderType : 'limit'(호가 주문), 'market'(시장가 주문)
    # price : 호가 주문에 사용하는 parameter
    # coinAmount : 매수하고자 하는 코인의 수량. 호가 주문인 경우에는 반드시 입력해야한다. 시장가 주문인 경우에는 자동으로 생성.
    # fiatAmount : 시장가 주문인 경우에만 사용하는 구매에 쓰일 원화량
    # nonce : api 호출마다 반드시 증가시켜야하는 value. 동일 주문을 방지하기 위함.
    def orderCoin(self, currencyPair = None, orderType = None, 
                  price = 0, coinAmount = 0, fiatAmount = 0, nonce = None):
        if currencyPair is None or orderType is None or fiatAmount == 0 or nonce is None:
            print("구매할 코인 / 주문 형태 / 코인 수량 / 원화 / nonce 등을 입력해주세요")
            if orderType == 'limit' and price == 0:
                print("호가 주문입니다. 코인 가격을 입력해주세요")
            if orderType == 'market' and fiatAmount == 0:
                print("시장가 주문입니다. 구매 가격을 입력해주세요.")
        postData = {
            'currency_pair': currencyPair,
            'type': orderType,
            'price': str(price),
            'coin_amount': str(coinAmount),
            'nonce': str(nonce),
            'fiat_amount': str(fiatAmount)
        }
        return self.requestPost(path="user/orders/buy", data = postData, headers = self.headers)
    
    # 매도 주문
    # Returns orderId, status, currency_pair Fields
    # currencyPair : 'btc_krw', 'eth_krw', 'etc_krw', 'xrp_krw', 'bch_krw'
    # orderType : 'limit'(호가 주문), 'market'(시장가 주문)
    # price : 매도 주문에 사용할 가격. 호가 주문에만 사용.
    # coinAmount : 매도하고자 하는 코인의 수량.
    def sellCoin(self, currencyPair = None, orderType = None, price = 0, coinAmount = 0, nonce = None):
        postData = {
            'currency_pair': currencyPair,
            'type': orderType,
            'price': str(price),
            'coin_amount': str(coinAmount),
            'nonce': str(nonce)
        }
        return self.requestPost(path="user/orders/sell", data = postData, headers = self.headers)