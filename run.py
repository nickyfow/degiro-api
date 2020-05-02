#!/usr/bin/env python3.7
from degiro import DeGiro
from degiro.product import Product

from config import DEGIRO_USERNAME, DEGIRO_PASSWORD

degiro = DeGiro()
degiro.login(DEGIRO_USERNAME, DEGIRO_PASSWORD)
products = degiro.search_products('Vanguard', product_types=[Product.Type.ETF])
print(f'{products[0]["name"]}: {products[0]["isin"]}')
