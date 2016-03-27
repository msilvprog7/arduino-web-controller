# arduino-web-controller
A website-based controller for custom arduino outputs.

## Running the server locally
1. `cd server`
2. `sudo pip install -r requirements.txt`
3. `python app.py`
4. Open the website in a browser at `http://localhost:5000`

## Running the arduino client with arduino
1. Install [Adafruit NeoPixel Library](https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-installation)
2. Load script onto arduino following client protocol for defining outputs (see `test-arduino-scripts/TestArduinoScript/TestArduinoScript.ino`)
3. Plug in arduino
4. `cd arduino-client`
5. `sudo pip install -r requirements.txt`
6. `python arduino_client.py com_port [token]` [e.g. `python arduino COM8`, Note: token is used to re-use the same name without creating a new board and having to navigate to the new name on the website]
7. Go to `http://localhost:5000/` and enter the assigned board-name to start controlling the outputs!

## Running the test client for checking server requests
1. `cd test-server-client`
2. `sudo pip install -r requirements.txt`
3. `python client.py`