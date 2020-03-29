import unittest

from utils.extraction_utils import check_for_repetition_expression

class TimeUtilsTest(unittest.TestCase):
	def test_if_start_every_until_expression_then_should_extract_all_events(self):
		sentence = "Melodifestivalen will start on February 1 2020 and run every Saturday until March 7 2020."
		events = check_for_repetition_expression(sentence)
		self.assertTrue(len(events) == 6)
		self.assertTrue(events[0].dateTimesCet[0]['date'] == '2020-02-01T20:00:00')
		self.assertTrue(events[1].dateTimesCet[0]['date'] == '2020-02-08T20:00:00')
		self.assertTrue(events[2].dateTimesCet[0]['date'] == '2020-02-15T20:00:00')
		self.assertTrue(events[3].dateTimesCet[0]['date'] == '2020-02-22T20:00:00')
		self.assertTrue(events[4].dateTimesCet[0]['date'] == '2020-02-29T20:00:00')
		self.assertTrue(events[5].dateTimesCet[0]['date'] == '2020-03-07T20:00:00')

	def test_if_every_from_to_expression_then_should_extract_all_events(self):
		sentence = "Sanremo will run every night from February 4 2020 to February 8 2020."
		events = check_for_repetition_expression(sentence)
		self.assertTrue(len(events) == 5)
		self.assertTrue(events[0].dateTimesCet[0]['date'] == '2020-02-04T20:00:00')
		self.assertTrue(events[1].dateTimesCet[0]['date'] == '2020-02-05T20:00:00')
		self.assertTrue(events[2].dateTimesCet[0]['date'] == '2020-02-06T20:00:00')
		self.assertTrue(events[3].dateTimesCet[0]['date'] == '2020-02-07T20:00:00')
		self.assertTrue(events[4].dateTimesCet[0]['date'] == '2020-02-08T20:00:00')
