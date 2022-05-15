import sys
import random
import re
import copy
from enum import Enum
from colorama import init
from termcolor import colored

'''
commands:
wordle - picks a random word and plays with you
wordle solver - solver for wordle
wordle test - does build run stats, picks a random string for file names
wordle build strategy_file - builds strategy
wordle run strategy_file - creates leaderboard result file
wordle stats result_file - prints relevant stats (avg guess, etc)
wordle play strategy_file answer - print guesses leading to answer

functions:
play(answer, strategy) -> list of guesses, last one is answer
build(answer_list, guess_list) -> strategy
run(answer_list, strategy) -> result list
stats(result_list) -> stats



file types:
config -> points to answer list and guess list file
answer list
guess list
strategy file
reuslt file

data types:
strategy - tree, can be serialized as a text file
'''

ANSWER_LIST_FILE = "wordle-nyt-answers-alphabetical.txt"
GUESS_LIST_FILE = "wordle-nyt-allowed-guesses.txt"
MAX_GUESSES = 6

class C(Enum):
	GREEN = 1
	YELLOW = 2
	GREY = 3

class Information:
	def __init__(self, green=None, yellow=None, grey=None):
		self.green = green if green is not None else [None, None, None, None, None]
		self.yellow = yellow if yellow is not None else [set(), set(), set(), set(), set()]
		self.grey = grey if grey is not None else set()
		self.validate()

	def __repr__(self):
		return "wordle.Information({0}, {1}, {2})".format(self.green, self.yellow, self.grey)

	def set_green(self, position, letter):
		if self.green[position] is not None:
			raise Exception("Letter already there")
		self.green[position] = letter
		self.validate()

	def add_yellow(self, position, letters):
		self.yellow[position].update(letters)
		self.validate()

	def add_grey(self, letters):
		self.grey.update(letters)
		self.validate()

	def plus(self, guess, hint):
		info = copy.deepcopy(self)
		for i in range(5):
			if hint[i] == C.GREEN:
				info.set_green(i, guess[i])
			elif hint[i] == C.YELLOW:
				info.add_yellow(i, guess[i])
			else:
				info.add_grey(guess[i])
		return info

	def valid_answer(self, answer):
		for i, c in enumerate(answer):
			if c in self.yellow[i] or c in self.grey:
				return False
			if self.green[i] and self.green[i] != c:
				return False
		for y in self.yellow:
			for c in y:
				if c not in answer:
					return False
		return True

	def validate(self):
		assert type(self.green) is list
		assert len(self.green) == 5
		for c in self.green:
			assert (type(c) is str and re.fullmatch('[a-z]', c)) or c is None
		assert type(self.yellow) is list
		assert len(self.yellow) == 5
		for y in self.yellow:
			assert type(y) is set
			for c in y:
				assert type(c) is str and re.fullmatch('[a-z]', c)
		assert type(self.grey) is set
		for c in self.grey:
			assert type(c) is str and re.fullmatch('[a-z]', c)
		for i, c in enumerate(self.green):
			if c is not None:
				assert c not in self.grey
				assert c not in self.yellow[i]
		for y in self.yellow:
			for c in y:
				assert c not in self.grey

def get_hint(guess, answer):
	output = []
	for i in range(5):
		if guess[i] == answer[i]:
			output.append(C.GREEN)
		elif guess[i] in answer:
			output.append(C.YELLOW)
		else:
			output.append(C.GREY)
	return output

def hint_from_string(hint_string):
	return [{"G": C.GREEN, "Y": C.YELLOW, "-": C.GREY}[c] for c in hint_string]

def solver_by_words():
	info = Information()
	answer_list, _ = load_answer_guess_lists()
	while True:
		guess = input("Guess: ")
		if not re.fullmatch('[a-z][a-z][a-z][a-z][a-z]', guess):
			print("Bad format; guess 5 lower case letters.")
			continue
		hint_string = input("Hints: ")
		if not re.fullmatch("[-GY][-GY][-GY][-GY][-GY]", hint_string):
			print("Bad format. Use 'G' for green letters, 'Y' for yellow letters, '-' for grey letters.")
			continue
		hint = hint_from_string(hint_string)
		info = info.plus(guess, hint)
		print("Possible answers: ")
		new_list = []
		for answer in answer_list:
			if info.valid_answer(answer):
				print(answer)
				new_list.append(answer)
		answer_list = new_list

def solver_by_letters():
	info = Information()
	while True:
		green = input("Green letters (use spaces for empty spots): ")
		if re.fullmatch('[ a-z]{0,5}', green):
			break
	for i, c in enumerate(green):
		if c == " ":
			continue
		info.set_green(i, c)
	for i in range(5):
		while True:
			yellow = input("Yellow letters for spot " +
				"-----"[:i] + str(i+1) + "-----"[i+1:] +
				" (5 spots total): ")
			if re.fullmatch('[a-z]*', yellow):
				break
		info.add_yellow(i, yellow)
	while True:
		grey = input("Grey letters: ")
		if re.fullmatch('[a-z]*', grey):
			break
	info.add_grey(grey)

	print("Possible answers: ")
	answer_list, _ = load_answer_guess_lists()
	for answer in answer_list:
		if info.valid_answer(answer):
			print(answer)

def play_human():
	init() # Colorama
	answer_list, guess_list = load_answer_guess_lists()
	guess_list = set(guess_list)
	answer = random.choice(answer_list)

	for count in range(1, MAX_GUESSES + 1):
		while True:
			guess = input("Make a guess ({0}): ".format(count))
			if not re.fullmatch('[a-z][a-z][a-z][a-z][a-z]', guess):
				print("Bad format; guess 5 lower case letters.")
			elif not guess in guess_list:
				print("Not a word.")
			else:
				break

		hint = get_hint(guess, answer)
		hint_display = ""
		for i in range(5):
			color = {C.GREEN: 'on_green', C.YELLOW: 'on_yellow', C.GREY: 'on_grey'}[hint[i]]
			hint_display += colored(guess[i], 'white', color)
		print("          result: " + hint_display)

		if guess == answer:
			print("--- Nice! You guessed correctly in {0} tries! ---".format(count))
			break
	else:
		print("--- Too Bad! The correct word was {0}. ---".format(answer))

def load_answer_guess_lists():
	with open(ANSWER_LIST_FILE) as answer_file:
		with open(GUESS_LIST_FILE) as guess_file:
			answer_list = answer_file.read().splitlines()
			guess_list = guess_file.read().splitlines()
			guess_list.extend(answer_list)
			return (answer_list, guess_list)

def main():
	args = sys.argv[1:]
	if not args:
		play_human()
	elif args[0] == "solver":
		if args[1] == "words":
			solver_by_words()
		elif args[1] == "letters":
			solver_by_letters()
	elif args[0] == "test":
		pass
	elif args[0] == "build":
		strategy_file = args[1]
		pass
	elif args[0] == "run":
		strategy_file = args[1]
		pass
	elif args[0] == "stats":
		results_file = args[1]
		pass
	elif args[0] == "play":
		strategy_file = args[2]
		answer = args[1]
		pass
	else:
		print("Invalid arguments")

if __name__ == "__main__":
	main()