## A Simple Wordle Command Line Game and Solver

To start a game just run `python3 wordle.py`. 

To start the solver, run `python3 wordle.py solver words`, which will prompt you for your current guesses and given hints, and give you a list of valid words. To input hints, use 'G' for green (correctly placed) letters, 'Y' for yellow (good but wrong place) letters, and '-' for bad letters; e.g. If you guessed 'crane' and 'r' was green and 'e' was yellow, you would put in '-G--Y' for the hint.

There is even more functionality, such as generating a decision tree to minimize the number of guesses across all possible answers, in the tool. See `wordle.py` for more information.
