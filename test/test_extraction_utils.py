import unittest

from utils.extraction_utils import check_for_repetition_expression

class ExtractionUtilsTest(unittest.TestCase):
    def test_if_start_every_until_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will start on January 9 and run every Saturday until February 13"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "start on January 9 and run every Saturday until February 13")

    def test_if_another_start_every_end_expression_then_should_extract_all_events(self):
        sentence = "Melodifestivalen will start on February 6 and run every Saturday until March 13 on SVT1"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "02-13")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "02-20")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "02-27")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "03-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "03-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "start on February 6 and run every Saturday until March 13")

    def test_if_every_from_to_expression_then_should_extract_all_events(self):
        sentence = "Sanremo will run every night on RAI1 from February 4 to February 8"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 5)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == '02-04')
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == '02-05')
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == '02-06')
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == '02-07')
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == '02-08')
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0])
        self.assertTrue(events[0][0] == "every night on RAI1 from February 4 to February 8")

    def test_if_another_every_from_to_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will take place every Saturday from January 9 to February 13 on NRK1"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "every Saturday from January 9 to February 13")

    def test_if_yet_another_every_from_to_expression_then_should_extract_all_events(self):
        sentence = "Melodifestivalen will take place every Saturday from February 6 to March 13"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "02-13")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "02-20")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "02-27")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "03-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "03-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "every Saturday from February 6 to March 13")

    def test_if_from_to_every_expression_then_should_extract_all_events(self):
        sentence = "Melodi Grand Prix will run from January 9 to February 13 every Saturday"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "01-09")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "01-16")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "01-23")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "01-30")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "02-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "from January 9 to February 13 every Saturday")

    def test_if_another_from_to_every_expression_then_should_extract_all_events(self):
        sentence = "Melodifestivalen will run from February 6 to March 13 every Saturday on SVT1"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 6)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == "02-06")
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == "02-13")
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == "02-20")
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == "02-27")
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == "03-06")
        self.assertTrue(events[5][1].strftime("%Y-%m-%d")[5:] == "03-13")
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0] == events[5][0])
        self.assertTrue(events[0][0] == "from February 6 to March 13 every Saturday")

    def test_if_from_to_expression_without_frequency_token_then_should_default_to_daily_and_extract_all_events(self):
        sentence = "Sanremo 2021 will take place between February 4 and February 8"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 5)
        self.assertTrue(events[0][1].strftime("%Y-%m-%d")[5:] == '02-04')
        self.assertTrue(events[1][1].strftime("%Y-%m-%d")[5:] == '02-05')
        self.assertTrue(events[2][1].strftime("%Y-%m-%d")[5:] == '02-06')
        self.assertTrue(events[3][1].strftime("%Y-%m-%d")[5:] == '02-07')
        self.assertTrue(events[4][1].strftime("%Y-%m-%d")[5:] == '02-08')
        # verify context
        self.assertTrue(events[0][0] == events[1][0] == events[2][0] == events[3][0] == events[4][0])
        self.assertTrue(events[0][0] == "between February 4 and February 8")

    def test_if_from_to_expression_without_frequency_token_then_should_default_to_daily_but_find_that_the_interval_is_too_large_and_extract_no_event(self):
        sentence = "Sanremo 2021 will take place between February 4 and March 28"
        events = check_for_repetition_expression(sentence)
        self.assertTrue(len(events) == 0)
