# Issue a market order
from degiro import DeGiro
from degiro.utils import pretty_json
from degiro.order import Order
from datetime import datetime

from examples.config import DEGIRO_USERNAME, DEGIRO_PASSWORD

def main():
  print('Init session')
  degiro = DeGiro()
  degiro.login(DEGIRO_USERNAME, DEGIRO_PASSWORD)
  degiro.init_urls()
  print('Make order')
  order = Order(
    buySell=Order.BuySell.BUY,
    orderType=Order.Type.MARKET,
    productId=16583624,
    timeType=Order.TimeType.DAY,
    size=1,
  )
  order_id = degiro.order_make(order)
  print(pretty_json(order_id))
  print('Cancel order')
  degiro.order_cancel(order_id)

if __name__ == '__main__':
  main()
