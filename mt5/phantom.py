# Import Dependencies
# ==============================================================================
import MetaTrader5 as mt5
import numpy
import tulipy as tpy
from datetime import datetime
from time import sleep
import threading


# ==============================================================================
#                               Class Object
# ==============================================================================
class BBB:
    def __init__(self, account, password, server, pair, timeframe, lot, sl, tp, deviation):
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
        self.candles = {
            "M1": 60 * 60 * 24 * 7,
            "M5": 12 * 24 * 7,
            "M15": 4 * 24 * 7,
            "M30": 2 * 24 * 7,
            "H1": 24 * 7,
            "D1": 100,
            "W1": 100,
            "MN1": 100,
        }

        self.Timeframe_list = [
            "M1", "M5", "M15", "M30", "H1", "D1", "W1", "MN1"]
        self.items = {}
        self.H_H = set()
        self.L_L = set()

        # Settings
        self.pair = pair
        self.timeframe = timeframe
        self.lot = lot
        self.sl = sl
        self.tp = tp
        self.deviation = deviation
        self.magic = 112026457

        # BOTS
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

        # Regulators
        self.connection = False
        self.run_rt = False
        self.track = False
        self.auto_trade = False

    # Initialize MetaTrader 5 n Log Client In
    # ==========================================
    def Connect(self):
        if self.Account and self.Password and self.Server:
            if not mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe", login=self.Account, password=self.Password, server=self.Server, timeout=60000, portable=False):
                return {"status": False, "message": mt5.last_error()}
            else:
                # Return
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
            self.pair, self.Timeframe_Dict[self.timeframe], 0, 50)

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
        _data = {}
        _data["positions"] = []
        _data["orders"] = []
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
            _data["positions"].append(data)
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
            _data["orders"].append(data)

        return _data

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
        while self.run_rt:
            data = mt5.copy_rates_from_pos(
                self.pair, self.Timeframe_Dict[self.timeframe], 0, 1440)

            cpArr = []

            for i in range(1440):
                cpArr.append(data[i][4])

            self.rsi = tpy.rsi(numpy.array(cpArr), 14)[-1]

            # Wait
            sleep(5)

    # Track Trade
    # ============================================================================

    def track_Trade(self):
        while self.track:
            # Get Orders
            positions = mt5.positions_get()

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

                            # Update number of positions
                            if type == mt5.ORDER_TYPE_SELL:
                                self.bot_B["trades"] -= 1
                            else:
                                self.bot_S["trades"] -= 1

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

                            # Update number of positions
                            if type == mt5.ORDER_TYPE_SELL:
                                self.bot_B["trades"] -= 1
                            else:
                                self.bot_S["trades"] -= 1

                        # If Current Profit On Order Is Not Incrementing, Update count
                        if prop.profit > 0 and prop.profit < (3 * prop.volume):
                            self.items[prop.ticket] += 1

                    # If Order Is Not Being Tracked
                    else:
                        # Check If In Loss And If Current Loss Is 2 Pips Or Greater, Below 0.
                        # If Above Requirements Meet, Close Trade.
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

                            # Update number of positions
                            if type == mt5.ORDER_TYPE_SELL:
                                self.bot_B["trades"] -= 1
                            else:
                                self.bot_S["trades"] -= 1

                        # Check If Current Profit Is Above 2 Pips,
                        # Add To Tracked Orders
                        elif prop.profit > (2 * prop.volume):
                            self.items[prop.ticket] = 1

            # Wait
            sleep(1)

    # Fetch return Prices
    # ============================================================================

    def fetcher(self):
        while self.run_rt:
            # Fetch Candles
            data = mt5.copy_rates_from_pos(
                self.pair, self.Timeframe_Dict[self.timeframe], 1, self.candles[self.timeframe] + 6)

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

            # Wait
            sleep(60 * 60 * 12)

    # Auto Trader 1
    # ============================================================================

    def auto_T1(self, price, no_of_trades, pattern):
        # Update Status
        self.bot_S["active"] = True

        print("BOT_S IS ACTIVE")

        # Initialize
        while self.bot_S["trades"] < int(no_of_trades) / 2:
            # Get Current Tick Info
            info = (mt5.symbol_info(self.pair))._asdict()

            # Check If Current Price Is Either 5 pips below or 5 pips above
            if info["ask"] - price <= 0.5 or price - info["ask"] <= 0.5:
                # Define variable
                order = None

                # Place Order
                if int(pattern) == 1:
                    order = self.Instant_Sell_Order(info["ask"])

                if int(pattern) == 2:
                    order = self.Sell_Stop_Order(info["ask"])

                if int(pattern) == 3:
                    order = self.Double_Instant_Order(
                        (info["ask"] + info["bid"]) / 2)

                if int(pattern) == 4:
                    order = self.Double_Pending_Order(
                        (info["ask"] + info["bid"]) / 2)

                if order["status"]:
                    # Update Last Traded Ask Price
                    self.bot_S["price"] = info["ask"]

                    # Update Number of Positions Opened
                    self.bot_S["trades"] += 1

                # Update Status
                self.bot_S["active"] = False

                # Return
                return order

            # Wait
            sleep(10)

    # Auto Trader 2
    # ============================================================================

    def auto_T2(self, price, no_of_trades, pattern):
        # Update Status
        self.bot_B["active"] = True

        print("BOT_B IS ACTIVE")

        # Initialize
        while self.bot_B["trades"] < int(no_of_trades) / 2:
            # Get Current Tick Info
            info = (mt5.symbol_info(self.pair))._asdict()

            # Check If Current Price Is Either 5 pips below or 5 pips above
            if info["bid"] - price <= 0.5 or price - info["bid"] <= 0.5:
                # Define variable
                order = None

                # Place Order
                if int(pattern) == 1:
                    order = self.Instant_Buy_Order(info["bid"])

                if int(pattern) == 2:
                    order = self.Buy_Stop_Order(info["bid"])

                if int(pattern) == 3:
                    order = self.Double_Instant_Order(
                        (info["ask"] + info["bid"]) / 2)

                if int(pattern) == 4:
                    order = self.Double_Pending_Order(
                        (info["ask"] + info["bid"]) / 2)

                if order["status"]:
                    # Update Last Traded Bid Price
                    self.bot_B["price"] = info["bid"]

                    # Update Number of Positions Opened
                    self.bot_B["trades"] += 1

                # Update Status
                self.bot_B["active"] = False

                # Return
                return order

            # Wait
            sleep(10)

    # Start Auto Trading
    # ============================================================================

    def start_auto(self, no_of_trades, pattern):
        # Get Existing Orders
        orders = mt5.positions_get()

        if len(orders) > 0:
            # Update Counter
            for prop in orders:
                if prop.type == 0:
                    self.bot_B["trades"] += 1
                else:
                    self.bot_S["trades"] += 1

        while self.auto_trade:
            # Check RSI
            if self.rsi > 0:
                # Get Current Tick Info
                info = (mt5.symbol_info(self.pair))._asdict()

                # Check If Database Has Been Updated And Number Of Existing Orders Are Not Greater Than Required
                if len(self.H_H) > 0 and len(self.L_L) > 0:
                    # Start HP Monitor
                    if info["ask"] in self.H_H and self.bot_B["trades"] < int(no_of_trades) / 2 and not self.bot_S["active"]:
                        if info["ask"] - self.bot_B["price"] > 0.3 and self.rsi >= 65:
                            s_a1 = threading.Thread(target=self.auto_T1, args=(
                                info["ask"], no_of_trades, pattern,), daemon=False)
                            s_a1.start()

                    # Start LP Monitor
                    if info["bid"] in self.L_L and self.bot_S["trades"] < int(no_of_trades) / 2 and not self.bot_B["active"]:
                        if self.bot_S["price"] - info["bid"] > 0.3 and self.rsi <= 35:
                            s_a2 = threading.Thread(target=self.auto_T2, args=(
                                info["bid"], no_of_trades, pattern,), daemon=False)
                            s_a2.start()

            # Wait
            sleep(20)
