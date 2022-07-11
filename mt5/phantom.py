# Import Dependencies
import MetaTrader5 as mt5
import numpy
from datetime import datetime
from threading import Timer
from time import sleep, time


# Class Object
class bot:
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
        self.Timeframe_list = ["M1", "M5", "M15", "M30", "H1", ]
        self.items = {}
        self.H_H = set()
        self.L_L = set()
        self.auto_trade = False

    # Initialize MetaTrader 5
    # ==========================================

    def Connect(self):
        if self.Account and self.Password and self.Server:
            if not mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe", login=self.Account, password=self.Password, server=self.Server, timeout=60000, portable=False):
                return {"status": False, "message": mt5.last_error()}
            else:
                self.track_Trade()
                return {"status": True, "message": "success"}

    # Get Symbols
    # ===================================================================================

    def Get_Currency_Pairs(self):
        pairs = mt5.symbols_get()

        # List
        data = []
        for prop in pairs:
            data.append(prop._asdict()["name"])

        return data

    # Get currency pair information
    # ===================================================================================

    def Get_Currency_Pair_Info(self, currency_pair):
        info = mt5.symbol_info(currency_pair)

        if not info.visible:
            if not mt5.symbol_select(currency_pair, True):
                print("Failed to add {}".format(currency_pair))
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

    def HLOC(self, timeframe, pair):
        data = mt5.copy_rates_from_pos(
            pair, self.Timeframe_Dict[timeframe], 0, 60)

        array = []

        for prop in data:
            arr = []
            dt = datetime.fromtimestamp(prop[0]).strftime("%Y-%m-%d, %H:%M")
            arr.append(str(dt.split(",")[1]))
            arr.append(numpy.float64(prop[3]))
            arr.append(numpy.float64(prop[1]))
            arr.append(numpy.float64(prop[4]))
            arr.append(numpy.float64(prop[2]))

            # Send
            array.append(arr)

        return array

    # Get active trades
    # ===================================================================================
    def Orders(self):
        positions = mt5.positions_get()
        orders = mt5.orders_get()
        _data = {}
        _data["positions"] = []
        _data["orders"] = []
        count = 0

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

    def Instant_Buy_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_BUY,
            "price": float(price),
            "sl": float(price) - float(stop_loss),
            "tp": float(price) + float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
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

    def Buy_Stop_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": float(price),
            "sl": float(price) - float(stop_loss),
            "tp": float(price) + float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
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

    def Instant_Sell_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_SELL,
            "price": float(price),
            "sl": float(price) + float(stop_loss),
            "tp": float(price) - float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
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

    def Sell_Stop_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": float(price),
            "sl": float(price) + float(stop_loss),
            "tp": float(price) - float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
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

    def Double_Instant_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):

        request_B = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_BUY,
            "price": float(price),
            "sl": float(price) - float(stop_loss),
            "tp": float(price) + float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        request_S = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_SELL,
            "price": float(price),
            "sl": float(price) + float(stop_loss),
            "tp": float(price) - float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello World",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response_B = mt5.order_send(request_B)
        response_S = mt5.order_send(request_S)

        # Validate
        if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message_B": response_B.comment, "message_S": response_S.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Place Buy-Stop and Sell-Stop Order
    # ===================================================================================

    def Double_Pending_Order(self, lot_size, pair, deviation, stop_loss, take_profit, price):

        request_B = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": float(price),
            "sl": float(price) - float(stop_loss),
            "tp": float(price) + float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        request_S = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": float(lot_size),
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": float(price),
            "sl": float(price) + float(stop_loss),
            "tp": float(price) - float(take_profit),
            "deviation": int(deviation),
            "magic": 112026457,
            "comment": "Hello WOrld",
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send Order
        response_B = mt5.order_send(request_B)
        response_S = mt5.order_send(request_S)

        # Validate
        if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": False, "message_B": response_B.comment, "message_S": response_S.comment}
        else:
            return {"status": True, "message": self.Orders()}

    # Close Instant Orders
    # ===================================================================================

    def close_Instant_Orders(self, index, deviation):
        orders = mt5.positions_get()
        i = 0

        while i < len(orders):
            if int(index) == i:
                ticket = orders[i].ticket

                # Check if trade type is BUY
                if orders[i].type == 0:
                    symbol = orders[i].symbol
                    price = mt5.symbol_info_tick(
                        symbol).ask if orders[i].type == 0 else mt5.symbol_info_tick(symbol).bid
                    lot = orders[i].volume

                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_SELL,
                        "position": ticket,
                        "price": price,
                        "deviation": deviation,
                        "magic": 112026457,
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

                # Check if trade type is SELL
                if orders[i].type == 1:
                    symbol = orders[i].symbol
                    price = mt5.symbol_info_tick(
                        symbol).ask if orders[i].type == 0 else mt5.symbol_info_tick(symbol).bid
                    lot = orders[i].volume

                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_BUY,
                        "position": ticket,
                        "price": price,
                        "deviation": deviation,
                        "magic": 112026457,
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
    def close_Pending_Orders(self, ticket):
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

    # Track Trade
    # ============================================================================
    def track_Trade(self):
        Timer(0.5, self.track_Trade).start()
        positions = mt5.positions_get()

        if len(positions) > 0:
            for prop in positions:
                if prop.ticket in self.items:
                    if prop.profit > self.items[prop.ticket]:
                        self.items[prop.ticket] = prop.profit
                        print("updated ticket:", prop.ticket,
                              "profit to", prop.profit)
                    elif prop.profit > 0.2 and prop.profit <= (self.items[prop.ticket] - (3 * prop.volume)):
                        print("saved profit minus current =",
                              self.items[prop.ticket] - prop.profit)
                        type = mt5.ORDER_TYPE_SELL if prop.type == 0 else mt5.ORDER_TYPE_BUY
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": prop.symbol,
                            "volume": float(prop.volume),
                            "type": type,
                            "position": prop.ticket,
                            "price": prop.price_current,
                            "deviation": 20,
                            "magic": 112026457,
                            "comment": "Hello World",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_FOK,
                        }

                        # Close Order
                        mt5.order_send(request)
                        del self.items[prop.ticket]
                    elif prop.profit <= (0 - (3 * prop.volume)):
                        type = mt5.ORDER_TYPE_SELL if prop.type == 0 else mt5.ORDER_TYPE_BUY
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": prop.symbol,
                            "volume": float(prop.volume),
                            "type": type,
                            "position": prop.ticket,
                            "price": prop.price_current,
                            "deviation": 20,
                            "magic": 112026457,
                            "comment": "Hello World",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_FOK,
                        }

                        # Close Order
                        mt5.order_send(request)
                        del self.items[prop.ticket]
                    else:
                        pass
                else:
                    if prop.profit <= (0 - (3 * prop.volume)):
                        type = mt5.ORDER_TYPE_SELL if prop.type == 0 else mt5.ORDER_TYPE_BUY
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": prop.symbol,
                            "volume": float(prop.volume),
                            "type": type,
                            "position": prop.ticket,
                            "price": prop.price_current,
                            "deviation": 20,
                            "magic": 112026457,
                            "comment": "Hello World",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_FOK,
                        }

                        # Close Order
                        mt5.order_send(request)
                    elif prop.profit > (2 * prop.volume):
                        self.items[prop.ticket] = prop.profit
                    else:
                        pass

    # Fetcher
    # ============================================================================
    def fetcher(self, pair):
        timestamp = ["M1", "M15", "M30", "H1"]
        candles = [2880, 192, 96, 48]

        for e in range(4):
            data = mt5.copy_rates_from_pos(
                pair, self.Timeframe_Dict[timestamp[e]], 1, candles[e] + 6)

            for i in range(len(data)):
                count = 0
                if (i <= len(data) - 6):
                    for j in range(1, 6):
                        if data[i][2] - data[i + j][2] >= 0.5 and data[i + j][4] < data[i + j][1]:
                            count = count + 1

                        if count >= 4:
                            self.H_H.add(data[i][2])
                else:
                    break

            for i in range(1, len(data)):
                count = 0
                if (i <= len(data) - 6):
                    for j in range(1, 6):
                        if data[i + j][3] - data[i][3] >= 0.5 and data[i + j][4] > data[i + j][1]:
                            count = count + 1

                    if count >= 5:
                        self.L_L.add(data[i][3])
                else:
                    break

    # Auto Trader 1
    # ============================================================================

    def auto_T1(self, currency_pair, lot, no_of_trades):
        orders = mt5.positions_get()
        existing = set()

        for i in range(5, 0, -1):
            for prop in orders:
                existing.add(float(prop.price_open) + float(i/10))

        if len(self.H_H) > 0 and len(orders) <= int(no_of_trades):
            info = (mt5.symbol_info(currency_pair))._asdict()

            for i in range(5, 0, -1):
                if info["bid"] + (i/10) in self.H_H and info["bid"] + (i/10) not in existing:
                    request_B = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": currency_pair,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": float(info["bid"] + (i/10)),
                        "sl": float(info["bid"] + (i/10)) - float(10),
                        "tp": float(info["bid"] + (i/10)) + float(10),
                        "deviation": int(20),
                        "magic": 112026457,
                        "comment": "Hello WOrld",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    request_S = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": currency_pair,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": float(info["bid"] + (i/10)),
                        "sl": float(info["bid"] + (i/10)) + float(10),
                        "tp": float(info["bid"] + (i/10)) - float(10),
                        "deviation": int(20),
                        "magic": 112026457,
                        "comment": "Hello World",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    # Send Order
                    response_B = mt5.order_send(request_B)
                    response_S = mt5.order_send(request_S)
                    print(response_B.comment)
                    print(response_S.comment)

                    # Validate
                    if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
                        print("message_Buy", response_B.comment,
                              "message_Sell", response_S.comment)

    # Auto Trader 2
    # ============================================================================

    def auto_T2(self, currency_pair, lot, no_of_trades):
        orders = mt5.positions_get()
        existing = set()

        for i in range(5, 0, -1):
            for prop in orders:
                existing.add(float(prop.price_open) - float(i/10))

        if len(self.L_L) > 0 and len(orders) <= int(no_of_trades):
            info = (mt5.symbol_info(currency_pair))._asdict()

            for i in range(5, 0, -1):
                if info["ask"] - (i/10) in self.L_L and info["bid"] + (i/10) not in existing:
                    request_B = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": currency_pair,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": float(info["ask"] - (i/10)),
                        "sl": float(info["ask"] - (i/10)) - float(10),
                        "tp": float(info["ask"] - (i/10)) + float(10),
                        "deviation": int(20),
                        "magic": 112026457,
                        "comment": "Hello WOrld",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    request_S = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": currency_pair,
                        "volume": float(lot),
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": float(info["ask"] - (i/10)),
                        "sl": float(info["ask"] - (i/10)) + float(10),
                        "tp": float(info["ask"] - (i/10)) - float(10),
                        "deviation": int(20),
                        "magic": 112026457,
                        "comment": "Hello World",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    # Send Order
                    response_B = mt5.order_send(request_B)
                    response_S = mt5.order_send(request_S)
                    print(response_B.comment)
                    print(response_S.comment)

                    # Validate
                    if response_B.retcode != mt5.TRADE_RETCODE_DONE and response_S.retcode != mt5.TRADE_RETCODE_DONE:
                        print("message_Buy", response_B.comment,
                              "message_Sell", response_S.comment)

    # Start Auto Trading
    # ============================================================================

    def start_auto(self, currency_pair, lot, no_of_trades):
        # Populate Prices
        self.fetcher(currency_pair)

        while self.auto_trade:
            # Start HP Monitor
            self.auto_T1(currency_pair, lot, no_of_trades)

            # Start LP Monitor
            self.auto_T2(currency_pair, lot, no_of_trades)

            sleep(2)
