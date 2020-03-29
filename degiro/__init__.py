import requests
import logging
import urllib
from datetime import datetime, timedelta

from .utils import pretty_json
from .client_info import ClientInfo
from .product import Product
from .order import Order

class DeGiro:
  __LOGIN_URL           = 'https://trader.degiro.nl/login/secure/login'
  __CONFIG_URL            = 'https://trader.degiro.nl/login/secure/config'
  __PRODUCT_SEARCH_URL  = 'https://trader.degiro.nl/product_search/secure/v5/products/lookup'
  __CLIENT_INFO_URL     = 'https://trader.degiro.nl/pa/secure/client'
  __TRANSACTIONS_URL    = 'https://trader.degiro.nl/reporting/secure/v4/transactions'
  __ORDERS_URL          = 'https://trader.degiro.nl/reporting/secure/v4/order-history'

  urls = {}

  __GET_REQUEST = 0
  __POST_REQUEST = 1
  __DELETE_REQUEST = 2
  __SPECIAL_REQUEST = 3

  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)

  def __request(self, url, payload, request_type=__GET_REQUEST, error_message='An error occurred.'):
    if request_type == DeGiro.__GET_REQUEST:
      response = requests.get(url, params=payload)
    elif request_type == DeGiro.__POST_REQUEST:
      response = requests.post(url, json=payload)
    elif request_type == DeGiro.__DELETE_REQUEST:
      response = requests.delete(url)
    elif request_type == DeGiro.__SPECIAL_REQUEST:
      response = requests.get(url, json=payload,
        headers={ 'Cookie': 'JSESSIONID=' + str(self.session_id) }
      )
    else:
      raise Exception(f'Unknown request type: {request_type}')

    if response.status_code != 200:
      raise Exception(f'{error_message} Response: {response.text}')
    self.logger.debug(pretty_json(response.json()))
    return response.json()

  def order_cancel(self, orderId):
    # Check order before submitting it
    payload = {
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id,
    }
    res = self.__request(
      self.urls['tradingUrl']
        + 'v5/order/' + orderId + ';jsessionid=' + self.session_id
        + '?' + urllib.parse.urlencode(payload),
      {},
      request_type=DeGiro.__DELETE_REQUEST,
      error_message='Could not confirm order.'
    )
    return res

  def order_check(self, order):
    # Check order before submitting it
    payload = {
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id,
    }
    res = self.__request(
      self.urls['tradingUrl']
        + 'v5/checkOrder;jsessionid=' + self.session_id
        + '?' + urllib.parse.urlencode(payload),
      order.to_dict(),
      request_type=DeGiro.__POST_REQUEST,
      error_message='Could not check order.'
    )
    return res

  def order_confirm(self, order, confirmationId):
    # Check order before submitting it
    payload = {
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id,
    }
    res = self.__request(
      self.urls['tradingUrl']
        + 'v5/order/' + confirmationId + ';jsessionid=' + self.session_id
        + '?' + urllib.parse.urlencode(payload),
      order.to_dict(),
      request_type=DeGiro.__POST_REQUEST,
      error_message='Could not confirm order.'
    )
    return res

  def order_make(self, order):
    # Check, then confirm order
    confirmationId = self.order_check(order)['data']['confirmationId']
    return self.order_confirm(order, confirmationId)['data']['orderId']

  def get_products_by_ids(self, product_ids):
    # Get trading url from the broker
    payload = {
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id,
    }
    res = self.__request(
      self.urls['productSearchUrl']
        + 'v5/products/info?'
        + urllib.parse.urlencode(payload),
      product_ids,
      request_type=DeGiro.__POST_REQUEST,
      error_message='Could not get product ids.'
    )
    return res

  def init_urls(self):
    # Get urls from the broker
    payload = {
      'isPassCodeReset': False,
      'isRedirectToMobile': False
    }
    res = self.__request(DeGiro.__CONFIG_URL,
      payload,
      request_type=DeGiro.__SPECIAL_REQUEST,
      error_message='Could not get config.'
    )['data']
    self.urls = {
      'productSearchUrl': res['productSearchUrl'],
      'tradingUrl': res['tradingUrl']
    }
    return res

  def login(self, username, password):
    login_payload = {
      'username': username,
      'password': password,
      'isPassCodeReset': False,
      'isRedirectToMobile': False
    }
    login_response = self.__request(DeGiro.__LOGIN_URL, login_payload, request_type=DeGiro.__POST_REQUEST, error_message='Could not login.')
    self.session_id = login_response['sessionId']

    client_info_payload = { 'sessionId': self.session_id }
    client_info_response =  self.__request(DeGiro.__CLIENT_INFO_URL, client_info_payload, error_message='Could not get client info.')
    self.client_info = ClientInfo(client_info_response['data'])

  def portfolio(self):
    # Return portfolio
    # Note: includes liquidity funds and cash
    data = {
      'portfolio': 0,
    }
    res = self.__request(self.urls['tradingUrl']
        + 'v5/update/' + str(self.client_info.account_id)
        + ';jsessionid=' + str(self.session_id),
      data,
      error_message='Could not get portfolio.'
    )
    # Skip inactive products
    ret = [
      product for product in res['portfolio']['value']
      if [
        i for i in product['value']
        if i['name'] == 'size' and i['value'] != 0
      ]
    ]
    return ret

  def find_nasdaq_symbol(self, symbol):
    # Return info for given symbol (NASDAQ)
    # throw error if zero, or more than one found
    url_params = {
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id,
      'productType': 1, # STOCK
      'stockListType': 'exchange',
      'stockList': 663, # NASDAQ
      'country': 846, # US
      'searchText': symbol,
      'sortColumns': 'name',
      'sortTypes': 'asc',
    }
    res = self.__request(self.urls['productSearchUrl']
        + 'v5/products/lookup?' + urllib.parse.urlencode(url_params),
      {},
      error_message='Could not get portfolio.'
    )
    if 'products' not in res or len(res['products']) == 0:
      raise Exception(f'Could not find symbol {symbol}')
    elif len(res['products']) > 1:
      raise Exception(f'More than one product found for {symbol}')
    return res['products'][0]

  def search_products(self, searchText, limit=7, product_types=None):
    product_search_payload = {
      'searchText': searchText,
      'limit': limit,
      'offset': 0,
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id
    }
    products = self.__request(DeGiro.__PRODUCT_SEARCH_URL, product_search_payload, error_message='Could not get products.')['products']
    if product_types:
      return [p for p in products if p['productTypeId'] in product_types]
    else:
      return products

  def transactions(self, from_date, to_date, group_transactions=False):
    transactions_payload = {
      'fromDate': from_date.strftime('%d/%m/%Y'),
      'toDate': to_date.strftime('%d/%m/%Y'),
      'group_transactions_by_order': group_transactions,
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id
    }
    return self.__request(DeGiro.__TRANSACTIONS_URL, transactions_payload, error_message='Could not get transactions.')['data']
    
  def orders(self, from_date, to_date):
    orders_payload = {
      'fromDate': from_date.strftime('%d/%m/%Y'),
      'toDate': to_date.strftime('%d/%m/%Y'),
      'intAccount': self.client_info.account_id,
      'sessionId': self.session_id
    }
    # The DeGiro API requires the time span to be max 90 days, otherwise it returns orders between `fromDate` and `fromDate + 90 days`.
    if (toDate - fromDate).days > 90:
      raise Exception('The DeGiro API requires the time span to be max 90 days.')
    
    return self.__request(DeGiro.__ORDERS_URL, orders_payload, error_message='Could not get orders.')['data']
