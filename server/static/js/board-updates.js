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
		RETRIEVE_TIMEOUT: 100,

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
			operations = {};
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
				document.getElementById("modalSave").onclick = function (e) { saveFcn(); e.stopPropagation(); };
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
					BoardAPI.controls.RGB_LED.setupModal();
					BoardAPI.modal.show();
				},

				/**
				 * Set button displayed on Modal
				 */
				setupModal: function () {
					var type = BoardAPI.TYPES.RGB_LED_GROUPS,
						values = board['RGB_LED_GROUPS'][BoardAPI.controls.RGB_LED.group][type.components][BoardAPI.controls.RGB_LED.led];

					// Initialize values
					$("#modalR").val(values.r);
					$("#modalG").val(values.g);
					$("#modalB").val(values.b);
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
				modalTitle: "Set the RGB LED Group",
				modalBody: "<p>R: <input id='modalR' type='number' min='0' max='255' /> G: <input id='modalG' type='number' min='0' max='255' /> B: <input id='modalB' type='number' min='0' max='255' /></p>",
				command: "rgb-leds",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.RGB_LEDs.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.RGB_LEDs.modalTitle, BoardAPI.controls.RGB_LEDs.modalBody, BoardAPI.controls.RGB_LEDs.modalSave);
					BoardAPI.modal.show();
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					var intValues = "" + BoardAPI.controls.RGB_LEDs.group + "," +
									$("#modalR").val() + "," + $("#modalG").val() + "," + $("#modalB").val();
					BoardAPI.post(BoardAPI.controls.RGB_LEDs.command, intValues);
					BoardAPI.modal.hide();
				}
			},

			/**
			 * Randomize Group of RGB LEDs
			 */
			rand: {
				group: undefined,
				modalTitle: "Set Random pattern on RGB LEDs",
				modalBody: "<p>Option: <select id='randSelect'></select></p>",
				command: "rand",
				options: ["completely", "flip-flop"],

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.rand.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.rand.modalTitle, BoardAPI.controls.rand.modalBody, BoardAPI.controls.rand.modalSave);
					BoardAPI.controls.rand.setupModal();
					BoardAPI.modal.show();
				},

				/**
				 * Set button displayed on Modal
				 */
				setupModal: function () {
					var groupId = BoardAPI.controls.rand.group;
					
					// Initialize select
					BoardAPI.controls.rand.options.forEach(function (option, index) {
						var additional = "";
						if (index === 0) {
							additional = "selected='selected'";
						}

						$("#randSelect").append("<option value='" + option + "'" + additional + ">" + option  + "</option>");
					});
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					var groupId = BoardAPI.controls.rand.group,
						option = $("#randSelect").val(),
						intValues = "" + groupId,
						strValues = option;

					// Perform random option
					BoardAPI.post(BoardAPI.controls.rand.command, intValues, strValues);

					BoardAPI.modal.hide();
				}
			},

			/**
			 * For a Group Pulse
			 */
			pulse: {
				group: undefined,
				pulsing: {},
				rate: {},
				modalTitle: "Set a Pulse across the RGB LEDs",
				modalBody: "<p>Milliseconds: <input id='pulseRate' type='number' min='10' max='5000' /><br /><button id='pulseFlip' type='button' class='btn' onclick='BoardAPI.controls.pulse.flip()'></button></p>",
				command: "pulse",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.pulse.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.pulse.modalTitle, BoardAPI.controls.pulse.modalBody, BoardAPI.controls.pulse.modalSave);
					BoardAPI.controls.pulse.setupModal();
					BoardAPI.modal.show();
				},

				/**
				 * Set button displayed on Modal
				 */
				setupModal: function () {
					var groupId = BoardAPI.controls.pulse.group;
					
					// Initialize if needed
					if (BoardAPI.controls.pulse.pulsing[groupId] === undefined) {
						BoardAPI.controls.pulse.pulsing[groupId] = false;
					}

					if (BoardAPI.controls.pulse.rate[groupId] === undefined) {
						BoardAPI.controls.pulse.rate[groupId] = 1000;
					}

					// Set values on modal
					$("#pulseRate").val(BoardAPI.controls.pulse.rate[groupId]);
					$("#pulseFlip").html((BoardAPI.controls.pulse.pulsing[groupId]) ? "Flip Off" : "Flip On");
					$("#pulseFlip").addClass((BoardAPI.controls.pulse.pulsing[groupId]) ? "btn-danger" : "btn-success");
				},

				/**
				 * Flip button
				 */
				flip: function () {
					if ($("#pulseFlip").html() === "Flip Off") {
						$("#pulseFlip").html("Flip On");
						$("#pulseFlip").removeClass("btn-danger");
						$("#pulseFlip").addClass("btn-success");
					} else {
						$("#pulseFlip").html("Flip Off");
						$("#pulseFlip").removeClass("btn-success");
						$("#pulseFlip").addClass("btn-danger");
					}
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					var groupId = BoardAPI.controls.pulse.group,
						updatedPulsing = $("#pulseFlip").html() === "Flip Off",
						rate = $("#pulseRate").val();

					// Set rate
					BoardAPI.controls.pulse.rate[groupId] = rate;

					// Start pulsing
					if (!BoardAPI.controls.pulse.pulsing[groupId] && updatedPulsing) {
						setTimeout(function () {
							BoardAPI.controls.pulse.pulse(groupId);
						}, rate);
					}

					// Update pulsing
					BoardAPI.controls.pulse.pulsing[groupId] = updatedPulsing;

					BoardAPI.modal.hide();
				},

				/**
				 * Pulse 
				 */
				 pulse: function (groupId) {
				 	// Pulse
				 	var intValues = "" + groupId + "," + BoardAPI.UTILS.randRGB();
				 	BoardAPI.post(BoardAPI.controls.pulse.command, intValues);

				 	// Continue
				 	setTimeout(function () {
				 		if (BoardAPI.controls.pulse.pulsing[groupId]) {
				 			BoardAPI.controls.pulse.pulse(groupId);
				 		}
				 	}, BoardAPI.controls.pulse.rate[groupId]);
				 }
			},

			/**
			 * For a Group Tweet
			 */
			tweet: {
				group: undefined,
				tweets: {},
				modalTitle: "Set RGB LEDs to reflect Tweets Every 5 Minutes",
				modalBody: "<p>Category 1: <input id='tweetCategory1' type='text' /><br />Category 2: <input id='tweetCategory2' type='text' /><br />Category 3: <input id='tweetCategory3' type='text' /><br /><button id='tweetFlip' type='button' class='btn' onclick='BoardAPI.controls.tweet.flip()'></button></p>",
				tweetCommand: "tweet",
				untweetCommand: "untweet",

				/**
				 * Show the modal
				 */
				show: function (groupId) {
					BoardAPI.controls.tweet.group = groupId;
					BoardAPI.modal.set(BoardAPI.controls.tweet.modalTitle, BoardAPI.controls.tweet.modalBody, BoardAPI.controls.tweet.modalSave);
					BoardAPI.controls.tweet.setupModal();
					BoardAPI.modal.show();
				},

				/**
				 * Setup modal 
				 */
				setupModal: function () {
					var groupId = BoardAPI.controls.tweet.group,
						rgb_leds = board['RGB_LED_GROUPS'][groupId];

					// Try to retrieve running tweets from last board update
					if (rgb_leds !== undefined && rgb_leds["tweets"] !== undefined && rgb_leds["tweets"] !== null) {
						BoardAPI.controls.tweet.tweets[groupId] = {
							running: true,
							categories: rgb_leds["tweets"].map(function (category) {
								return category["name"];
							})
						};
					} else {
						// Initialize to Daniel's favorites
						BoardAPI.controls.tweet.tweets[groupId] = {
							running: false,
							categories: ["Filthy Frank", "Madoka Magica", "Hearthstone"]
						};
					}

					// Set values in modal
					BoardAPI.controls.tweet.tweets[groupId].categories.forEach(function (category, index) {
						$("#tweetCategory" + (index + 1)).val(category);
					});
					$("#tweetFlip").html((BoardAPI.controls.tweet.tweets[groupId].running) ? "Flip Off" : "Flip On");
					$("#tweetFlip").addClass((BoardAPI.controls.tweet.tweets[groupId].running) ? "btn-danger" : "btn-success");
				},

				/**
				 * Flip button
				 */
				flip: function () {
					if ($("#tweetFlip").html() === "Flip Off") {
						$("#tweetFlip").html("Flip On");
						$("#tweetFlip").removeClass("btn-danger");
						$("#tweetFlip").addClass("btn-success");
					} else {
						$("#tweetFlip").html("Flip Off");
						$("#tweetFlip").removeClass("btn-success");
						$("#tweetFlip").addClass("btn-danger");
					}
				},

				/**
				 * Save the modal
				 */
				modalSave: function () {
					var groupId = BoardAPI.controls.tweet.group,
						updatedRunning = ($("#tweetFlip").html() === "Flip Off");

					// Set categories
					BoardAPI.controls.tweet.tweets[groupId].categories = [1, 2, 3].map(function (num) {
						return $("#tweetCategory" + num).val();
					});

					// Turn on tweets or turn off tweets
					if (!BoardAPI.controls.tweet.tweets[groupId].running && updatedRunning) {
						BoardAPI.controls.tweet.tweet(groupId);
					} else if (BoardAPI.controls.tweet.tweets[groupId].running && !updatedRunning) {
						BoardAPI.controls.tweet.untweet(groupId);
					}

					// Set tweet running
					BoardAPI.controls.tweet.tweets[groupId].running = updatedRunning;

					BoardAPI.modal.hide();
				},

				/**
				 * Signal the server to start analyzing tweets and changing the RGB group
				 */
				tweet: function (groupId) {
					var intValues = "" + groupId,
						strValues = BoardAPI.controls.tweet.tweets[groupId].categories[0] + "," + BoardAPI.controls.tweet.tweets[groupId].categories[1] + "," + BoardAPI.controls.tweet.tweets[groupId].categories[2];

					BoardAPI.post(BoardAPI.controls.tweet.tweetCommand, intValues, strValues);
				},

				/**
				 * Signal the server to stop analyzing tweets
				 */
				untweet: function (groupId) {
					var intValues = "" + groupId;

					BoardAPI.post(BoardAPI.controls.tweet.untweetCommand, intValues);
				},
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
		},

		/**
		 * Utilities
		 */
		UTILS: {
			/**
			 * Get a random color value 0 - 255
			 */
			randColorValue: function () {
				return Math.floor(Math.random() * 256);
			},

			/**
			 * Get a random RGB string
			 */
			randRGB: function () {
				return "" + BoardAPI.UTILS.randColorValue() + "," + BoardAPI.UTILS.randColorValue() + "," + BoardAPI.UTILS.randColorValue();
			}
		}
	};
})();