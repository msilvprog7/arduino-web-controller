import random

ADJECTIVE_FILE = "config/adjectives.txt"
NOUN_FILE = "config/nouns.txt"

class NameGenerator:
	""" A way to generate board names """

	def __init__(self):
		""" Constructor """
		self.load_words()

	def get_name(self):
		""" Retrieve an adj-noun combo """
		return NameGenerator.rand_word(self.adjectives) + "-" + NameGenerator.rand_word(self.nouns)

	def load_words(self):
		""" Load in adjectives and nouns """
		self.adjectives = NameGenerator.words_from_file(ADJECTIVE_FILE)
		self.nouns = NameGenerator.words_from_file(NOUN_FILE)

	@staticmethod
	def words_from_file(filename):
		""" Obtain list of words from a file """
		words = []
		# Read from file
		with open(filename, 'r') as word_file:
			words.extend(word_file.read().split())
		return words

	@staticmethod
	def rand_word(word_list):
		""" Get a random word from the list """
		return random.choice(word_list)