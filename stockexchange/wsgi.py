# import os

import requests
from flask import Flask, jsonify

app = Flask(__name__)

def getSymbolData(symbol):
    out = {"error": None, "symbol": symbol}
    try:
        r = requests.get("http://careers-data.benzinga.com/rest/richquote", params={"symbols": symbol})
        j = r.json()[symbol]
        if ("error" in j):
            out["error"] = j["error"]["message"]
        else:
            out["name"] = j["name"]
            out["askPrice"] = j["askPrice"]
            out["bidPrice"] = j["bidPrice"]
    except Exception, e:
        app.logger.error("getQuoteData error: " + str(e))
        out["error"] = "Unknown error"
    return out

@app.route("/api/getsymbol/<symbol>")
def getsymbol(symbol):
    return jsonify(**getSymbolData(symbol))

if __name__ == "__main__":
    app.run(debug=True)
