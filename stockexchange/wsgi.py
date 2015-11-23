import requests
from flask import Flask, jsonify, session, render_template

app = Flask(__name__)
app.secret_key = "Super secret key"

def getSymbolData(symbol):
    out = {"message": "OK", "symbol": symbol}
    try:
        r = requests.get("http://careers-data.benzinga.com/rest/richquote", params={"symbols": symbol})
        j = r.json()[symbol]
        if ("error" in j):
            out["message"] = j["error"]["message"]
        else:
            out["name"] = j["name"]
            out["askPrice"] = j["askPrice"]
            out["bidPrice"] = j["bidPrice"]
    except Exception, e:
        app.logger.error("getQuoteData error: " + str(e))
        out["message"] = "Unknown error"
    return out

def initSession():
    if ("portfolio" not in session):
        session["portfolio"] = {}
        session["balance"] = 100000.0

@app.route("/api/buy/<symbol>/<quantity>")
def api_buy(symbol, quantity):
    initSession()
    data = getSymbolData(symbol)
    out = {"message": "OK"}
    if (data["message"] != "OK"):
        out["message"] = "Symbol error: " + data["message"]
    else:
        session["portfolio"].setdefault(symbol, {"quantity": 0, "lastprice": 0})
        try:
            quantity = int(quantity)
            if (quantity < 0):
                out["message"] = "Invalid quantity"
            else:
                price = quantity * data["askPrice"]
                if (price <= session["balance"]):
                    session["portfolio"][symbol]["quantity"] += quantity
                    session["portfolio"][symbol]["lastprice"] = data["askPrice"]
                    session["portfolio"][symbol]["name"] = data["name"]
                    session["balance"] -= price
                else:
                    out["message"] = "Not enough funds"
        except ValueError:
            out["message"] = "Invalid quantity"
    return jsonify(**out)

@app.route("/api/sell/<symbol>/<quantity>")
def api_sell(symbol, quantity):
    initSession()
    out = {"message": "OK"}
    if (symbol not in session["portfolio"]):
        out["message"] = "No shares"
    else:
        try:
            quantity = int(quantity)
            if (quantity < 0):
                out["message"] = "Invalid quantity"
            else:
                s = session["portfolio"][symbol]
                if (s["quantity"] >= quantity):
                    data = getSymbolData(symbol)
                    out = {"message": "OK"}
                    if (data["message"] != "OK"):
                        out["message"] = "Symbol error: " + data["message"]
                    else:
                        s["quantity"] -= quantity
                        session["balance"] += data["bidPrice"] * quantity
                        if (s["quantity"] == 0):
                            del session["portfolio"][symbol]
                else:
                    out["message"] = "Not enough shares"
        except ValueError:
            out["message"] = "Invalid quantity"
    return jsonify(**out)

@app.route("/api/portfolio")
def api_portfolio():
    initSession()
    out = {}
    out["balance"] = session["balance"]
    out["portfolio"] = session["portfolio"]
    return jsonify(**out)

@app.route("/api/info/<symbol>")
def api_info_symbol(symbol):
    return jsonify(**getSymbolData(symbol))

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

