import json

class Order:
  class BuySell:
    BUY = 'BUY'
    SELL = 'SELL'

  class Type:
    LIMIT = 0
    MARKET = 2
    STOPLOSS = 3
    STOPLIMIT = 1

    def from_string(name):
      return {
        'LIMIT': OrderType.LIMIT,
        'MARKET': OrderType.MARKET,
        'STOPLOSS': OrderType.STOPLOSS,
        'STOPLIMIT': OrderType.STOPLIMIT
      }[name]

  class TimeType:
    DAY = 1
    PERMANENT = 3

  # Properties: Provide these in constructor
  #buySell = BuySell
  #orderType = Type
  #productId = int
  #timeType = TimeType
  #size = int
  #price = float # optional
  #stopPrice = float # optional

  # Order constructor
  def __init__(self, **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)

  def to_dict(self):
    return dict(vars(self))

  def to_json(self):
    return(json.dumps(vars(self)))
