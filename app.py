# Import Dependencies
# ==============================================================================
from flask import Flask, jsonify, request, render_template, make_response
from mt5.phantom import bot

# Instantiate
# ==============================================================================
app = Flask(__name__)

# Routes
# ==============================================================================


# App
@app.route("/", methods=["GET"])
def home():
    if request.method == "GET":
        return render_template("app.html")
    return


# Auth
@app.route("/auth", methods=["POST"])
def auth():
    global Trader
    if request.method == "POST":
        data = request.get_json(force=True)
        Trader = bot(data["account"], data["password"], data["server"])
        account = Trader.Connect()
        if account["status"]:
            response = make_response(
                jsonify(
                    {"message": account["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
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


# Get pairs
@app.route("/pairs", methods=["GET"])
def pairs():
    if request.method == "GET":
        return jsonify(Trader.Get_Currency_Pairs())
    return


# Get timeframe
@app.route("/timeframe", methods=["GET"])
def timeframes():
    if request.method == "GET":
        return jsonify(Trader.Timeframe_list)
    return


# Get Chart Data
@app.route("/chartData", methods=["POST"])
def chartData():
    if request.method == "POST":
        data = request.get_json(force=True)
        return jsonify(Trader.HLOC(data["timeframe"], data["pair"]))
    return


# Get Currency pair info
@app.route("/bid_ask", methods=["POST"])
def bid_ask():
    if request.method == "POST":
        data = request.get_json(force=True)
        return jsonify(Trader.Get_Currency_Pair_Info(data["pair"]))
    return


# Buy Order
@app.route("/buy_order", methods=["POST"])
def buy_order():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Instant_Buy_Order(
            data["lot_size"], data["pair"], data["deviation"], data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Buy Stop Order
@app.route("/buy_stop_order", methods=["POST"])
def buy_stop_order():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Buy_Stop_Order(data["lot_size"], data["pair"], data["deviation"],
                                   data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Sell Order
@app.route("/sell_order", methods=["POST"])
def sell_order():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Instant_Sell_Order(
            data["lot_size"], data["pair"], data["deviation"], data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Sell Order
@app.route("/sell_stop_order", methods=["POST"])
def sell_stop_order():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Sell_Stop_Order(data["lot_size"], data["pair"], data["deviation"],
                                    data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Double Instant Order
@app.route("/double_instant", methods=["POST"])
def double_instant():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Double_Instant_Order(
            data["lot_size"], data["pair"], data["deviation"], data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message_B": pd["message_B"],
                        "message_S": pd["message_S"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Double Pending Order
@app.route("/double_pending", methods=["POST"])
def double_pending():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.Double_Pending_Order(
            data["lot_size"], data["pair"], data["deviation"], data["stop_loss"], data["take_profit"], data["price"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message_B": pd["message_B"],
                        "message_S": pd["message_S"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Trades
@app.route("/trades", methods=["GET"])
def trades():
    if request.method == "GET":
        return jsonify(Trader.Orders())
    return


# Close Instant Order
@app.route("/close_itr", methods=["POST"])
def close_itr():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.close_Instant_Orders(data["index"], data["deviation"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Close Pending Order
@app.route("/close_ptr", methods=["POST"])
def close_ptr():
    if request.method == "POST":
        data = request.get_json(force=True)
        pd = Trader.close_Pending_Orders(data["ticket"])
        if pd["status"]:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            response = make_response(
                jsonify(
                    {"message": pd["message"]}
                ),
                400,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    return


# Start Auto trader
@app.route("/auto_trade", methods=["POST"])
def autoTrade():
    if request.method == "POST":
        data = request.get_json(force=True)
        Trader.auto_trade = True
        Trader.start_auto(data["pair"], data["lot"], data["ntr"])
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
@app.route("/sta_trade", methods=["GET"])
def sta_trade():
    if request.method == "GET":
        Trader.auto_trade = False
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
    app.run()
