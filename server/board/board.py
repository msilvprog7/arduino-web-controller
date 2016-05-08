import random, re, threading, time, tweepy, uuid

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

	def set_rgb_led_group(self, set_id, value):
		""" Set all values in an RGB LED group """
		for group in self.rgb_led_groups:
			if group.id == set_id:
				group.set_all(value)
				return

	def set_single_rgb(self, set_id, led_id, value):
		""" Set a single RGB in an RGB LED group """
		for group in self.rgb_led_groups:
			if group.id == set_id:
				group.set(led_id, value)
				return

	def update_controls(self, command, int_values, str_values):
		""" Update controls based on a specific command and int values """
		# Parse values
		int_values = [int(x) for x in re.findall("\d+", int_values)]
		str_values = [x.strip() for x in str_values.split(",")]

		# Commands
		if command == "rgb-led" and len(int_values) == 5:
			# Set a single RGB LED: group id, led id, rgb
			self.set_single_rgb(int_values[0], int_values[1], int_values[2:])
		elif command == "rgb-leds" and len(int_values) == 4:
			# Set a group of RGB LEDs: group id, rgb
			self.set_rgb_led_group(int_values[0], int_values[1:])
		elif command == "pulse" and len(int_values) == 4:
			# Pulse through the RGB LEDs
			self.rgb_led_groups[int_values[0]].pulse(int_values[1:])
		elif command == "tweet" and len(int_values) == 1 and len(str_values) == 3:
			# Start analyzing tweets
			self.rgb_led_groups[int_values[0]].tweet(str_values)
		elif command == "untweet" and len(int_values) == 1:
			# Stop analyzing tweets
			self.rgb_led_groups[int_values[0]].untweet()
			pass

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
		self.more_than_ten = False
		if num <= 0:
			return

		for i in range(num):
			self.add(i)

		self.single_rgb_led = len(self.rgb_leds) <= 1
		self.more_than_ten = len(self.rgb_leds) > 10

	def add(self, id):
		""" Add an LED """
		self.rgb_leds.append(RGB_LED(id))

	def get(self):
		""" Get the values of the group """
		return {"rgb-leds": [x.get() for x in self.rgb_leds], "group_id": self.id}

	def set_all(self, value):
		""" Set all the values """
		for led in self.rgb_leds:
			print "Updating Set", self.id, "RGB", led.id, "to", value
			led.set_value(value)

	def set(self, led_id, value):
		""" Set single value """
		for led in self.rgb_leds:
			if led.id == led_id:
				print "Updating Set", self.id, "RGB", led_id, "to", value
				led.set_value(value)
				return

	def pulse(self, rgb):
		""" Shift all and set first """
		for i in reversed(range(len(self.rgb_leds))):
			if i == 0:
				self.rgb_leds[i].set_value(rgb)
			else:
				self.rgb_leds[i].set_dict(self.rgb_leds[i - 1].get())

	def tweet(self, categories):
		""" Start analyzing tweets periodically """
		print "tweet", categories
		self.tweets = {"last-update": TweetAnalyzer.current_ms(), "categories": map(lambda category: {"name": category, "count": 0}, categories)}
		tweet_analyzer = TweetAnalyzer()
		tweet_analyzer.add(self)

	def display_tweets(self):
		""" Update the RGB LEDs based on the tweet counts """
		# Get counts
		rgb = []
		total_count = 0
		for category in self.tweets["categories"]:
			rgb.append(category["count"])
			total_count += category["count"]

		# Divide and multiply by 255 for percentile
		if total_count != 0:
			rgb = [int(255 * v / total_count) for v in rgb]
		
		# Set rgb values
		self.set_all(rgb)

	def reset_tweets(self):
		""" Reset the counts for tweet categories """
		for category in self.tweets["categories"]:
				category["count"] = 0

	def untweet(self):
		""" Stop analyzing tweets """
		print "untweet"
		tweet_analyzer = TweetAnalyzer()
		tweet_analyzer.remove(self)
		self.tweets = {}

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

	def set_value(self, values):
		if len(values) < 3 or any([int(x) < 0 or int(x) > 255 for x in values]):
			print "At least one value was invalid, rejecting transaction"
			return

		self.set(int(values[0]), int(values[1]), int(values[2]))

	def set_dict(self, d):
		if d.has_key("r") and type(d["r"]) is int:
			self.r = int(d["r"])

		if d.has_key("g") and type(d["g"]) is int:
			self.g = int(d["g"])

		if d.has_key("b") and type(d["b"]) is int:
			self.b = int(d["b"])

		if d.has_key("r") and type(d["r"]) is int:
			self.mode = str(d["mode"])

class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class TweetAnalyzer(threading.Thread):
	""" Analyze tweets for different boards with RGB LED groups """
	__metaclass__ = Singleton
	RETRIEVE_TIME_BETWEEN = 0.1 # Tenth of a second between
	RETRIEVE_TIMEOUT = 10 # Every 10 seconds
	ANALYSIS_DURATION = 60000 # Every minute, in ms
	PROPERTIES_FILE = "resources/twitter.properties"

	def __init__(self):
		""" Constructor """
		threading.Thread.__init__(self)
		self.rgb_led_groups = []
		self.rgb_led_groups_lock = threading.Lock()
		self.load_properties()

	def get_key(self, key):
		return self.properties[key] if key in self.properties else ""

	def load_properties(self):
		""" Load properties for Twitter Auth """
		# Load properties 
		self.properties = {}
		with open(TweetAnalyzer.PROPERTIES_FILE, 'r') as propFile:
			for line in propFile:
				# Remove comments, remove whitespace to get key=value, and separate
				key_val = line.split("#", 1)[0].strip().split("=", 1)
				if len(key_val) != 2:
					continue
				# Store key value
				self.properties[key_val[0]] = key_val[1]

		self.__auth = tweepy.OAuthHandler(self.get_key("CONSUMER_KEY"), self.get_key("CONSUMER_SECRET"))
		self.__auth.set_access_token(self.get_key("ACCESS_TOKEN"), self.get_key("ACCESS_TOKEN_SECRET"))
		self.__api = tweepy.API(self.__auth)

	@staticmethod
	def current_ms():
		""" Get the current time in Milliseconds """
		return int(round(time.time() * 1000))

	def add(self, rgb_led_group):
		""" Add an rgb_led_group to the analysis """
		self.rgb_led_groups_lock.acquire()
		print "Adding RGB LED Group", rgb_led_group.id
		self.rgb_led_groups.append(rgb_led_group)
		self.rgb_led_groups_lock.release()

	def remove(self, rgb_led_group):
		""" Remove an rgb_led_group from the analysis """
		self.rgb_led_groups_lock.acquire()
		print "Removing RGB LED Group", rgb_led_group.id
		self.rgb_led_groups.remove(rgb_led_group)
		self.rgb_led_groups_lock.release()

	def fetch_tweets(self, rgb_led_group):
		""" Fetch tweets for the RGB LED Group """
		print "TweetAnalyzer", rgb_led_group.id, rgb_led_group.tweets["categories"]

		curr_time = TweetAnalyzer.current_ms()

		if curr_time >= (rgb_led_group.tweets["last-update"] + TweetAnalyzer.ANALYSIS_DURATION):
			# Display data
			rgb_led_group.display_tweets()
			# Reset counts
			rgb_led_group.reset_tweets()
			# Update time
			rgb_led_group.tweets["last-update"] = curr_time
			print "TweetAnalyzer", rgb_led_group.id, "RESET"
		
		# Get a tweet that filters on categories
		# Update counts
		rgb_led_group.tweets["categories"][0]["count"] += random.randint(0, 100)
		rgb_led_group.tweets["categories"][1]["count"] += random.randint(0, 100)
		rgb_led_group.tweets["categories"][2]["count"] += random.randint(0, 100)

	def run(self):
		""" Analyze tweets for RGB LED Groups """
		while True:
			# Collect tweets
			self.rgb_led_groups_lock.acquire()
			print "TweetAnalyzer", len(self.rgb_led_groups), "groups"
			for rgb_led_group in self.rgb_led_groups:
				self.fetch_tweets(rgb_led_group)
				time.sleep(TweetAnalyzer.RETRIEVE_TIME_BETWEEN)
			self.rgb_led_groups_lock.release()

			# Wait for timeout
			time.sleep(TweetAnalyzer.RETRIEVE_TIMEOUT)