import xml.etree.ElementTree as ET
import datetime
import requests
import re
import string
from dateparser.search import search_dates

from model.story import Story
from model.event_suggestion import EventSuggestion
from utils.eurovision_utils import get_countries_data, generate_event_stages
from utils.time_utils import is_temporal_sentence, is_day_of_week
from utils.extraction_utils import check_for_repetition_expression
from utils.story_parsing_utils import get_nf_items_from_xml_items

try:
	import boto3
except ImportError:
	pass

try:
	dynamodb = boto3.resource('dynamodb')
	events_table = dynamodb.Table('lys_events')
	suggested_events_table = dynamodb.Table('lys_suggested_events')
	country_ref_table = dynamodb.Table('lys_ref_country')

	ccountries_data = {}
	for d in country_ref_table.scan()['Items']:
		countries_data[d['country']] = d
except NameError:
	countries_data = get_countries_data()
	pass

events = []
suggested_events = []
NEXT_SUGGESTED_EVENT_ID = 0
event_suggestions_to_be_saved = []

countries = countries_data.keys()
nf_names = set(map(lambda d: d['eventName'].lower(), list(countries_data.values())))
for c in countries_data.values():
	nf_names = nf_names.union(set(map(lambda e: e.lower(), c['altEventNames'])))
nf_names.remove("-")


def create_story(item):
	categories = list(map(lambda c: c.text, item.findall('category')))
	country = ""
	for cat in categories:
		if cat in countries:
			country = cat
			break

	# if no country found in the category, try the title
	if country == "":
		title = item.find('title').text
		for word in title.translate(str.maketrans('', '', string.punctuation)).split(' '):
			if word in countries:
				country = word
				break

	if country == "":
		return Story("", "", "")

	content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text.replace('<!--[CDATA[', '').replace(']]>', '').replace('\n', '.')
	try:
		content = content[0:content.index('Source: ')]
	except ValueError:
		pass
	content = re.sub(re.compile('<.*?>'), '', content)
	# content = re.sub(re.compile(r"\\x[a-z0-9]+"), '', content)
	content = re.sub(re.compile(r"&#[0-9]+;"), '', content)
	return Story(country, content, item.find('link').text)


def get_country_data(country):
	return countries_data.get(country)


def mark_event_suggestion_for_saving(suggested_event):
	global NEXT_SUGGESTED_EVENT_ID

	# remove dates for which an event with that name already exists in list
	suggested_event.dateTimesCet = [date for date in suggested_event.dateTimesCet if not any(e['dateTimeCet'][0:10] == date['date'][0:10] and e['name'] == suggested_event.name for e in events)]
	# remove dates for which an event suggestion for that NF was already saved
	suggested_event.dateTimesCet = [date for date in suggested_event.dateTimesCet if not any(date['date'][0:10] in list(map(lambda d: d[0:10], e['dateTimesCet'])) and e['name'] == suggested_event.name for e in suggested_events)]
	# remove dates for which an event for that NF was already suggested in the current run
	suggested_event.dateTimesCet = [date for date in suggested_event.dateTimesCet if not any(date['date'][0:10] in list(map(lambda d: d['date'][0:10], e.dateTimesCet)) and e.name == suggested_event.name for e in event_suggestions_to_be_saved)]

	if len(suggested_event.dateTimesCet) > 0:
		suggested_event.id = NEXT_SUGGESTED_EVENT_ID
		NEXT_SUGGESTED_EVENT_ID += 1
		event_suggestions_to_be_saved.append(suggested_event)


def get_events_for_story(story, current_datetime):
	country_data = get_country_data(story.country)
	sentences = story.text.split('.')
	sentences = list(filter(lambda s: is_temporal_sentence(s), sentences))
	found_dates = []

	for sentence in sentences:
		sentence_events = []
		repetition_dates = check_for_repetition_expression(sentence)

		if len(repetition_dates) > 0:
			found_dates = repetition_dates
			break
		else:
			# Correcting sentences by adding repetition where needed to make it easier for the date parser:
			# January 1 & 2 => January 1 and January 2; 1st and 2nd January => 1st January and 2nd January
			sentence = re.sub(re.compile('(January|February|March|April|May|June|July|August|September|October|November|December) ([0-9]+(?:st|nd|rd|th)*) and ([0-9]+(?:st|nd|rd|th)*)'), r'\1 \2, \1 \3,', sentence)
			sentence = re.sub(re.compile('([0-9]+(?:st|nd|rd|th)*) and ([0-9]+(?:st|nd|rd|th)*) (January|February|March|April|May|June|July|August|September|October|November|December)'), r'\1 \3, \2 \3,', sentence)
			found_dates.extend(search_dates(sentence, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or [])

	# correcting the years for upcoming dates (post containing "on February 15" in November => February 15 of the next year)
	# we're only applying this correction if current month >= April (so we don't catch fake positives by mistake, e.g "The semi-final took place on February 8 and...")
	if current_datetime.month >= 4:
		for i, date in enumerate(found_dates):
			if date[1] < current_datetime and date[1].year == current_datetime.year and date[1].month <= 3:
				found_dates[i] = (date[0], date[1].replace(year=date[1].year+1))

	# filtering out the false positives
	# non-dates ("placed 12th in the final", "got 20% of the vote", etc.)
	found_dates = list(filter(lambda d: is_temporal_sentence(d[0]), found_dates))
	# years ("in 2019", etc.)
	found_dates = list(filter(lambda d: re.match(re.compile("[a-z ]*20[0-9]{2}[a-z ]*"), d[0]) == None, found_dates))
	# too close (like this day next week or such)
	found_dates = list(filter(lambda d: not(re.match(re.compile("^[a-zA-Z ]+$"), d[0]) != None and d[1].day == current_datetime.day), found_dates))
	# past dates
	found_dates = list(filter(lambda d: d[1] > current_datetime, found_dates))
	# beyond 2 years in the future
	found_dates = list(filter(lambda d: d[1].year <= current_datetime.year + 2, found_dates))
	# before september or beyond march
	found_dates = list(filter(lambda d: d[1].month >= 9 and d[1].month <= 12 or d[1].month <= 3, found_dates))
	
	dates = []
	dates.extend(list(map(lambda d: {'date': d[1].strftime("%Y-%m-%d") + "T20:00:00", 'context': d[0]}, found_dates)))

	filtered_dates = []

	for date in dates:
		# filtering out duplicates
		if not any(d['date'] == date['date'] for d in filtered_dates):
			filtered_dates.append(date)
	filtered_dates = sorted(filtered_dates, key=lambda d: d['date'])
	
	stages_for_events = generate_event_stages(len(filtered_dates), country_data['stages'], story.country)
	events_for_story = []

	for i in range(0,len(filtered_dates)):
		date = filtered_dates[i]
		event_suggestion = EventSuggestion(story.country, country_data['eventName'], stages_for_events[i], [date], story.sourceLink, country_data['watchLink'])
		events_for_story.append(event_suggestion)

	return events_for_story


def extract_events(event, is_local_env):
	global events
	global suggested_events
	global NEXT_SUGGESTED_EVENT_ID

	IS_TEST = "isTest" in event or is_local_env

	events = []
	if not is_local_env:
		events = events_table.scan()['Items']

	suggested_events = []
	if not is_local_env:
		suggested_events = suggested_events_table.scan()['Items']

	NEXT_SUGGESTED_EVENT_ID = 0
	try:
		NEXT_SUGGESTED_EVENT_ID = max(e['id'] for e in suggested_events) + 1
	except ValueError:
		pass

	source = "https://eurovoix.com/feed/"
	xml = requests.get(source).content
	root = ET.fromstring(xml)

	items = root.find('channel').findall('item')

	nf_items = get_nf_items_from_xml_items(items, nf_names)

	stories = []
	event_suggestions = []

	for item in nf_items:
		story = create_story(item)
		if story.country != "":
			stories.append(story)
	stories = [Story("Norway", "The final will take place on February 22.", "http://nrk.no")]
	for story in stories:
		events_for_story = get_events_for_story(story, datetime.datetime.now())
		event_suggestions.extend(events_for_story)

	print("Extracted events:")
	for event in event_suggestions:
		print(event)
		mark_event_suggestion_for_saving(event)

	print("\nSaved event suggestions:")
	for event in event_suggestions_to_be_saved:
		print(event.__str__())
		if(not IS_TEST):
			try:
				suggested_events_table.put_item(Item=dict(event))
			except Exception as e:
				print("* Unable to save event " + str(event) + " - Exception is " + str(e))


def main(event, context):
	extract_events(event, False)


if __name__ == '__main__':
	extract_events({}, True)
