import serial
import time
from board import RGB_LED, RGB_LED_Group

port = 'COM8'
numStrips = 0 # The number of strips connected to the arduino

listForSending = []


# Functions---------------------------------Start

def sendToArduino(msg):
	"Sends a message to the arduino over the com port"
	ard.write(msg)
	ard.write('\n')
	return;

def readFromArduino():
	"Reads an int from the com port"
	tmp = ard.read(ard.in_waiting) # Reads all of the bytes waiting in the buffer
	#print tmp
	return tmp;

def grabCommaDel():
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

def sendLEDsToArduino():
	"Sends the ledGroupList to Arduino; that is, the RGB values for each LED"
	listForSending = []
	listForSending.append('WS2812S')
	tmpSendCounter = 0
	while(tmpSendCounter < numStrips): # Set all of the strips
		i = 0
		while(i < len(ledGroupList[tmpSendCounter].rgb_leds)):
			listForSending.append(str(ledGroupList[tmpSendCounter].rgb_leds[i].r).zfill(3))
			listForSending.append(str(ledGroupList[tmpSendCounter].rgb_leds[i].g).zfill(3))
			listForSending.append(str(ledGroupList[tmpSendCounter].rgb_leds[i].b).zfill(3))
			i = i + 1
		tmpSendCounter = tmpSendCounter + 1
	sendToArduino(''.join(listForSending))
	

# End Functions--------------------------------------------------------------------End



ard = serial.Serial(port,38400,timeout=5)
time.sleep(3) # Wait for arduino to boot
ledGroupList = [] # The list of LED groups; contains their RGB values

while not ard.isOpen():
	print "The Chamber of Secrets is Closed!"
	time.sleep(3)

if(ard.isOpen()):
	print "The Chamber of Secrets is Open!"

#response = "Didn't Work"
#sendToArduino("P") # Set a pin
#time.sleep(1) # It doesn't work without these pauses
#sendToArduino("13") # Select pin 13
#time.sleep(1)
#sendToArduino("O") # Set the pin as an output
#time.sleep(1)
#sendToArduino("H") # Set the pin high
#time.sleep(1)
#response = readFromArduino()
#print response # For debugging

# Set up the LED arrays----------------------------------------------------------Start
ard.flush() # Clear the buffer if there's anything waiting to be read
sendToArduino("WS2812?") # Something regarding the connected WS2812 LEDs
time.sleep(1)
# It will send number (how many strips there are), and the number of LEDs in each strip
tmpResponse = 0
tmpCounter = 0
numStrips = int(float(grabCommaDel())) # the number of strips should be the first thing sent
#print "The number of strips is"
#print numStrips
while(tmpCounter < numStrips): # Loop through all of the connected strips
	tmpCounter = tmpCounter + 1
	tmpNumLEDResponse = int(float(grabCommaDel()))
	ledGroupList.append(RGB_LED_Group(tmpNumLEDResponse))
# ledGroupList should now contain all of the LED groups------------------------End	

# FOR TESTING, FILL THE LIST WITH GEARBAGE
garbCounter = 0
while(garbCounter < numStrips): # Set all of the strips
	i = 0
	while(i < len(ledGroupList[garbCounter].rgb_leds)):
		ledGroupList[garbCounter].rgb_leds[i].r = (50*i)%255
		ledGroupList[garbCounter].rgb_leds[i].g = (95*i)%255
		ledGroupList[garbCounter].rgb_leds[i].b = (111*i)%255
		i = i + 1
	garbCounter = garbCounter + 1
# GEARBAGE FULFILLED

sendLEDsToArduino() # Send the ledGroupList to the Arduino



print "script done."
exit()