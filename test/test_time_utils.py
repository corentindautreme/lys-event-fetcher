import unittest

from utils.time_utils import is_temporal_sentence, is_day_of_week

class TimeUtilsTest(unittest.TestCase):
	def test_if_sentence_contains_temporal_expression_then_is_temporal_sentence_should_return_true(self):
		sentence = "This will be decided on the 12th of February"
		self.assertTrue(is_temporal_sentence(sentence))

	def test_if_sentence_does_not_contain_temporal_expression_then_is_temporal_sentence_should_return_false(self):
		sentence = "It ended in 5th place."
		sentence2 = "It got 150 points."
		sentence3 = "It received 23% of the televote."
		self.assertFalse(is_temporal_sentence(sentence))
		self.assertFalse(is_temporal_sentence(sentence2))
		self.assertFalse(is_temporal_sentence(sentence3))

	def test_if_valid_day_of_week_then_is_day_of_week_should_return_true(self):
		self.assertTrue(is_day_of_week("Monday"))

	def test_if_invalid_day_of_week_then_is_day_of_week_should_return_true(self):
		self.assertFalse(is_day_of_week("Onsdag"))
		self.assertFalse(is_day_of_week("Fakeday"))