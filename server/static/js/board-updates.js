$(document).ready(function () {
	$(".led-button").click(changeLed);
	$(".led-set-button").click(changeLedSet);
	$("#rgbModalSave").click(saveRgbLed);
	$(".pulse-button").click(pulseModalShow)
	$("#pulseModalOff").click(pulseOff);
	$("#pulseModalOn").click(pulseOn);
});

var rgbSaveStr = undefined,
	rgbSaveSuccess = undefined,
	pulse = undefined;

var changeLed = function (e) {
	var myMatches = $(this).attr("id").match(/\d+/g);
	if (myMatches === undefined || myMatches.length != 2) {
		console.error($(this).attr("id") + " id not in led-setId-ledId format");
		return;
	}

	var setId = parseInt(myMatches[0]),
		ledId = parseInt(myMatches[1]),
		saveStr = "led-" + setId + "-" + ledId;
	rgbSet("Set RGB LED " + ledId + " in Set " + setId, $(this).attr("id"), saveStr, function () {
		// Success
		var rgbStr = "rgb(" + $("#rgbModalR").val() + "," + $("#rgbModalG").val() + "," + $("#rgbModalB").val() + ")";
		$("#" + saveStr).css("background-color", rgbStr);
	});
};

var changeLedSet = function (e) {
	var myMatches = $(this).attr("id").match(/\d+/g);
	if (myMatches === undefined || myMatches.length != 1) {
		console.error($(this).attr("id") + " id not in led-set-setId format");
		return;
	}

	var setId = parseInt(myMatches[0]),
		saveStr = "led-set-" + setId;
	rgbSet("Set RGB LEDs for Set " + setId, $(this).attr("id"), saveStr, function () {
		// Success
		var rgbStr = "rgb(" + $("#rgbModalR").val() + "," + $("#rgbModalG").val() + "," + $("#rgbModalB").val() + ")";
		$("#" + saveStr).css("background-color", rgbStr);

		var ledId = 0,
			currentLed = document.getElementById("led-" + setId + "-" + ledId);
		while (currentLed !== null) {
			$("#led-" + setId + "-" + ledId).css("background-color", rgbStr);
			ledId++;
			currentLed = document.getElementById("led-" + setId + "-" + ledId);
		}
	});
};

var rgbSet = function (title, idToCopyRGB, saveStr, success) {
	$("#rgbModalTitle").html(title);
	copyRGB(idToCopyRGB);
	$("#rgbModal").modal("show");
	rgbSaveStr = saveStr;
	rgbSaveSuccess = success;
};

var copyRGB = function (id) {
	var rgb = $("#" + id).css("background-color");
		matches = rgb.match(/\d+/g);

	if (matches == undefined || matches.length < 3) {
		console.error("Wrong number of rgb number matches");
		return;
	}

	$("#rgbModalR").val(parseInt(matches[0]));
	$("#rgbModalR").css("background-color", "#ffffff");
	$("#rgbModalR").css("color", "#000000");

	$("#rgbModalG").val(parseInt(matches[1]));
	$("#rgbModalG").css("background-color", "#ffffff");
	$("#rgbModalG").css("color", "#000000");

	$("#rgbModalB").val(parseInt(matches[2]));
	$("#rgbModalB").css("background-color", "#ffffff");
	$("#rgbModalB").css("color", "#000000");
};

var invalidUChar = function (id) {
	var value = parseInt($(id).val());

	if (value < 0 || value > 255) {
		$(id).css("background-color", "#993339");
		$(id).css("color", "#d98e93");
		return true;
	} else {
		$(id).css("background-color", "#ffffff");
		$(id).css("color", "#000000");
		return false;
	}
};

var saveRgbLed = function () {
	if (rgbSaveStr === undefined) {
		console.error("Cannot save without speciying save string");
		return;
	}

	var invalidR = invalidUChar("#rgbModalR"),
		invalidG = invalidUChar("#rgbModalG"),
		invalidB = invalidUChar("#rgbModalB");

	if (invalidR || invalidG || invalidB) {
		console.error("Incorrect RGB values");
		return;
	}

	var rgbData = {
		"update-key": rgbSaveStr, 
		"update-value": $("#rgbModalR").val() + "," + $("#rgbModalG").val() + "," + $("#rgbModalB").val()
	};

	$.ajax({
		url: "/board/" + $("#hiddenBoardName").val(),
		type: "POST",
		data: rgbData,
		success: function (data) {
			$("#rgbModal").modal("hide");
			rgbSaveSuccess();
		},
		error: function () {
			console.error("Unable to save RGB data");
		}
	});
};


var pulseOn = function () {
	var setId = parseInt($("#hiddenPulseSet").val());
	pulse[setId].pulsing = true;
	pulse[setId].ms = parseInt($("#pulseModalMS").val());
	$("#pulseModal").modal("hide");
	$("#pulse-" + setId).removeClass("btn-danger");
	$("#pulse-" + setId).addClass("btn-success");
	pulseRepeat(setId);
};

var pulseOff = function () {
	var setId = parseInt($("#hiddenPulseSet").val());
	pulse[setId].pulsing = false;
	$("#pulseModal").modal("hide");
	$("#pulse-" + setId).removeClass("btn-success");
	$("#pulse-" + setId).addClass("btn-danger");
};

var randUChar = function () {
	return Math.floor(Math.random() * 256);
}

var pulseRepeat = function (setId) {
	var boardUrl = "/board/" + $("#hiddenBoardName").val();
	$.ajax({
		url: boardUrl,
		type: "GET",
		success: function (data) {
			var rgb_leds = data["rgb-led-groups"][setId]["rgb-leds"],
				updateStrBase = "led-" + setId + "-";
			for (var i = rgb_leds.length - 1; i > 0; i--) {
				var rgb = rgb_leds[i - 1]["r"] + "," + rgb_leds[i - 1]["g"] + "," + rgb_leds[i - 1]["b"];
				$.ajax({
					url: boardUrl,
					type: "POST",
					data: {"update-key": updateStrBase + i, "update-value": rgb}
				});

				$("#" + updateStrBase + i).css("background-color", "rgb(" + rgb + ")");
			}

			// Random first LED
			var rgb = randUChar() + "," + randUChar() + "," + randUChar();
			$.ajax({
				url: boardUrl,
				type: "POST",
				data: {"update-key": updateStrBase + i, "update-value": rgb},
			});
			$("#" + updateStrBase + "0").css("background-color", "rgb(" + rgb + ")");

			// Set timeout
			if (pulse[setId].pulsing) {
				setTimeout(function () {
					pulseRepeat(setId);
				}, pulse[setId].ms);
			}
		},
		error: function () {
			console.error("error getting board status");
		}
	});
};

var initPulse = function () {
	pulse = []
	for (var i = 0; i < parseInt($("#hiddenNumSets").val()); i++) {
		pulse.push({pulsing: false, ms: 0});
	}
};


var pulseModalShow = function () {
	var myMatches = $(this).attr("id").match(/\d+/g);
	if (myMatches === undefined || myMatches.length != 1) {
		console.error($(this).attr("id") + " id not in pulse-setId format");
		return;
	}

	if (pulse === undefined) {
		initPulse();
	}

	var setId = parseInt(myMatches[0]);
	$("#hiddenPulseSet").val(setId);
	$("#pulseModalTitle").html("Pulse LEDs across Set " + setId);
	if (pulse[setId].pulsing) {
		$("#pulseModalOn").hide();
		$("#pulseModalOff").show();
	} else {
		$("#pulseModalOff").hide();
		$("#pulseModalOn").show();
	}

	$("#pulseModal").modal("show");
};