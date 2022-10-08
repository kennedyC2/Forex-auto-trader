# Import Dependencies
# ==============================================================================
from flask import Flask, jsonify, request, render_template, make_response
from mt5.phantom import BBB
import threading

# Instantiate
# ==============================================================================
app = Flask(__name__)

# ==============================================================================
#                                ROUTES
# ==============================================================================


# App
# ==============================================================================
@app.route("/", methods=["GET"])
def home():
    if request.method == "GET":
        return render_template("app.html")
    return


# Auth
# ==============================================================================
@app.route("/auth", methods=["POST"])
def auth():
    global Trader

    if request.method == "POST":
        data = request.get_json(force=True)

        # Instantiate BBB
        Trader = BBB(
            data["account"], data["password"], data["server"], data["timeframe"], data["lot"], data["sl"], data["tp"], data["deviation"])
        account = Trader.Connect()

        # Send Response If Successfully logged In
        if account["status"]:
            # Get Pair
            pairs = Trader.Get_Currency_Pairs()

            # Set Pair
            Trader.pair = pairs[0]

            # Set kick
            Trader.run_rt = True
            Trader.track = True

            # Trade Tracker Thread
            global t_trade
            t_trade = threading.Thread(
                target=Trader.track_Trade, args=(), daemon=False)

            # RSI Thread
            global s_RSI
            s_RSI = threading.Thread(
                target=Trader.c_RSI, args=(), daemon=False)

            # Fetcher Thread
            global s_fetcher
            s_fetcher = threading.Thread(
                target=Trader.fetcher, args=(), daemon=False)

            # Start Thread
            t_trade.start()

            # Start RSI Thread
            s_RSI.start()

            # Start Fetcher Thread
            s_fetcher.start()

            response = make_response(
                jsonify(
                    {"message": account["message"], "pair": Trader.pair}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If Unsuccessful logging In
        else:
            response = make_response(
                jsonify(
                    {"message": account["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Get Currency Pairs
# ==============================================================================
@app.route("/pairs", methods=["GET"])
def pairs():
    if request.method == "GET":
        return jsonify(Trader.Get_Currency_Pairs())
    return


# Get timeframe
# ==============================================================================
@app.route("/timeframe", methods=["GET"])
def timeframes():
    if request.method == "GET":
        return jsonify(Trader.Timeframe_list)
    return


# Get Data For Candle Chart
# ==============================================================================
@app.route("/chartData", methods=["GET"])
def chartData():
    if request.method == "GET":
        return jsonify(Trader.HLOC())
    return


# Get Currency pair info
# ==============================================================================
@app.route("/bid_ask", methods=["GET"])
def bid_ask():
    if request.method == "GET":
        return jsonify(Trader.Get_Currency_Pair_Info())
    return


# Place Buy Order
# ==============================================================================
@app.route("/order/instant/buy", methods=["POST"])
def buy_order():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Instant_Buy_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If Unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Buy Stop Order
# ==============================================================================
@app.route("/order/pending/buy_stop", methods=["POST"])
def buy_stop_order():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Buy_Stop_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If Unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Sell Order
# ==============================================================================
@app.route("/order/instant/sell", methods=["POST"])
def sell_order():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Instant_Sell_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If Unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Sell Stop Order
# ==============================================================================
@app.route("/order/pending/sell_stop", methods=["POST"])
def sell_stop_order():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Sell_Stop_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If Unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Double Instant Order
# ==============================================================================
@app.route("/order/instant/double", methods=["POST"])
def double_instant():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Double_Instant_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message_B": order["message_B"],
                        "message_S": order["message_S"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Double Pending Order
# ==============================================================================
@app.route("/order/pending/double", methods=["POST"])
def double_pending():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Place Order
        order = Trader.Double_Pending_Order(data["price"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message_B": order["message_B"],
                        "message_S": order["message_S"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Trades
# ==============================================================================
@app.route("/orders", methods=["GET"])
def orders():
    if request.method == "GET":
        return jsonify(Trader.Orders())
    return


# Close Instant Order
# ==============================================================================
@app.route("/order/instant/close", methods=["POST"])
def close_instant():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Close Order
        order = Trader.close_Instant_Order(data["index"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Close Pending Order
# ==============================================================================
@app.route("/order/pending/close", methods=["POST"])
def close_pending():
    if request.method == "POST":
        data = request.get_json(force=True)

        # Close Order
        order = Trader.close_Pending_Order(data["ticket"])

        # Send Response If Successful
        if order["status"]:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # Send Response If unsuccessful
        else:
            response = make_response(
                jsonify(
                    {"message": order["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Start Auto trader
# ==============================================================================
@app.route("/order/auto/start", methods=["POST"])
def trade_start():
    if request.method == "POST":
        data = request.get_json(force=True)
        Trader.auto_trade = True

        # Start Thread
        global s_thread
        s_thread = threading.Thread(target=Trader.start_auto, args=(
            data["ntr"], data["ptn"]), daemon=False)

        s_thread.start()

        response = make_response(
            jsonify(
                {"message": "success"}
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    return


# Stop Auto Trade
# ==============================================================================
@app.route("/order/auto/stop", methods=["GET"])
def trade_stop():
    if request.method == "GET":
        Trader.auto_trade = False
        Trader.AvG = 0
        Trader.AvL = 0

        response = make_response(
            jsonify(
                {"message": "success"}
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    return


# Settings
# ==============================================================================
@app.route("/settings", methods=["POST"])
def settings():
    if request.method == "POST":
        # Stop Fetcher and RSI Calculator
        Trader.run_rt = False

        # Update Defaults
        data = request.get_json(force=True)
        Trader.pair = str(data["pair"])
        Trader.timeframe = str(data["timeframe"])
        Trader.lot = float(data["lot"])
        Trader.sl = float(data["sl"])
        Trader.tp = float(data["tp"])
        Trader.deviation = int(data["deviation"])

        # start Fetcher and RSI Calculator
        Trader.run_rt = True

        # RSI Thread
        s_RSI = threading.Thread(
            target=Trader.c_RSI, args=(), daemon=False)

        # Fetcher Thread
        s_fetcher = threading.Thread(
            target=Trader.fetcher, args=(), daemon=False)

        # Start RSI Thread
        s_RSI.start()

        # Start Fetcher Thread
        s_fetcher.start()

        # Send Response
        response = make_response(
            jsonify(
                {"message": "success"}
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    return

# Shutdown
# ==============================================================================


@app.route("/shutdown", methods=["GET"])
def shutdown():
    if request.method == "GET":
        Trader.auto_trade = False
        Trader.run_rt = False
        Trader.track = False

        response = make_response(
            jsonify(
                {"message": "success"}
            ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return response
    return


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)
