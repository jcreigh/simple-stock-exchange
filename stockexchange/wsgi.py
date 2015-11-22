import requests
from flask import Flask, jsonify, session

app = Flask(__name__)
app.secret_key = "Super secret key"

def getSymbolData(symbol):
    out = {"message": "OK", "symbol": symbol}
    try:
        r = requests.get("http://careers-data.benzinga.com/rest/richquote", params={"symbols": symbol})
        j = r.json()[symbol]
        if ("message" in j):
            out["message"] = j["message"]["message"]
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

@app.route("/api/buy/<symbol>/<count>")
def api_buy(symbol, count):
    initSession()
    data = getSymbolData(symbol)
    out = {"message": "OK"}
    if (data["message"] != "OK"):
        out["message"] = "Symbol error: " + data["message"]
    else:
        session["portfolio"].setdefault(symbol, {"count": 0, "lastprice": 0})
        try:
            count = int(count)
            price = count * data["askPrice"]
            if (price <= session["balance"]):
                session["portfolio"][symbol]["count"] += count
                session["portfolio"][symbol]["lastprice"] = data["askPrice"]
                session["balance"] -= price
            else:
                out["message"] = "Not enough funds"
        except ValueError:
            out["message"] = "Invalid count"
    return jsonify(**out)

@app.route("/api/sell/<symbol>/<count>")
def api_sell(symbol, count):
    initSession()
    out = {"message": "OK"}
    if (symbol not in session["portfolio"]):
        out["message"] = "No shares"
    else:
        try:
            count = int(count)
            s = session["portfolio"][symbol]
            if (s["count"] >= count):
                data = getSymbolData(symbol)
                out = {"message": "OK"}
                if (data["message"] != "OK"):
                    out["message"] = "Symbol error: " + data["message"]
                else:
                    s["count"] -= count
                    session["balance"] += data["bidPrice"] * count
                    if (s["count"] == 0):
                        del session["portfolio"][symbol]
            else:
                out["message"] = "Not enough shares"
        except ValueError:
            out["message"] = "Invalid count"
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


if __name__ == "__main__":
    app.run(debug=True)

