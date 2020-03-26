from degiro import DeGiro
from degiro.utils import pretty_json
from datetime import datetime

from examples.config import DEGIRO_USERNAME, DEGIRO_PASSWORD

def main():
  degiro = DeGiro()
  degiro.login(DEGIRO_USERNAME, DEGIRO_PASSWORD)
  degiro.init_urls()
  portfolio = degiro.portfolio()
  print(pretty_json(portfolio))

if __name__ == '__main__':
  main()
