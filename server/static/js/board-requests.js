$(document).ready(function () {
	$("#controlBoardRedirectForm").submit(enteredBoardName);
	$("#boardNameSubmit").attr("disabled", true);
	$("#boardName").on("input", toggleBoardNameSubmit);
});

// Redirect to board route
var enteredBoardName = function (e) {
	window.location.replace("/control-board/" + $("#boardName").val());
	e.preventDefault();
};

// Toggle whether the board name can be submitted
var toggleBoardNameSubmit = function() {
	if ($("#boardName").val().length <= 0) {
		// Disable
		$("#boardNameSubmit").attr("disabled", true);
	} else {
		$("#boardNameSubmit").removeAttr("disabled");
	}
};