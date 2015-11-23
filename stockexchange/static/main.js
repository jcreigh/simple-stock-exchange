$(function() {
	account = {"balance": 0, "portfolio": []};

	doBuy = function(stock, quantity) {
		$("#quote-alert").hide();
		$.getJSON("/api/buy/" + stock + "/" + quantity, function(data) {
			if (data["message"] != "OK") {
				$("#quote-alert-text").html(data["message"]);
				$("#quote-alert").show();
			}
			loadPortfolio();
		});
	};

	doSell = function(stock, quantity) {
		$("#quote-alert").hide();
		$.getJSON("/api/sell/" + stock + "/" + quantity, function(data) {
			if (data["message"] != "OK") {
				$("#quote-alert-text").html(data["message"]);
				$("#quote-alert").show();
			}
			loadPortfolio();
		});
	};

	getStock = function(stock) {
		$("#quote-alert").hide();
		$.getJSON("/api/info/" + stock, function(data) {
			if (data["message"] == "OK") {
				$("#quote-heading-text").html(data["name"] + " (" + data["symbol"] + ")");
				$("#quote-bid").html("$" + data["bidPrice"]);
				$("#quote-ask").html("$" + data["askPrice"]);
				var fromPortfolio = account["portfolio"][data["symbol"]];
				var qty = 0;
				if (fromPortfolio) {
					qty = fromPortfolio["quantity"];
				}
				$("#quote-button-sell").prop("disabled", qty == 0);
				$("#quote-input").val(0);
				$("#quote-input").data("symbol", data["symbol"]);
				$("#quote-owned").html(qty);
				$("#quote-info").show();
				$("#quote-heading").show();
				$("#quote-text").hide();
				handleChange();
			} else {
				$("#quote-text").html("Error: " + data["message"]);
				$("#quote-heading-text").html(data["symbol"]);
				$("#quote-info").hide();
				$("#quote-heading").show();
				$("#quote-text").show();
			}
		});
	};

	loadPortfolio = function() {
		$.getJSON("/api/portfolio", function(data) {
			account["balance"] = data["balance"];
			$("#portfolio-heading-text").html("$" + Math.round(data["balance"] * 100) / 100);
			$("#portfolio-heading").show();
			account["portfolio"] = data["portfolio"];
			var tableRows = $("#portfolio-table > tbody > tr");
			tableRows.each(function(i, row) {
				$(row).remove();
			});
			$("#quote-owned").html("0");
			for (var sym in account["portfolio"]) {
				var data = account["portfolio"][sym];
				if ($("#quote-input").data("symbol") == sym) {
					$("#quote-owned").html(data["quantity"]);
				}
				var row = $("<tr>");
				row.append("<td>" + sym + "</td>");
				row.append("<td>" + data["name"] + "</td>");
				row.append("<td>" + data["quantity"] + "</td>");
				row.append("<td>" + data["lastprice"] + "</td>");
				row.append("<td><button data-symbol=\"" + sym + "\" class=\"portfolio-stock-button btn btn-default btn-xs\"><span class=\"glyphicon glyphicon-eye-open\"></span> View</button></td>");
				$("#portfolio-table > tbody").append(row);
			};
			$(".portfolio-stock-button").on("click", function(e) {
				getStock($(e.target).closest("button").data("symbol"));
			});
			$("#portfolio-text").hide();
			$("#portfolio-table").show();
			handleChange();
		});
	}

	handleSearch = function(e) {
		e.preventDefault();
		var sym = $("#search-input").val();
		if (sym != "") {
			getStock(sym);
		}
	};

	handleChange = function(e) {
		var input = $("#quote-input");
		var symbol = input.data("symbol");
		var owned = 0;
		if (account["portfolio"][symbol] != undefined) {
			owned = account["portfolio"][symbol]["quantity"];
		}
		var quantity = input.val();
		$("#quote-button-sell").prop("disabled", quantity <= 0 || quantity > owned);
		$("#quote-button-buy").prop("disabled", quantity <= 0);
	}

	handleBuy = function(e) {
		var input = $("#quote-input");
		$("#quote-button-buy").prop("disabled", true);
		doBuy(input.data("symbol"), input.val());
	}

	handleSell = function(e) {
		var input = $("#quote-input");
		$("#quote-button-sell").prop("disabled", true);
		doSell(input.data("symbol"), input.val());
	}

	$("#search-form").on("submit", handleSearch);
	$("#search-input-btn").on("click", handleSearch);
	$("#quote-input").on("change", handleChange);
	$("#quote-input").on("keyup", handleChange);
	$("#quote-button-buy").on("click", handleBuy);
	$("#quote-button-sell").on("click", handleSell);

	loadPortfolio();
});
