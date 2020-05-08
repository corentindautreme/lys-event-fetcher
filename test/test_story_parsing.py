import unittest
import datetime
import xml.etree.ElementTree as ET

from model.story import Story
from main import get_events_for_story
from utils.story_parsing_utils import get_nf_items_from_xml_items

class StoryParsingTest(unittest.TestCase):
	def test_if_story_contains_valid_date_then_event_should_be_extracted(self):
		story = Story(
			"Norway",
			"Norway will participate in the Eurovision Song Contest 2020. Melodi Grand Prix will again be used to select the country's entrant, with the final taking place on the 15th of February.",
			"http://link.com"
		)
		events = get_events_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(events) == 1)
		self.assertTrue(len(events[0].dateTimesCet) == 1)
		date = events[0].dateTimesCet[0]['date']
		self.assertTrue(date[5:10] == "02-15")


	def test_if_story_does_not_contain_date_within_nf_season_range_then_no_event_should_be_extracted(self):
		story = Story(
			"Sweden",
			"Jan Då has won Melodifestivalen and will represent Sweden. Sweden will take part in the first semi-final on May 12.",
			"http://link"
		)
		events = get_events_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(events) == 0)


	def test_if_story_contains_some_valid_dates_then_associated_events_should_be_extracted(self):
		story = Story(
			"Estonia",
			"Estonia will choose their representative through Eesti Laul. The semi-finals will take place on February 8 and 10, and the final on February 22. Estonia will take part in the first semi-final on May 12.",
			"http://link"
		)
		events = get_events_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(events) == 3)
		self.assertTrue(events[0].dateTimesCet[0]['date'][5:10] == "02-08")
		self.assertTrue(events[1].dateTimesCet[0]['date'][5:10] == "02-10")
		self.assertTrue(events[2].dateTimesCet[0]['date'][5:10] == "02-22")


	def test_if_story_contains_numerical_values_that_are_not_dates_these_should_not_be_extracted(self):
		story = Story(
			"France",
			"Destination Eurovision will take place on the 25th of January. Last year france was represented by Jean D'eau who won Destination Eurovision with 25% of the public vote and 155 points. He finished 16th at Eurovision 2019.",
			"http://link"
		)
		events = get_events_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(events) == 1)
		self.assertTrue(events[0].dateTimesCet[0]['date'][5:10] == "01-25")

	def test_if_xml_items_include_items_with_national_selection_category_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>First item</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<content>Content</content>
				</item>
				<item>
					<title>Second item</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
				<item>
					<title>Third item</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')

		nf_items = get_nf_items_from_xml_items(items, [])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "First item")
		self.assertTrue(titles[1] == "Third item")

	def test_if_xml_items_include_items_without_national_selection_category_but_with_nf_name_in_title_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Sweden: Melodifestivalen final on March 13</title>
					<link>https://eurovoix.com/</link>
					<category>Sweden</category>
					<content>Content</content>
				</item>
				<item>
					<title>Second item</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
				<item>
					<title>Latvia: Supernova submission window open</title>
					<link>https://eurovoix.com/</link>
					<category>Eurovision</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen', 'supernova'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "Sweden: Melodifestivalen final on March 13")
		self.assertTrue(titles[1] == "Latvia: Supernova submission window open")

	def test_if_xml_items_include_items_with_unwanted_categories_then_should_not_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Ireland: Junior Eurovision selection on October 30</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<category>Junior Eurovision Song Contest</category>
					<content>Content</content>
				</item>
				<item>
					<title>Sweden: EYM selection on February 1</title>
					<link>https://eurovoix.com/</link>
					<category>Eurovision Young Musicians</category>
					<category>National Selection</category>
					<content>Content</content>
				</item>
				<item>
					<title>Sweden: Lilla Melodifestivalen final on October 15</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<category>Junior Eurovision Song Contest</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 0)

	def test_if_xml_items_include_items_without_national_selection_category_but_with_nf_name_or_alt_name_in_title_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Sweden: Melfest final on March 13</title>
					<link>https://eurovoix.com/</link>
					<category>Sweden</category>
					<content>Content</content>
				</item>
				<item>
					<title>Finland: UMK 2021 opens submission window</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen', 'melfest', 'umk', 'uuden musiikin kilpailu'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "Sweden: Melfest final on March 13")
		self.assertTrue(titles[1] == "Finland: UMK 2021 opens submission window")
