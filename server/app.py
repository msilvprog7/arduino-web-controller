from flask import Flask, json, jsonify, render_template, request
from board import names
from board.board import Board

# Define app
app = Flask(__name__)

# Boards being used
boards = []

# Name generator
name_generator = names.NameGenerator()


def has_board(board_name):
	return get_board(board_name) is not None

def get_board(board_name):
	for current_board in boards:
		if current_board.name == board_name:
			return current_board
	return None

def get_board_with_token(token):
	for current_board in boards:
		if current_board.token == token:
			return current_board
	return None

def add_board(board_to_add):
	for i, current_board in enumerate(boards):
		# Found in list, replace
		if current_board.name == board_to_add.name:
			print "Replacing board in list"
			boards[i] = board_to_add
			return

	# Not in list, add
	print "Adding new board to list"
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
	print guid, controls

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
	print results
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
		# TODO: Update board info
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