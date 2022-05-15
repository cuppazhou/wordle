import wordle
import unittest

class TestInformation(unittest.TestCase):

	def test_valid_answer_empty(self):
		info = wordle.Information()
		answer_list, _ = wordle.load_answer_guess_lists()
		for answer in answer_list:
			self.assertTrue(info.valid_answer(answer))

	def test_valid_answer_green(self):
		info = wordle.Information()
		info.set_green(0, "a")
		self.assertEqual(info.valid_answer("axxxx"), True)
		self.assertEqual(info.valid_answer("bxxxx"), False)

	def test_valid_answer_yellow(self):
		info = wordle.Information()
		info.add_yellow(0, "a")
		self.assertEqual(info.valid_answer("xxxxx"), False)
		self.assertEqual(info.valid_answer("axxxx"), False)
		self.assertEqual(info.valid_answer("xaxxx"), True)
		self.assertEqual(info.valid_answer("aaxxx"), False)
		self.assertEqual(info.valid_answer("xaxax"), True)
		info.add_yellow(0, "b")
		self.assertEqual(info.valid_answer("xxxxx"), False)
		self.assertEqual(info.valid_answer("axxxx"), False)
		self.assertEqual(info.valid_answer("bxxxx"), False)
		self.assertEqual(info.valid_answer("xaxxx"), False)
		self.assertEqual(info.valid_answer("xbxxx"), False)
		self.assertEqual(info.valid_answer("xabxx"), True)
		self.assertEqual(info.valid_answer("aabxx"), False)
		self.assertEqual(info.valid_answer("xabab"), True)
		info.add_yellow(1, "c")
		self.assertEqual(info.valid_answer("xcabx"), False)
		self.assertEqual(info.valid_answer("xxabc"), True)
		self.assertEqual(info.valid_answer("cabxx"), True)

	def test_valid_answer_grey(self):
		info = wordle.Information()
		info.add_grey("a")
		self.assertEqual(info.valid_answer("xxxxx"), True)
		self.assertEqual(info.valid_answer("xxxxa"), False)

	def test_valid_answer_example(self):
		info = wordle.Information(
			["a", None, None, None, None],
			[set(), {"b"}, set(), set(), set()],
			{"c"})
		answer_list, _ = wordle.load_answer_guess_lists()
		valid_answers = list(filter(info.valid_answer, answer_list))
		valid_answers.sort()
		self.assertEqual(valid_answers, ["adobe", "album", "alibi", "amber", "amble", "arbor"])
