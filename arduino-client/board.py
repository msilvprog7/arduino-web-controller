import re, uuid

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
			for i, rgb_leds in enumerate(rgb_led_groups):
				# Add new RGB LED Group
				self.rgb_led_groups.append(RGB_LED_Group(rgb_leds, i))

	def set_rgb_led_group(self, set_id, update_value):
		""" Set all values in an RGB LED group """
		for group in self.rgb_led_groups:
			if group.id == set_id:
				group.set_all(update_value)
				return

	def set_single_rgb(self, set_id, led_id, update_value):
		""" Set a single RGB in an RGB LED group """
		for group in self.rgb_led_groups:
			if group.id == set_id:
				group.set(led_id, update_value)
				return

	def update_controls(self, update_key, update_value):
		""" Update controls based on a specific key and value """
		# RGB Group update
		rgb_led_set_updates = re.findall("led-set-\d+", update_key)
		for set_update in rgb_led_set_updates:
			set_id = int(set_update.rsplit("-")[2])
			self.set_rgb_led_group(set_id, update_value)

		# RGB update
		rgb_led_update = re.findall("led-\d+-\d+", update_key)
		for rgb_update in rgb_led_update:
			split_values = rgb_update.rsplit("-")
			set_id = int(split_values[1])
			led_id = int(split_values[2])
			self.set_single_rgb(set_id, led_id, update_value)

class RGB_LED_Group:
	""" A cluster of RGB LEDs """

	def __init__(self, num, id):
		"""Constructor """
		self.reset(num)
		self.id = id

	def reset(self, num):
		""" Reset the LEDs """
		self.rgb_leds = []
		self.single_rgb_led = True
		if num <= 0:
			return

		for i in range(num):
			self.add(i)

		self.single_rgb_led = len(self.rgb_leds) <= 1

	def add(self, id):
		""" Add an LED """
		self.rgb_leds.append(RGB_LED(id))

	def get(self):
		""" Get the values of the group """
		return {"rgb-leds": [x.get() for x in self.rgb_leds], "group_id": self.id}

	def set_all(self, update_value):
		""" Set all the values """
		for led in self.rgb_leds:
			print "Updating Set", self.id, "RGB", led.id, "to", update_value
			led.set_value(update_value)

	def set(self, led_id, update_value):
		""" Set single value """
		for led in self.rgb_leds:
			if led.id == led_id:
				print "Updating Set", self.id, "RGB", led_id, "to", update_value
				led.set_value(update_value)
				return

class RGB_LED:
	""" A single RGB LED """

	def __init__(self, id):
		""" Constructor """
		self.set(0, 0, 0)
		self.id = id

	def set(self, r, g, b, mode=None):
		""" Set value """
		self.r = r
		self.g = g
		self.b = b
		self.mode = None

	def get(self):
		""" Return dictionary of values """
		return {"r": self.r, "g": self.g, "b": self.b, "mode": self.mode, "id": self.id}

	def set_value(self, value_str):
		values = re.findall("\d+", value_str)

		if len(values) < 3 or any([int(x) < 0 or int(x) > 255 for x in values]):
			print "At least one value was invalid, rejecting transaction"
			return

		self.set(int(values[0]), int(values[1]), int(values[2]))

	def set_dict(self, d):
		if d.has_key["r"] and type(d["r"]) is int:
			self.r = int(d["r"])

		if d.has_key["g"] and type(d["g"]) is int:
			self.g = int(d["g"])

		if d.has_key["b"] and type(d["b"]) is int:
			self.b = int(d["b"])

		if d.has_key["r"] and type(d["r"]) is int:
			self.mode = str(d["mode"])

