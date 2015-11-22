$(function() {
	getStock = function(stock) {
		$.getJSON("/api/info/" + stock, function(data) {
			if (data["message"] == "OK") {
				$("#quote-heading-text").html(data["name"] + " (" + data["symbol"] + ")");
				$("#quote-bid").html("$" + data["bidPrice"]);
				$("#quote-ask").html("$" + data["askPrice"]);
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

	handleSearch = function(e) {
		e.preventDefault();
		var sym = $("#search-input").val();
		if (sym != "") {
			getStock(sym);
		}
	};

	$("#search-form").on("submit", handleSearch);
	$("#search-input-btn").on("click", handleSearch);
});
