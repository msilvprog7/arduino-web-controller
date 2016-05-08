from flask import Flask, json, jsonify, render_template, request
from board import names
from board.board import Board, TweetAnalyzer

# Define app
app = Flask(__name__)

# Boards being used
boards = []

# Name generator
name_generator = names.NameGenerator()

# Start thread for Tweet Analyzer
tweet_analyzer = TweetAnalyzer()
tweet_analyzer.start()


def has_board(board_name):
	""" Whether or not the board list has the board with specified name """
	return get_board(board_name) is not None

def get_board(board_name):
	""" Get the board in the board list with the specified name or None """
	for current_board in boards:
		if current_board.name == board_name:
			return current_board
	return None

def get_board_with_token(token):
	""" Get the board in the board list with the specified board token or None """
	for current_board in boards:
		if current_board.token == token:
			return current_board
	return None

def add_board(board_to_add):
	""" Add the board to the board list either to the end or replacing the
		old one with the same name """
	for i, current_board in enumerate(boards):
		# Found in list, replace
		if current_board.name == board_to_add.name:
			boards[i] = board_to_add
			return

	# Not in list, add
	boards.append(board_to_add)





@app.route("/", methods=['GET'])
def index():
	""" Render the main page """
	return render_template("index.html")

@app.route("/board", methods=['POST'])
def board():
	""" Obtain a board name to work with (optionally present GUID to reset) """
	guid = str(request.form['board-token']) if 'board-token' in request.form else None
	controls = {"rgb-led-groups": str(request.form['rgb-led-groups']) if 'rgb-led-groups' in request.form else ""}

	current_board = get_board_with_token(guid)

	# Incorrect credentials
	if current_board is None and guid is not None:
		results = {"error": "board token invalid"}
		return jsonify(**results)

	# Generate new board
	if current_board is None:
		# Obtain name
		current_board_name = None
		while current_board_name is None or has_board(current_board_name):
			current_board_name = name_generator.get_name()
		# Create
		current_board = Board(current_board_name)

	# Assign controls
	current_board.set_controls(controls)

	# Push to boards
	add_board(current_board)

	# Format results
	results = current_board.get_owner_dict()
	return jsonify(**results)

@app.route("/board/<name>", methods=['GET', 'POST'])
def get_board_status(name):
	""" Get board info """
	results = {"board-name": name, "error": "does not exit"}
	current_board = get_board(name)

	if request.method == 'GET' and current_board is not None:
		# Get board info
		results = current_board.get_dict()
	elif request.method == 'POST' and current_board is not None:
		# Update board info
		command = str(request.form['command']) if 'command' in request.form else ""
		int_values = str(request.form['int-values']) if 'int-values' in request.form else ""
		str_values = str(request.form['str-values']) if 'str-values' in request.form else ""
		print command, int_values, str_values
		# Update control value
		current_board.update_controls(command, int_values, str_values)
		# Get update values as results
		results = current_board.get_dict()

	return jsonify(**results)

@app.route("/control-board/<name>", methods=['GET'])
def control_board(name):
	""" Control the board """
	# Get board control info
	current_board = get_board(name)
	return render_template("board.html", board=current_board)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)