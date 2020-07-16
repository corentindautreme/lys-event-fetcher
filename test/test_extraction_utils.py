import unittest

from utils.extraction_utils import check_for_repetition_expression

class ExtractionUtilsTest(unittest.TestCase):
    def test_if_start_every_until_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will start on January 9 and run every Saturday until February 13."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")

    def test_if_another_start_every_end_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will start on January 9 and run every Saturday until February 13."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")

    def test_if_every_from_to_expression_then_should_extract_all_events(self):
        sentence = "Sanremo will run every night from February 4 to February 8."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 5)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == '02-04')
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == '02-05')
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == '02-06')
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == '02-07')
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == '02-08')

    def test_if_another_every_from_to_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will take place every Saturday from January 9 to February 13."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")

    def test_if_from_to_every_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will run from January 9 to February 13 every Saturday."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")

    def test_if_another_from_to_every_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will run from January 9 to February 13 every Saturday."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")

    def test_if_from_to_expression_without_frequency_token_then_should_default_to_daily_and_extract_all_events(self):
        sentence = "Sanremo 2021 will take place between February 4 and February 8."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 5)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == '02-04')
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == '02-05')
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == '02-06')
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == '02-07')
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == '02-08')

    def test_if_from_to_expression_without_frequency_token_then_should_default_to_daily_but_find_that_the_interval_is_too_large_and_extract_no_event(self):
        sentence = "Sanremo 2021 will take place between February 4 and March 28."
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 0)
