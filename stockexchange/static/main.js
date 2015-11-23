$(function() {
	account = {"balance": 0, "portfolio": []};

	getStock = function(stock) {
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
				$("#quote-owned").html(qty);
				$("#quote-info").show();
				$("#quote-heading").show();
				$("#quote-text").hide();
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
			$("#portfolio-heading-text").html("$" + data["balance"]);
			$("#portfolio-heading").show();
			account["portfolio"] = data["portfolio"];
			var tableRows = $("#portfolio-table > tbody > tr");
			tableRows.each(function(i, row) {
				$(row).remove();
			});
			for (var sym in account["portfolio"]) {
				var data = account["portfolio"][sym];
				var row = $("<tr>");
				row.append("<td>" + sym + "</td>");
				row.append("<td>" + data["name"] + "</td>");
				row.append("<td>" + data["quantity"] + "</td>");
				row.append("<td>" + data["lastprice"] + "</td>");
				row.append("<td><button data-symbol=\"" + sym + "\" class=\"portfolio-stock-button btn btn-default btn-xs\"><span class=\"glyphicon glyphicon-eye-open\"></span> View</button></td>");
				$("#portfolio-table > tbody").append(row);
			};
			$(".portfolio-stock-button").on("click", function(e) {
				getStock($(e.target).data("symbol"));
			});
			$("#portfolio-text").hide();
			$("#portfolio-table").show();
		});
	}

	handleSearch = function(e) {
		e.preventDefault();
		var sym = $("#search-input").val();
		if (sym != "") {
			getStock(sym);
		}
	};

	$("#search-form").on("submit", handleSearch);
	$("#search-input-btn").on("click", handleSearch);
	loadPortfolio();
});
