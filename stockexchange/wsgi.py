import requests
from flask import Flask, jsonify, session, render_template

app = Flask(__name__)
app.secret_key = "Super secret key"

# Use Benzinga API to obtain quote information for a symbol
def getSymbolData(symbol):
    out = {"message": "OK", "symbol": symbol}
    try:
        r = requests.get("http://careers-data.benzinga.com/rest/richquote", params={"symbols": symbol})
        j = r.json()[symbol]
        if ("error" in j):
            out["message"] = j["error"]["message"]
        else:  # We don't need all the data
            out["name"] = j["name"]
            out["askPrice"] = j["askPrice"]
            out["bidPrice"] = j["bidPrice"]
    except Exception, e:
        app.logger.error("getSymbolData error: " + str(e))
        out["message"] = "Unknown error"
    return out

# Initialize session with an empty portfolio and a balance of $100,000.00
def initSession():
    if ("portfolio" not in session):
        session["portfolio"] = {}
        session["balance"] = 100000.0

# Buy a quantity of shares
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
            if (quantity < 0):  # Buying a negative quantity would be bad
                out["message"] = "Invalid quantity"
            else:
                price = quantity * data["askPrice"]
                if (price <= session["balance"]):  # Only act if we can afford it
                    session["portfolio"][symbol]["quantity"] += quantity
                    session["portfolio"][symbol]["lastprice"] = data["askPrice"]
                    session["portfolio"][symbol]["name"] = data["name"]
                    session["balance"] -= price
                else:
                    out["message"] = "Not enough funds"
        except ValueError:
            out["message"] = "Invalid quantity"
    return jsonify(**out)

# Sell a quantity of shares
@app.route("/api/sell/<symbol>/<quantity>")
def api_sell(symbol, quantity):
    initSession()
    out = {"message": "OK"}
    if (symbol not in session["portfolio"]):
        out["message"] = "No shares"
    else:
        try:
            quantity = int(quantity)
            if (quantity < 0):  # Selling a negative quantity would also be bad
                out["message"] = "Invalid quantity"
            else:
                s = session["portfolio"][symbol]
                if (s["quantity"] >= quantity):  # Only act if we have enough shares
                    data = getSymbolData(symbol)
                    out = {"message": "OK"}
                    if (data["message"] != "OK"):
                        out["message"] = "Symbol error: " + data["message"]
                    else:
                        s["quantity"] -= quantity
                        session["balance"] += data["bidPrice"] * quantity
                        if (s["quantity"] == 0):  # If we no longer have any shares, remove it from the portfolio
                            del session["portfolio"][symbol]
                else:
                    out["message"] = "Not enough shares"
        except ValueError:
            out["message"] = "Invalid quantity"
    return jsonify(**out)

# Return the current portfolio information
@app.route("/api/portfolio")
def api_portfolio():
    initSession()
    out = {}
    out["balance"] = session["balance"]
    out["portfolio"] = session["portfolio"]
    return jsonify(**out)

# Return quote information
@app.route("/api/info/<symbol>")
def api_info_symbol(symbol):
    return jsonify(**getSymbolData(symbol))

# Render and server the main html
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

