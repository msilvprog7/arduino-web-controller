import requests, serial, sys, time, yaml
from board import RGB_LED, RGB_LED_Group

url = "http://127.0.0.1:5000"
ping_server_ms = 1000 / 10

# Functions---------------------------------Start

def sendToArduino(ard, msg):
	"Sends a message to the arduino over the com port"
	ard.write(msg)
	ard.write('\n')
	return;

def readFromArduino(ard):
	"Reads an int from the com port"
	tmp = ard.read(ard.in_waiting) # Reads all of the bytes waiting in the buffer
	#print tmp
	return tmp;

def grabCommaDel(ard):
	"Gets comma delimited information from the serial port"
	while(ard.in_waiting == 0):
		# do nothing
		pass
	tmpResponse = ''
	tmpByteRead = ''
	tmpByteRead = ard.read(1) # Read in 1 byte
	while(tmpByteRead != ','):
		tmpResponse += tmpByteRead # Concatenate the new byte
		#print "preparing to read a second byte"
		tmpByteRead = ard.read(1) # Read in 1 byte
		#print "Read successful, byte is "
		#print tmpByteRead
	return tmpResponse

def sendLEDsToArduino(ard, ledGroupList):
	"Sends the ledGroupList to Arduino; that is, the RGB values for each LED"
	# Initial formatting
	listForSending = []
	listForSending.append('WS2812S')
	# Set output of LED groups
	for led_group in ledGroupList: # Set all of the strips
		for rgb_led in led_group.rgb_leds:
			listForSending.append(str(rgb_led.r).zfill(3))
			listForSending.append(str(rgb_led.g).zfill(3))
			listForSending.append(str(rgb_led.b).zfill(3))
	# Send to the Arduino
	sendToArduino(ard, ''.join(listForSending))



def register_with_server(led_groups, token=None):
	""" Register the board with the server """
	opts = {}

	# Set token
	if token is not None:
		opts["board-token"] = token

	# Set LED group info as string of comma delineated numbers for LEDs in group
	opts["rgb-led-groups"] = ",".join(map(lambda x: str(x), [len(group.rgb_leds) for group in led_groups]))

	return requests.post(url + "/board", data=opts).json()

def update_board_from_server(board_name, ledGroupList):
	""" Update the board with the outputs specified by the server """
	response = yaml.safe_load(yaml.safe_dump(requests.get(url + "/board/" + board_name).json()))

	if response.has_key("rgb-led-groups") and type(response["rgb-led-groups"]) is list:
		for group_id, group in enumerate(response["rgb-led-groups"]):
			if group.has_key("rgb-leds") and type(group["rgb-leds"]) is list:
				for led_id, led in enumerate(group["rgb-leds"]):
					ledGroupList[group_id].rgb_leds[led_id].set_dict(led)
	

	

# End Functions--------------------------------------------------------------------End



def main():
	""" Main function for code """
	# Get command line arguments
	if len(sys.argv) < 2:
		print "Incorrect commandline request: should be in format 'python arduino_client.py 'COM8' [token]'"
		exit(1)
	# Set com port
	port = sys.argv[1]
	# Set token (if available)
	token = sys.argv[2] if len(sys.argv) > 2 else None

	# Create ardiuno serial connection
	ard = serial.Serial(port, 38400, timeout=5)
	time.sleep(3) # Wait for arduino to boot
	ledGroupList = [] # The list of LED groups; contains their RGB values
	numStrips = 0 # The number of strips connected to the arduino

	while not ard.isOpen():
		print "Waiting on aruino connection..."
		time.sleep(3)

	if(ard.isOpen()):
		print "Arduino connection."

	# Set up the LED arrays----------------------------------------------------------Start
	ard.flush() # Clear the buffer if there's anything waiting to be read
	sendToArduino(ard, "WS2812?") # Something regarding the connected WS2812 LEDs
	time.sleep(1)
	# It will send number (how many strips there are), and the number of LEDs in each strip
	tmpResponse = 0
	tmpCounter = 0
	numStrips = int(float(grabCommaDel(ard))) # the number of strips should be the first thing sent
	print "The number of strips is", numStrips
	while(tmpCounter < numStrips): # Loop through all of the connected strips
		tmpCounter = tmpCounter + 1
		tmpNumLEDResponse = int(float(grabCommaDel(ard)))
		print tmpNumLEDResponse
		ledGroupList.append(RGB_LED_Group(tmpNumLEDResponse, tmpCounter))
	# ledGroupList should now contain all of the LED groups------------------------End	

	# Register with the server
	board_info = register_with_server(ledGroupList, token=token)

	if board_info.has_key("error"):
		print "Server error:", board_info["error"]
		exit(2)
	elif not board_info.has_key("board-name") or not board_info.has_key("board-token"):
		print "Server error: did not retrieve board-name or board-token"
		exit(3)

	print "\nSuccessfully registered your board with the following information:"
	print "board-name:\t\t%s\nboard-token:\t\t%s\n" % (board_info["board-name"], board_info["board-token"])

	# Continuously retrieve board updates
	print "Getting server updates every", str(ping_server_ms), "ms (Press Ctrl+C to quit)"
	print "Next run:\t\tpython arduino_client.py", port, board_info["board-token"]

	ping_server_s = ping_server_ms / 1000
	board_name = board_info["board-name"]
	while True:
		update_board_from_server(board_name, ledGroupList)
		sendLEDsToArduino(ard, ledGroupList)
		time.sleep(ping_server_s)

# Run main
if __name__ == "__main__":
	main()