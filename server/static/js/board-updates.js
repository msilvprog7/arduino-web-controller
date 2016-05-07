/**
 * API to interact with the board
 */
var BoardAPI = (function () {
	var name,
		board;

	return {
		/**
		 * Base URL for boards
		 */
		BOARD_ROUTE: "/board/",

		/**
		 * Milliseconds till next board update/get
		 */
		RETRIEVE_TIMEOUT_MS: 100,

		/**
		 * Types of Controls
		 */
		TYPES: {
			/**
			 * RGB LED Groups
			 */
			RGB_LED_GROUPS: {
				name: "rgb-led-groups", 
				component: "rgb-led",
				components: "rgb-leds",
				group: true,
				parse: function (v) { return "rgb(" + v.r + "," + v.g + "," + v.b + ")"; }
			}
		},

		/**
		 * Initialize the board
		 */
		init: function (boardName) {
			if (boardName === undefined) {
				return;
			}

			name = boardName;
			board = {};
			BoardAPI.get();
		},

		/**
		 * Update a type of control on the board
		 */
		update: function (type, values) {
			board[type] = values;
		},

		/**
		 * Display board controls with current values
		 */
		display: function () {
			var typeParams,
				componentSelector;

			// Iterate over different board control types
			Object.keys(board).forEach(function (type) {
				typeParams = BoardAPI.TYPES[type];

				// Handle groups in the appropriate manner
				if (typeParams.group) {
					// Iterate over groups
					board[type].forEach(function (group, groupId) {
						componentSelector = "#" + typeParams.component + "-" + groupId + "-";
						// Iterate over items in groups
						group[typeParams.components].forEach(function (item, itemId) {
							$(componentSelector + itemId).css("background-color", typeParams.parse(item));
						});
					});
				} else {
					componentSelector = "#" + typeParams.component + "-";

					// Iterate over items
					board[type].forEach(function (item, itemId) {
						$(componentSelector + itemId).css("background-color", typeParams.parse(item));
					});
				}
			});
		},

		/**
		 * Customize the modal on the page
		 */
		modal: {
			set: function (title, body, saveFcn) {
				$("#modalTitle").html(title);
				$("#modalBody").html(body);
				$("#modalSave").click(function () { saveFcn(); });
			},

			show: function () {
				$("#modal").modal("show");
			},

			hide: function () {
				$("#modal").modal("hide");
			}
		},

		/**
		 * Controls that the website can use to modify the board
		 */
		controls: {
			/**
			 * For a Single RGB LED
			 */
			RGB_LED: {
				group: undefined,
				led: undefined,
				modalTitle: "Set the RGB LED",
				modalBody: "<p>R: <input id='modalR' type='number' min='0' max='255' /> G: <input id='modalG' type='number' min='0' max='255' /> B: <input id='modalB' type='number' min='0' max='255' /></p>",
				command: "rgb-led",

				/**
				 * Show the modal
				 */
				show: function (groupId, ledId) {
					BoardAPI.controls.RGB_LED.group = groupId;
					BoardAPI.controls.RGB_LED.led = ledId;
					BoardAPI.modal.set(BoardAPI.controls.RGB_LED.modalTitle, BoardAPI.controls.RGB_LED.modalBody, BoardAPI.controls.RGB_LED.modalSave);
					BoardAPI.modal.show();
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					var intValues = "" + BoardAPI.controls.RGB_LED.group + "," + BoardAPI.controls.RGB_LED.led + "," +
									$("#modalR").val() + "," + $("#modalG").val() + "," + $("#modalB").val();
					BoardAPI.post(BoardAPI.controls.RGB_LED.command, intValues);
					BoardAPI.modal.hide();
				}
			},

			/**
			 * For a Group of RGB LEDs
			 */
			RGB_LEDs: {
				group: undefined,
				modalTitle: "Set the RGB LED",
				modalBody: "<p>R: <input id='modalR' type='number' min='0' max='255' /> G: <input id='modalG' type='number' min='0' max='255' /> B: <input id='modalB' type='number' min='0' max='255' /></p>",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.RGB_LEDs.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.RGB_LEDs.modalTitle, BoardAPI.controls.RGB_LEDs.modalBody, BoardAPI.controls.RGB_LEDs.modalSave);
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					BoardAPI.modal.hide();
				}
			},

			/**
			 * For a Group Pulse
			 */
			pulse: {
				group: undefined,
				modalTitle: "Set the RGB LED",
				modalBody: "<p>R: <input id='modalR' type='number' min='0' max='255' /> G: <input id='modalG' type='number' min='0' max='255' /> B: <input id='modalB' type='number' min='0' max='255' /></p>",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.pulse.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.pulse.modalTitle, BoardAPI.controls.pulse.modalBody, BoardAPI.controls.pulse.modalSave);
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					BoardAPI.modal.hide();
				}
			},

			/**
			 * For a Group Tweet
			 */
			tweet: {
				group: undefined,
				modalTitle: "Set RGB LEDs to reflect Tweets",
				modalBody: "<p>R: <input id='modalR' type='number' min='0' max='255' /> G: <input id='modalG' type='number' min='0' max='255' /> B: <input id='modalB' type='number' min='0' max='255' /></p>",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.tweet.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.tweet.modalTitle, BoardAPI.controls.tweet.modalBody, BoardAPI.controls.tweet.modalSave);
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					BoardAPI.modal.hide();
				}
			}
		},

		/**
		 * Get the board and update controls
		 */
		get: function () {
			$.ajax({
				url: BoardAPI.BOARD_ROUTE + name,
				type: "GET",
				success: function (data) {
					var name;

					// Iterate over board output types
					Object.keys(BoardAPI.TYPES).forEach(function (type) {
						// Update client for server entries
						name = BoardAPI.TYPES[type].name;
						if (data[name] !== undefined) {
							BoardAPI.update(type, data[name]);
						}
					});

					// Display updates made
					BoardAPI.display();

					setTimeout(BoardAPI.get, BoardAPI.RETRIEVE_TIMEOUT);
				},
				error: function () { console.error("error getting board status"); }
			});
		},

		/**
		 * Post to update a part of the board 
		 */
		post: function (command, intValues, strValues) {
			$.ajax({
				url: BoardAPI.BOARD_ROUTE + name,
				data: {
					"command": command,
					"int-values": intValues,
					"str-values": strValues
				},
				type: "POST",
				success: function (data) {
					// Wait till next display to get results
				},
				error: function () { console.error("error getting board status"); }
			});
		}
	};
})();







/*
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
				updateStrBase = "led-" + setId + "-",
				pulseStr = "pulse-" + setId;

			// Random first LED
			var newRgb = randUChar() + "," + randUChar() + "," + randUChar();
			$.ajax({
				url: boardUrl,
				type: "POST",
				data: {"update-key": pulseStr, "update-value": newRgb},
			});
			$("#" + updateStrBase + "0").css("background-color", "rgb(" + newRgb + ")");

			for (var i = rgb_leds.length - 1; i > 0; i--) {
				var rgb = rgb_leds[i - 1]["r"] + "," + rgb_leds[i - 1]["g"] + "," + rgb_leds[i - 1]["b"];
				$("#" + updateStrBase + i).css("background-color", "rgb(" + rgb + ")");
			}

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
*/