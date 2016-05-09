from __future__ import division
import math, random, re, thread, threading, time, tweepy, uuid


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
		elif command == "rand" and len(int_values) == 1 and len(str_values) == 1:
			# Randomly set RGB LEDs
			self.rgb_led_groups[int_values[0]].rand(str_values[0])

class RGB_LED_Group:
	""" A cluster of RGB LEDs """

	def __init__(self, num, id):
		"""Constructor """
		self.reset(num)
		self.id = id

	def reset(self, num):
		""" Reset the LEDs """
		self.rgb_leds = []
		self.tweets = None
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
		return {"group_id": self.id, "rgb-leds": [x.get() for x in self.rgb_leds], \
			"tweets": self.tweets["categories"] if self.tweets != None and "categories" in self.tweets else None}

	def set_all(self, value):
		""" Set all the values """
		for led in self.rgb_leds:
			# print "Updating Set", self.id, "RGB", led.id, "to", value
			led.set_value(value)

	def set(self, led_id, value):
		""" Set single value """
		for led in self.rgb_leds:
			if led.id == led_id:
				# print "Updating Set", self.id, "RGB", led_id, "to", value
				led.set_value(value)
				return

	def rand(self, option):
		""" Randomly set group """
		if option == "completely":
			# Set each to a new random value
			new_rgb = RGB_LED.get_rand_rgb()
			self.set_all(new_rgb)
		elif option == "flip-flop":
			# Odds to one rand, Evens to another
			odd_color = RGB_LED.get_rand_rgb()
			even_color = RGB_LED.get_rand_rgb()
			for i, rgb_led in enumerate(self.rgb_leds):
				rgb_led.set_value(odd_color if i % 2 == 0 else even_color)

	def pulse(self, rgb):
		""" Shift all and set first """
		for i in reversed(range(len(self.rgb_leds))):
			if i == 0:
				self.rgb_leds[i].set_value(rgb)
			else:
				self.rgb_leds[i].set_dict(self.rgb_leds[i - 1].get())

	def fade(self, rgb, time_delta, transitions):
		""" Fade all over duration """
		print "fade", rgb
		for val in transitions:
			self.set_all(map(lambda v: int(math.floor(v*val)), rgb))
			time.sleep(time_delta)

	def scale_fade(self, rgb, time_delta, transitions):
		""" Scale fade from original values (0.0) to rgb (1.0) """
		print "scale fade", rgb
		original_rgbs = [rgb_led.get_rgb() for rgb_led in self.rgb_leds]
		diff_rgbs = [map(lambda orig_v, new_v: new_v - orig_v, original_rgbs[i], rgb) for i in range(len(original_rgbs))]
		for val in transitions:
			for i in range(len(original_rgbs)):
				self.set(i, map(lambda orig_v, diff: int(math.floor(orig_v + val * diff)), original_rgbs[i], diff_rgbs[i]))
			time.sleep(time_delta)

	def tweet(self, categories):
		""" Start analyzing tweets periodically """
		self.tweets = {"last-update": TweetAnalyzer.current_ms(), "categories": map(lambda category: {"name": category, "count": 0}, categories), \
			"lock": threading.Lock()}
		tweet_analyzer = TweetAnalyzer()
		tweet_analyzer.add(self)

	def add_to_tweet_category(self, category_index, amount=1):
		""" Add amount to tweet category """
		if "lock" not in self.tweets:
			return

		self.tweets["lock"].acquire()
		# print "tweet", self.id, "add", amount, "to", self.tweets["categories"][category_index]["name"]
		self.tweets["categories"][category_index]["count"] += amount
		self.tweets["lock"].release()

	def display_tweets(self):
		""" Update the RGB LEDs based on the tweet counts """
		if "lock" not in self.tweets:
			return
		
		# Get counts
		rgb = []
		total_count = 0
		self.tweets["lock"].acquire()
		for category in self.tweets["categories"]:
			rgb.append(category["count"])
			total_count += category["count"]
		self.tweets["lock"].release()

		# Divide and multiply by 255 for percentile
		if total_count != 0:
			rgb = [int(255 * v / total_count) for v in rgb]
		
		# Fade rgb values
		thread.start_new_thread(RGB_LED_Group.scale_fade, (self, rgb, TweetAnalyzer.RGB_FADE_TIME_DELTA, \
				TweetAnalyzer.RGB_FADE_FUNCTION, ))

	def reset_tweets(self):
		""" Reset the counts for tweet categories """
		if "lock" not in self.tweets:
			return
		
		self.tweets["lock"].acquire()
		for category in self.tweets["categories"]:
				category["count"] = 0
		self.tweets["lock"].release()

	def untweet(self):
		""" Stop analyzing tweets """
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

	def get_rgb(self):
		""" Returns rgb values """
		return [self.r, self.g, self.b]

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

	@staticmethod
	def get_rand_rgb():
		""" Get a random RGB value """
		return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class MathUtil:
	TWO_PI = 2 * math.pi
	FOUR_PI = 4 * math.pi

	@staticmethod
	def precompute_transition(time_delta, duration, transition):
		""" Precompute a transition function's values """
		t = 0.0
		t_chunks = time_delta / duration
		computation = []
		while t <= 1.0:
			computation.append(transition(t))
			t += t_chunks
		# End with a 0.0
		computation.append(0.0)
		return computation

class TweetAnalyzer:
	""" Analyze tweets for different boards with RGB LED groups """
	__metaclass__ = Singleton
	ANALYSIS_DURATION = 60 # Every minute, in seconds
	LANGUAGES = ["en"]
	PROPERTIES_FILE = "resources/twitter.properties"
	RGB_FADE_TIME_DELTA = 0.05
	RGB_FADE_DURATION = 3.0
	RGB_FADE_FUNCTION = MathUtil.precompute_transition(RGB_FADE_TIME_DELTA, RGB_FADE_DURATION, \
		lambda t: abs(math.sin(MathUtil.TWO_PI * t)) if t < 0.25 or t > 0.75 else (-0.25*math.cos(MathUtil.FOUR_PI*t) + 0.75))

	def __init__(self):
		""" Constructor """
		self.rgb_led_stream_listeners = {}
		self.rgb_led_streams = {}
		self.rgb_led_streams_lock = threading.Lock()
		self.load_properties()

	@staticmethod
	def current_ms():
		""" Get the current time in Milliseconds """
		return int(round(time.time() * 1000))

	def get_key(self, key):
		""" Get property by key """
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

	def add(self, rgb_led_group):
		""" Add an rgb_led_group to the analysis """
		# Remove just in case
		self.remove(rgb_led_group)

		# Lock section
		self.rgb_led_streams_lock.acquire()


		# Create listener for stream
		stream_listener = RGB_LEDStreamListener(rgb_led_group)

		# Create stream
		stream = tweepy.Stream(auth=self.__auth, listener=stream_listener)

		# Start stream in a thread
		stream.filter(track=map(lambda category: category["name"], rgb_led_group.tweets["categories"]), async=True, languages=TweetAnalyzer.LANGUAGES)

		# Add to dictionary of listeners and streams
		self.rgb_led_stream_listeners[rgb_led_group.id] = stream_listener
		self.rgb_led_streams[rgb_led_group.id] = stream


		# Release lock
		self.rgb_led_streams_lock.release()

	def remove(self, rgb_led_group):
		""" Remove an rgb_led_group from the analysis """
		self.rgb_led_streams_lock.acquire()

		# Stop stream listener and remove it
		if rgb_led_group.id in self.rgb_led_stream_listeners:
			self.rgb_led_stream_listeners[rgb_led_group.id].running = False
			self.rgb_led_stream_listeners.pop(rgb_led_group.id)
		
		# Stop stream and remove
		if rgb_led_group.id in self.rgb_led_streams:
			# print "Removing RGB LED Group", rgb_led_group.id
			self.rgb_led_streams[rgb_led_group.id].running = False
			self.rgb_led_streams.pop(rgb_led_group.id, None)

		self.rgb_led_streams_lock.release()

class RGB_LEDStreamListener(tweepy.StreamListener):
	""" Handle a stream of tweets for an RGB_LED_Group """

	def __init__(self, rgb_led_group):
		""" Constructor """
		self.rgb_led_group = rgb_led_group
		self.categories = map(lambda category: category["name"].lower(), rgb_led_group.tweets["categories"])
		self.running = True
		thread.start_new_thread(RGB_LEDStreamListener.update_RGB_LEDs, (self, ))
		super(RGB_LEDStreamListener, self).__init__()

	def determine_category(self, tweet):
		""" Return index of category with highest similarity """
		totals = []
		for category in self.categories:
			relevance = sum([tweet.count(word) for word in category.split()])
			totals.append(relevance)

		# Assume one will only have the highest similarity
		return totals.index(max(totals))

	def on_status(self, status):
		""" Handle an incoming status """
		category = self.determine_category(status.text.lower())
		self.rgb_led_group.add_to_tweet_category(category)

	def update_RGB_LEDs(self):
		""" Update the RGB LEDs periodically """
		while self.running:
			time.sleep(TweetAnalyzer.ANALYSIS_DURATION)
			self.rgb_led_group.display_tweets()