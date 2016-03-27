import uuid

class Board:
	""" A board for manipulating inputs on """

	def __init__(self, name):
		""" Constructor """
		self.name = name
		self.token = str(uuid.uuid4())
		self.reset_controls()

	def get_dict(self):
		""" Return object representation """
		return {"board-name": self.name, "rgb-led-groups": [x.get() for x in self.rgb_led_groups]}

	def get_owner_dict(self):
		""" Get owner's dictionary with token """
		results = self.get_dict()
		results['board-token'] = self.token
		return results

	def reset_controls(self):
		""" Reset board controls """
		print "Resetting controls"
		self.rgb_led_groups = []

	def set_controls(self, controls):
		""" Set controls for the board """
		self.reset_controls()

		if type(controls) is not dict:
			print "Controls in the wrong format"
			return

		if controls.has_key("rgb-led-groups") and type(controls["rgb-led-groups"]) is str:
			# Set rgb led groups
			rgb_led_groups = map(lambda x: int(x), filter(lambda x: x != "", controls["rgb-led-groups"].split(",")))
			for rgb_leds in rgb_led_groups:
				# Add new RGB LED Group
				print "New RGB LED Group of", rgb_leds, "LEDs"
				self.rgb_led_groups.append(RGB_LED_Group(rgb_leds))

class RGB_LED_Group:
	""" A cluster of RGB LEDs """

	def __init__(self, num):
		"""Constructor """
		self.reset(num)

	def reset(self, num):
		""" Reset the LEDs """
		self.rgb_leds = []
		for i in range(num):
			self.add()
		print "Created", len(self.rgb_leds), "RGB LEDs"

	def add(self):
		""" Add an LED """
		self.rgb_leds.append(RGB_LED())

	def get(self):
		""" Get the values of the group """
		return {"rgb-leds": [x.get() for x in self.rgb_leds]}

class RGB_LED:
	""" A single RGB LED """

	def __init__(self):
		""" Constructor """
		self.set(0, 0, 0)

	def set(self, r, g, b, mode=None):
		""" Set value """
		self.r = r
		self.g = g
		self.b = b
		self.mode = None

	def get(self):
		""" Return dictionary of values """
		return {"r": self.r, "g": self.g, "b": self.b, "mode": self.mode}

