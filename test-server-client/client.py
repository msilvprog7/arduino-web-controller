import json, requests, yaml

url = "http://127.0.0.1:5000"

def create_new_board(opts=None):
	return requests.post(url + "/board", data=opts)

def create_new_board_with_token(opts={}):
	token = str(raw_input("Enter token: "))
	opts["board-token"] = token
	return create_new_board(opts)

def create_new_board_with_rgb_leds():
	opts = { "rgb-led-groups": [] }
	endLoop = False

	# Add RGB LED Groups
	while not endLoop:
		val = int(raw_input("Enter number in RGB LED Group (non-positive to stop): "))
		if val <= 0:
			endLoop = True
		else:
			opts["rgb-led-groups"].append(val)
	# Flatten list
	opts["rgb-led-groups"] = ",".join(map(lambda x: str(x), opts["rgb-led-groups"]))

	# return create_new_board_with_token(opts)
	return create_new_board(opts)

def get_board_status():
	name = str(raw_input("Enter board name: "))
	return requests.get(url + "/board/" + name)

def main():
	""" Main functionality """
	# response = create_new_board()
	# response = create_new_board_with_token()
	# response = create_new_board_with_rgb_leds()
	response = get_board_status()
	print yaml.safe_dump(response.json())

if __name__ == "__main__":
	main()