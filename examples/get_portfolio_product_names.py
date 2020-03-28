# Get current portfolio
# Returns symbol, company name, product id
from degiro import DeGiro
from degiro.utils import pretty_json
from datetime import datetime

from examples.config import DEGIRO_USERNAME, DEGIRO_PASSWORD

def main():
  degiro = DeGiro()
  degiro.login(DEGIRO_USERNAME, DEGIRO_PASSWORD)
  degiro.init_urls()
  portfolio = degiro.portfolio()
  products = [ product['id'] for product in portfolio ]
  products_info = degiro.get_products_by_ids(products)['data']
  # Select symbol and name, filter on stocks
  products_info = {
    product['symbol']: (product['name'], product['id'])
    for product in products_info.values()
    if 'marketAllowed' in product and product['marketAllowed']
  }
  print(pretty_json(products_info))

if __name__ == '__main__':
  main()
