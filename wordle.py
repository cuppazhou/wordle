import sys
import random
import re
import copy
import pickle
import time
from enum import Enum
from colorama import init
from termcolor import colored

'''
commands:
wordle - picks a random word and plays with you
wordle solver words/letters - solver for wordle
wordle test - does build run stats, picks a random string for file names
wordle build algorithm strategy_file - builds strategy
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

def load_answer_guess_lists():
	with open(ANSWER_LIST_FILE) as answer_file:
		with open(GUESS_LIST_FILE) as guess_file:
			answer_list = answer_file.read().splitlines()
			guess_list = guess_file.read().splitlines()
			guess_list.extend(answer_list)
			return (answer_list, guess_list)

class Information:
	def __init__(self, green=None, yellow=None, grey=None):
		self.green = green if green is not None else [None, None, None, None, None]
		self.yellow = yellow if yellow is not None else [set(), set(), set(), set(), set()]
		self.grey = grey if grey is not None else set()
		self.validate()

	def __repr__(self):
		return "wordle.Information({0}, {1}, {2})".format(self.green, self.yellow, self.grey)

	def set_green(self, position, letter):
		if self.green[position] is not None and self.green[position] != letter:
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
			if hint[i] == 'G':
				info.set_green(i, guess[i])
			elif hint[i] == 'Y':
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
			output.append("G")
		elif guess[i] in answer:
			output.append("Y")
		else:
			output.append("-")
	return "".join(output)

class Node:
	def __init__(self, guess):
		self.guess = guess
		self.child = dict() # hint -> Node

def build_maximize_partitions(answer_list, guess_list, level=0):
	print("Level {0}, num of answers: {1}, some answers: {2}".format(level, len(answer_list), ", ".join(answer_list[:5])))
	if level >= 6:
		raise Exception("Search got too deep.")
	if len(answer_list) == 1:
		return Node(answer_list[0])
	best_guess = None
	best_partitions = dict()
	for guess in guess_list:
		partitions = {}
		for answer in answer_list:
			hint = get_hint(guess, answer)
			if hint not in partitions:
				partitions[hint] = [answer]
			else:
				partitions[hint].append(answer)
		p, bp = len(partitions), len(best_partitions)
		if p > bp or (p == bp and 'GGGGG' in partitions):
			print("Best guess: {0}, # of paritions: {1}".format(guess, len(partitions)))
			best_guess = guess
			best_partitions = partitions
	strategy = Node(best_guess)
	for hint, answers in best_partitions.items():
		print("Hint: {0}".format(hint))
		strategy.child[hint] = build_maximize_partitions(answers, guess_list, level + 1)
	return strategy

def play(answer, strategy):
	guesses = []
	node = strategy
	while True:
		guesses.append(node.guess)
		if node.guess == answer:
			break
		hint = get_hint(node.guess, answer)
		node = node.child[hint]
	return guesses

###############################
#
# Human Interaction Section
#
###############################

def solver_by_words():
	info = Information()
	answer_list, _ = load_answer_guess_lists()
	while True:
		guess = input("Guess: ")
		if not re.fullmatch('[a-z][a-z][a-z][a-z][a-z]', guess):
			print("Bad format; guess 5 lower case letters.")
			continue
		hint = input("Hints: ")
		if not re.fullmatch("[-GY][-GY][-GY][-GY][-GY]", hint):
			print("Bad format. Use 'G' for green letters, 'Y' for yellow letters, '-' for grey letters.")
			continue
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
		colors = [{'G': 'on_green', 'Y': 'on_yellow', '-': 'on_grey'}[h] for h in hint]
		hint_display = "".join([colored(guess[i], 'white', colors[i]) for i in range(5)])
		print("          result: " + hint_display)

		if guess == answer:
			print("--- Nice! You guessed correctly in {0} tries! ---".format(count))
			break
	else:
		print("--- Too Bad! The correct word was {0}. ---".format(answer))

ALGORITHMS = {
	'max_part': build_maximize_partitions
}

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
		algorithm = ALGORITHMS[args[1]]
		file_name = str(int(time.time()))
		with open('strategies/' + file_name, 'wb') as sf:
			with open('results/' + file_name + '.txt', 'wt') as rf:
				answer_list, guess_list = load_answer_guess_lists()
				strategy = algorithm(answer_list, guess_list)
				pickle.dump(strategy, sf, pickle.HIGHEST_PROTOCOL)
				for answer in answer_list:
					guesses = play(answer, strategy)
					rf.write(", ".join(guesses) + '\n')
	elif args[0] == "build":
		algorithm = ALGORITHMS[args[1]]
		strategy_file = args[2]
		with open(strategy_file, 'wb') as sf:
			answer_list, guess_list = load_answer_guess_lists()
			strategy = algorithm(answer_list, guess_list)
			pickle.dump(strategy, sf, pickle.HIGHEST_PROTOCOL)
	elif args[0] == "run":
		strategy_file = args[1]
		results_file = args[2]
		with open(strategy_file, 'rb') as sf:
			with open(results_file, 'wt') as rf:
				strategy = pickle.load(sf)
				answer_list, _ = load_answer_guess_lists()
				for answer in answer_list:
					guesses = play(answer, strategy)
					rf.write(", ".join(guesses) + '\n')
	elif args[0] == "stats":
		results_file = args[1]
		with open(results_file, 'rt') as rf:
			guess_lines = rf.read().splitlines()
			total = 0
			for line in guess_lines:
				total += len(line.split(", "))
			print("Avg guesses: {0}, Total guesses: {1}".format(total / len(guess_lines), total))
	elif args[0] == "play":
		strategy_file = args[1]
		answer = args[2]
		with open(strategy_file, 'rb') as sf:
			strategy = pickle.load(sf)
			guesses = play(answer, strategy)
			print(", ".join(guesses))
	else:
		print("Invalid arguments")

if __name__ == "__main__":
	main()