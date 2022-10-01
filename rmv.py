
import socket


def connect_RSI(self):
    # Create Socket
    rServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to host and port
    rServer.bind((self.host, self.port))

    # Listen For msgs
    rServer.listen(1)

    # Accept connection
    connection, s_server = rServer.accept()

    print("Connected to", s_server)

    self.connection = connection


def update_RSI(self):
    # Loop
    while self.auto_trade and self.connection:
        # Receive RSI
        rsi = self.connection.recv(1024).decode().split(",")

        # Update
        self.lvl = rsi

    self.connection.close()

    # target=self.track_Trade, args=(mt5.positions_get, mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_BUY, mt5.TRADE_ACTION_DEAL, mt5.ORDER_TIME_GTC, mt5.ORDER_FILLING_FOK, mt5.order_send,))

# def track_Trade(self, getPosition, sellType, buyType, getTradeAction, getOrderTime, getOrderFiling, sendOrder):
#     while True:
#         # Wait
#         sleep(0.5)

#         # Get Orders
#         positions = getPosition()

#         print("Tracking Trades,", "Positions:", len(positions))

#         if len(positions) > 0:
#             for prop in positions:
#                 type = sellType if prop.type == 0 else buyType

#                 # Check If Order Is Already Being Tracked
#                 if prop.ticket in self.items:
#                     # Check If In Loss And If Current Loss Is 2 Pips Or Greater, Below 0.
#                     # If Requirements Meet, Close Trade.
#                     if prop.profit <= (0 - (2 * prop.volume)):
#                         # Instantiate Request Object
#                         request = {
#                             "action": getTradeAction,
#                             "symbol": prop.symbol,
#                             "volume": float(prop.volume),
#                             "type": type,
#                             "position": prop.ticket,
#                             "price": prop.price_current,
#                             "deviation": 20,
#                             "magic": self.magic,
#                             "comment": "Hello World",
#                             "type_time": getOrderTime,
#                             "type_filling": getOrderFiling,
#                         }

#                         # Close Order
#                         sendOrder(request)

#                     # If Current Trade Has maintained a Low Profit 5 Consecutive Times, End Trade
#                     if self.items[prop.ticket] >= 3:
#                         # Instantiate Request Object
#                         request = {
#                             "action": getTradeAction,
#                             "symbol": prop.symbol,
#                             "volume": float(prop.volume),
#                             "type": type,
#                             "position": prop.ticket,
#                             "price": prop.price_current,
#                             "deviation": 20,
#                             "magic": self.magic,
#                             "comment": "Hello World",
#                             "type_time": getOrderTime,
#                             "type_filling": getOrderFiling,
#                         }

#                         # Close Order
#                         sendOrder(request)
#                         del self.items[prop.ticket]

#                     # If Current Profit On Order Is Not Incrementing, Update count
#                     if prop.profit > 0 and prop.profit < (3 * prop.volume):
#                         self.items[prop.ticket] += 1

#                 # If Order Is Not Being Tracked
#                 else:
#                     # Check If In Loss And If Current Loss Is 2 Pips Or Greater, Below 0.
#                     # If Requirements Meet, Close Trade.
#                     if prop.profit <= (0 - (2 * prop.volume)):
#                         type = sellType if prop.type == 0 else buyType

#                         # Instantiate Request Object
#                         request = {
#                             "action": getTradeAction,
#                             "symbol": prop.symbol,
#                             "volume": float(prop.volume),
#                             "type": type,
#                             "position": prop.ticket,
#                             "price": prop.price_current,
#                             "deviation": 20,
#                             "magic": self.magic,
#                             "comment": "Hello World",
#                             "type_time": getOrderTime,
#                             "type_filling": getOrderFiling,
#                         }

#                         # Close Order
#                         sendOrder(request)

#                     # Check If Current Profit Is Above 2 Pips,
#                     # Add To Tracked Orders
#                     elif prop.profit > (2 * prop.volume):
#                         self.items[prop.ticket] = 1
