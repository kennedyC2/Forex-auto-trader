# Import Dependencies
# ==============================================================================
import MetaTrader5 as mt5
import numpy
from datetime import datetime
from threading import Timer
from time import sleep
import threading


# ==============================================================================
#                               Class Object
# ==============================================================================
class BBB:
    def __init__(self, account, password, server):
        self.Account = int(account)
        self.Password = password
        self.Server = server
        self.Timeframe_Dict = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }

        self.Timeframe_list = [
            "M1", "M5", "M15", "M30", "H1", "D1", "W1", "MN1"]
        self.items = {}
        self.H_H = set()
        self.L_L = set()

        # Settings
        self.pair = False
        self.timeframe = False
        self.lot = False
        self.sl = False
        self.tp = False
        self.deviation = False
        self.magic = 112026457

        self.bot_B = {
            "active": False,
            "trades": 0,
            "price": 0
        }

        self.bot_S = {
            "active": False,
            "trades": 0,
            "price": 0
        }

        # RSI
        self.rsi = 0
        self.AvG = 0
        self.AvL = 0
        self.pos = 0
        self.neg = 0

        self.connection = False
        self.auto_trade = False

    # Initialize MetaTrader 5 n Log Client In
    # ==========================================
    def Connect(self):
        if self.Account and self.Password and self.Server:
            if not mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe", login=self.Account, password=self.Password, server=self.Server, timeout=60000, portable=False):
                return {"status": False, "message": mt5.last_error()}
            else:
                # Define threads
                t_trade = threading.Thread(target=self.track_Trade)

                # Start Process
                t_trade.start()

                return {"status": True, "message": "success"}

    # Get Symbols || Currency Pair
    # ===================================================================================

    def Get_Currency_Pairs(self):
        pairs = mt5.symbols_get()

        # Create List of Pairs
        data = []
        for prop in pairs:
            data.append(prop._asdict()["name"])

        return data

    # Get currency pair information
    # ===================================================================================

    def Get_Currency_Pair_Info(self):
        info = mt5.symbol_info(self.pair)

        # Check If pair Is Available
        if not info.visible:
            # Add Pair If Not Available
            if not mt5.symbol_select(self.pair, True):
                print("Failed to add {}".format(self.pair))
            else:
                self.Get_Currency_Pair_Info()

        # Get Info If Pair Is Available
        else:
            data = info._asdict()
            res = {
                "time": "",
                "low": data["bidlow"],
                "open": data["session_open"],
                "close": data["session_close"],
                "high": data["bidhigh"],
                "bid": data["bid"],
                "ask": data["ask"]
            }

            return res

    # OPEN, CLOSE, HIGH, LOW
    # ===================================================================================

    def HLOC(self):
        data = mt5.copy_rates_from_pos(
            self.pair, self.Timeframe_Dict[self.timeframe], 0, 60)

        HLOC = []

        for prop in data:
            # Create Data
            arr = []
            dt = datetime.fromtimestamp(prop[0]).strftime("%Y-%m-%d, %H:%M")
            arr.append(str(dt.split(",")[1]))
            arr.append(numpy.float64(prop[3]))
            arr.append(numpy.float64(prop[1]))
            arr.append(numpy.float64(prop[4]))
            arr.append(numpy.float64(prop[2]))

            # Add To HLOC
            HLOC.append(arr)

        return HLOC

    # Get active trades
    # ===================================================================================

    def Orders(self):
        positions = mt5.positions_get()
        orders = mt5.orders_get()
        data = {}
        data["positions"] = []
        data["orders"] = []
        count = 0

        # Loop [Instant Orders]
        for prop in positions:
            data = {}
            data["pair"] = prop.symbol
            data["ticket"] = prop.ticket
            data["op"] = prop.price_open
            data["cl"] = prop.price_current
            data["profit"] = prop.profit
            data["sl"] = prop.sl
            data["tp"] = prop.tp
            data["lot"] = prop.volume
            data["index"] = count
            data["type"] = "buy" if prop.type == 0 else "sell"
            data["positions"].append(data)
            count = count + 1

        # Loop [Pending Orders]
        for prop in orders:
            data = {}
            data["pair"] = prop.symbol
            data["ticket"] = prop.ticket
            data["op"] = prop.price_open
            data["cl"] = prop.price_current
            data["profit"] = "pending"
            data["sl"] = prop.sl
            data["tp"] = prop.tp
            data["lot"] = prop.volume_current
            data["type"] = "buy_stop" if prop.type == 4 else "sell_stop"
            data["orders"].append(data)

        return data

    # Place Buy Order
    # ===================================================================================

    def Instant_Buy_Order(self, price):
        # Instantiate Request Object
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": float(price),
            "sl": float(price) - self.sl,
            "tp": float(price) + self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response = mt5.order_send(request)

        # Validate
        if response.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message": response.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Buy_Stop Order
    # ===================================================================================

    def Buy_Stop_Order(self, price):
        # Instantiate Request Object
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": float(price),
            "sl": float(price) - self.sl,
            "tp": float(price) + self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response = mt5.order_send(request)

        # Validate
        if response.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message": response.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Sell Order
    # ===================================================================================

    def Instant_Sell_Order(self, price):
        # Instantiate Request Object
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": float(price),
            "sl": float(price) + self.sl,
            "tp": float(price) - self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response = mt5.order_send(request)

        # Validate
        if response.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message": response.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Sell_Stop Order
    # ===================================================================================

    def Sell_Stop_Order(self, price):
        # Instantiate Request Object
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": float(price),
            "sl": float(price) + self.sl,
            "tp": float(price) - self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response = mt5.order_send(request)

        # Validate
        if response.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message": response.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Buy and Sell Order
    # ===================================================================================

    def Double_Instant_Order(self, price):
        # Instantiate Request Object
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": float(price),
            "sl": float(price) - self.sl,
            "tp": float(price) + self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Instantiate Request Object
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": float(price),
            "sl": float(price) + self.sl,
            "tp": float(price) - self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response_B = mt5.order_send(buy_request)
        response_S = mt5.order_send(sell_request)

        # Validate
        if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message_B": response_B.comment, "message_S": response_S.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Buy-Stop and Sell-Stop Order
    # ===================================================================================

    def Double_Pending_Order(self, price):

        buy_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": float(price),
            "sl": float(price) - self.sl,
            "tp": float(price) + self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        sell_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.pair,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": float(price),
            "sl": float(price) + self.sl,
            "tp": float(price) - self.tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response_B = mt5.order_send(buy_request)
        response_S = mt5.order_send(sell_request)

        # Validate
        if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message_B": response_B.comment, "message_S": response_S.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Close Instant Orders
    # ===================================================================================

    def close_Instant_Order(self, index):
        # Get Orders
        orders = mt5.positions_get()
        i = 0

        while i < len(orders):
            if int(index) == i:
                # initialize variables
                ticket = orders[i].ticket
                symbol = orders[i].symbol
                price = mt5.symbol_info_tick(
                    symbol).ask if orders[i].type == 0 else mt5.symbol_info_tick(symbol).bid
                order_type = mt5.ORDER_TYPE_SELL if orders[i].type == 0 else mt5.ORDER_TYPE_BUY

                # Instantiate Request Object
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": self.lot,
                    "type": order_type,
                    "position": ticket,
                    "price": price,
                    "deviation": self.deviation,
                    "magic": self.magic,
                    "comment": "Hello World",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }

                # Send Order
                response = mt5.order_send(request)

                if response.retcode != mt5.TRADE_RETCODE_DONE:
                    return {"status": False, "message": response.comment}
                else:
                    return {"status": True, "message": self.Orders()}

            i = i + 1

    # Close Pending Orders
    # ============================================================================
    def close_Pending_Order(self, ticket):
        # Instantiate Request Object
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": int(ticket),
        }

        # Send Order
        response = mt5.order_send(request)

        if response.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message": response.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # RSI
    # ============================================================================
    def c_RSI(self):
        while self.auto_trade:
            # if not self.AvG and not self.AvL:
            data = mt5.copy_rates_from_pos(
                self.pair, mt5.TIMEFRAME_M15, 0, 15)
            TG = 0
            TL = 0

            # Compute AvG and AvL
            for i in range(len(data) - 1):
                if data[i + 1][4] > data[i][4]:
                    TG += data[i + 1][4] - data[i][4]
                else:
                    TL += data[i][4] - data[i + 1][4]

            self.AvG = (TG / 14)
            self.AvL = (TL / 14)

            # RSI = 100 - (100 / (1 + (AvG / AvL)))
            if self.AvL != 0:
                self.rsi = round(
                    100 - (100 / (1 + (self.AvG / self.AvL))), 2)
            else:
                if self.AvG != 0:
                    self.rsi = 100
                else:
                    self.rsi = 50
            print("RSI:", self.rsi)
            # else:
            #     data = mt5.copy_rates_from_pos(
            #         self.pair, self.Timeframe_Dict[self.timeframe], 0, 2)

            #     # New Average
            #     if data[1][4] > data[0][4]:
            #         self.AvG = ((self.AvG * 13) - (self.pos) +
            #                     (data[1][4] - data[0][4])) / 14
            #         self.AvL = self.AvL - self.neg
            #         self.pos = data[1][4] - data[0][4]
            #         self.neg = 0
            #     else:
            #         self.AvL = ((self.AvL * 13) - (self.neg) +
            #                     (data[0][4] - data[1][4])) / 14
            #         self.AvG = self.AvG - self.pos
            #         self.neg = data[0][4] - data[1][4]
            #         self.pos = 0

            #     # RSI = 100 - (100 / (1 + (AvG / AvL)))
            #     if self.AvL != 0:
            #         self.rsi = round(
            #             100 - (100 / (1 + (self.AvG / self.AvL))), 2)
            #     else:
            #         if self.AvG != 0:
            #             self.rsi = 100
            #         else:
            #             self.rsi = 50
            #     print("RSI:", self.rsi)

            # Wait
            sleep(2)

    # Track Trade
    # ============================================================================

    def track_Trade(self):
        while True:
            # Wait
            sleep(0.5)

            # Get Orders
            positions = mt5.positions_get()

            print("Tracking Trades,", "Positions:", len(positions))

            if len(positions) > 0:
                for prop in positions:
                    type = mt5.ORDER_TYPE_SELL if prop.type == 0 else mt5.ORDER_TYPE_BUY

                    # Check If Order Is Already Being Tracked
                    if prop.ticket in self.items:
                        # Check If In Loss And If Current Loss Is 2 Pips Or Greater, Below 0.
                        # If Requirements Meet, Close Trade.
                        if prop.profit <= (0 - (2 * prop.volume)):
                            # Instantiate Request Object
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": prop.symbol,
                                "volume": float(prop.volume),
                                "type": type,
                                "position": prop.ticket,
                                "price": prop.price_current,
                                "deviation": 20,
                                "magic": self.magic,
                                "comment": "Hello World",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_FOK,
                            }

                            # Close Order
                            mt5.order_send(request)

                        # If Current Trade Has maintained a Low Profit 5 Consecutive Times, End Trade
                        if self.items[prop.ticket] >= 3:
                            # Instantiate Request Object
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": prop.symbol,
                                "volume": float(prop.volume),
                                "type": type,
                                "position": prop.ticket,
                                "price": prop.price_current,
                                "deviation": 20,
                                "magic": self.magic,
                                "comment": "Hello World",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_FOK,
                            }

                            # Close Order
                            mt5.order_send(request)
                            del self.items[prop.ticket]

                        # If Current Profit On Order Is Not Incrementing, Update count
                        if prop.profit > 0 and prop.profit < (3 * prop.volume):
                            self.items[prop.ticket] += 1

                    # If Order Is Not Being Tracked
                    else:
                        # Check If In Loss And If Current Loss Is 2 Pips Or Greater, Below 0.
                        # If Requirements Meet, Close Trade.
                        if prop.profit <= (0 - (2 * prop.volume)):
                            type = mt5.ORDER_TYPE_SELL if prop.type == 0 else mt5.ORDER_TYPE_BUY

                            # Instantiate Request Object
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": prop.symbol,
                                "volume": float(prop.volume),
                                "type": type,
                                "position": prop.ticket,
                                "price": prop.price_current,
                                "deviation": 20,
                                "magic": self.magic,
                                "comment": "Hello World",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_FOK,
                            }

                            # Close Order
                            mt5.order_send(request)

                        # Check If Current Profit Is Above 2 Pips,
                        # Add To Tracked Orders
                        elif prop.profit > (2 * prop.volume):
                            self.items[prop.ticket] = 1

    # Fetch return Prices
    # ============================================================================
    def fetcher(self, candles):
        # Fetch Candles
        data = mt5.copy_rates_from_pos(
            self.pair, self.Timeframe_Dict[self.timeframe], 1, candles + 6)

        # Filter returning Highs
        for i in range(len(data)):
            counter_1 = 0
            counter_2 = 0

            # Get Downtrend return Prices:
            # Check If Current Candle High Is Greater Than Next Candle High
            # Check If Next Candle closing Price Is Less Than Its Opening Price
            if (i <= len(data) - 6):
                for j in range(1, 6):
                    if data[i + j - 1][4] > data[i + j][4]:
                        counter_1 += 1

                if counter_1 >= 4:
                    self.H_H.add(data[i][2])
                else:
                    for j in range(1, 6):
                        if data[i + j - 1][4] < data[i + j][4]:
                            counter_2 += 1

                    if counter_2 >= 4:
                        self.L_L.add(data[i][3])
            else:
                break

    # Auto Trader 1
    # ============================================================================

    def auto_T1(self, price, no_of_trades):
        # Update Status
        self.bot_B["active"] = True

        print("BOT_B")

        # Initialize
        while self.bot_B["trades"] < int(no_of_trades) / 2:
            # Get Current Tick Info
            info = (mt5.symbol_info(self.pair))._asdict()

            # Check If Current Price Is Either 5 pips below or 5 pips above
            if info["ask"] - price <= 0.5 or price - info["ask"] <= 0.5:
                self.Instant_Sell_Order(
                    self.lot, self.pair, self.deviation, self.sl, self.tp, info["ask"])

                self.bot_B["price"] = info["ask"]

                # Wait
                sleep(10)

                # Update Status
                self.bot_B["active"] = False

                # Return
                return

            # Wait
            sleep(10)

    # Auto Trader 2
    # ============================================================================

    def auto_T2(self, price, no_of_trades):
        # Update Status
        self.bot_S["active"] = True

        print("BOT_S")

        # Initialize
        while self.bot_S["trades"] < int(no_of_trades) / 2:
            # Get Current Tick Info
            info = (mt5.symbol_info(self.pair))._asdict()

            # Check If Current Price Is Either 5 pips below or 5 pips above
            if info["bid"] - price <= 0.5 or price - info["bid"] <= 0.5:
                self.Instant_Buy_Order(
                    self.lot, self.pair, self.deviation, self.sl, self.tp, info["bid"])

                self.bot_S["price"] = info["bid"]

                # Wait
                sleep(10)

                # Update Status
                self.bot_S["active"] = False

                # Return
                return

            # Wait
            sleep(10)

    # Start Auto Trading
    # ============================================================================

    def start_auto(self, no_of_trades, candles):
        # Populate Prices
        self.fetcher(candles)

        # Get Existing Orders
        orders = mt5.positions_get()

        # RSI Thread
        s_RSI = threading.Thread(target=self.c_RSI)

        # Start RSI Thread
        s_RSI.start()

        if len(orders) > 0:
            # Update Counter
            for prop in orders:
                if prop.type == 0:
                    self.bot_B["trades"] += 1
                else:
                    self.bot_S["trades"] += 1

        while self.auto_trade:
            # print(self.rsi)
            # Check RSI
            # if len(self.rsi) > 0:
            #     # Get Current Tick Info
            #     info = (mt5.symbol_info(self.pair))._asdict()

            #     # Check If Database Has Been Updated And Number Of Existing Orders Are Not Greater Than Required
            #     if len(self.H_H) > 0 and len(self.L_L) > 0:
            #         # Start HP Monitor
            #         if info["ask"] in self.H_H and self.bot_B["trades"] < int(no_of_trades) / 2 and not self.bot_B["active"]:
            #             if info["ask"] - self.bot_B["price"] > 0.3 and round(float(self.lvl[0]), 1) >= 65:
            #                 self.auto_T1(info["ask"], no_of_trades)

            #         # Wait
            #         sleep(5)

            #         # Start LP Monitor
            #         if info["bid"] in self.L_L and self.bot_S["trades"] < int(no_of_trades) / 2 and not self.bot_S["active"]:
            #             if self.bot_S["price"] - info["bid"] > 0.3 and round(float(self.lvl[0]), 1) <= 35:
            #                 self.auto_T2(info["bid"], no_of_trades)

            # Wait
            sleep(5)
