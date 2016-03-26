from flask import Flask, jsonify, render_template
from board import names

# Define app
app = Flask(__name__)

# Boards being used
boards = []

# Name generator
name_generator = names.NameGenerator()


@app.route("/", methods=['GET'])
def index():
	""" Render the main page """
	return render_template("index.html")

@app.route("/board", methods=['GET'])
def board():
	""" Obtain a board name to work with """
	current_board = None
	while current_board is None or current_board in boards:
		current_board = name_generator.get_name()

	# Push to boards
	boards.append(current_board)

	# Format results
	results = {"board-name": current_board}

	return jsonify(**results)

@app.route("/board/<name>", methods=['GET', 'POST'])
def get_board(name):
	""" Get board info """
	results = {"board-name": name}

	# TODO: Get and Update board info

	return jsonify(**results)

@app.route("/control-board/<name>", methods=['GET'])
def control_board(name):
	""" Control the board """
	# Get board control info
	if name not in boards:
		name = None

	return render_template("board.html", board_name=name)

if __name__ == "__main__":
	app.run(host='0.0.0.0')