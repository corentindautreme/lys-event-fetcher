import xml.etree.ElementTree as ET
import datetime
import requests
import re
from dateparser.search import search_dates

from model.story import Story
from model.event_suggestion import EventSuggestion
from utils.eurovision_utils import get_country_data
from utils.time_utils import is_temporal_sentence, is_day_of_week

try:
	import boto3
except ImportError:
	pass

try:
	dynamodb = boto3.resource('dynamodb')
	events_table = dynamodb.Table('lys_events')
	suggested_events_table = dynamodb.Table('lys_suggested_events')
except NameError:
	pass

events = []
suggested_events = []
NEXT_SUGGESTED_EVENT_ID = 0
event_suggestions_to_be_saved = []

country_data = get_country_data()
countries = country_data.keys()


def create_story(item):
	categories = list(map(lambda c: c.text, item.findall('category')))
	country = ""
	for cat in categories:
		if cat in countries:
			country = cat
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


def get_event_for_country(country):
	return country_data.get(country)['eventName']


def check_for_repetition_expression(sentence):
	start_every_end_pattern = ".*(start|begin).*(every|each).*(until|end|finish)"
	every_from_to_pattern = ".*(every|each).*(start|from|between|begin).*(end|to|until|and).*"
	from_to_every_pattern = ".*(from|between).*(to|until|and).*(every|each).*"

	start_every_end = re.compile(start_every_end_pattern)
	every_from_to = re.compile(every_from_to_pattern)
	from_to_every = re.compile(from_to_every_pattern)

	begin_date = None
	end_date = None
	events = []

	if re.match(start_every_end, sentence) != None:
		try:
			# Find beginning of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["start", "begin"]] if i > -1)
			idx_end = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
			begin_expression = sentence[idx_start:idx_end]
			dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				begin_date = dates[0][1]

			# Find end of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["until", "end", "finish"]] if i > -1)
			end_expression = sentence[idx_start:]
			dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				end_date = dates[0][1]

			# Determine frequency
			idx_start = sentence.find(' ', min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)) + 1
			idx_end = min(i for i in [sentence.find(token) for token in ["until", "end", "finish"]] if i > -1) -1
			frequency = re.sub(re.compile('[^a-zA-Z]'), '', sentence[idx_start:idx_end])
			if len(frequency.split(' ')) > 1:
				# TODO uncovered use case: longer frequency expression or unrecognized
				return []
			if is_day_of_week(frequency):
				# happening every specified weekday between begin and end date
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
		except Exception as e:
			print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + start_every_end_pattern + "\" - Exception is: " + str(e))


	elif re.match(every_from_to, sentence) != None:
		try:
			# Determine frequency
			idx_freq_token = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
			idx_start = sentence.find(' ', idx_freq_token) + 1
			idx_end = min(i for i in [sentence.find(token) for token in ["start", "between", "from", "begin"]] if i > -1) - 1
			frequency = re.sub(re.compile('[^a-zA-Z]'), '', sentence[idx_start:idx_end])

			# Find beginning of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["start", "between", "from", "begin"]] if i > -1)
			idx_end = min(i for i in [sentence.find(token) for token in ["end", "to", "until", "and"]] if i > -1)
			begin_expression = sentence[idx_start:idx_end]
			dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				begin_date = dates[0][1]

			# Find end of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["end", "to", "until", "and"]] if i > -1)
			idx_end = re.search(" [a-z]", sentence[idx_start:]).start()
			end_expression = sentence[idx_start:idx_start+idx_end]
			dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				end_date = dates[0][1]
			
			if len(frequency.split(' ')) > 1:
				# TODO uncovered use case: longer frequency expression or unrecognized
				return []
			if is_day_of_week(frequency):
				# happening every specified weekday between begin and end date
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
		except Exception as e:
			print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + every_from_to_pattern + "\" - Exception is: " + str(e))

	elif re.match(from_to_every, sentence) != None:
		try:
			# Find beginning of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["from", "between"]] if i > -1)
			idx_end = min(i for i in [sentence.find(token) for token in ["to", "until", "and"]] if i > -1)
			begin_expression = sentence[idx_start:idx_end]
			dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				begin_date = dates[0][1]

			# Find end of cycle
			idx_start = min(i for i in [sentence.find(token) for token in ["to", "until", "and"]] if i > -1)
			idx_end = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
			end_expression = sentence[idx_start:idx_end]
			dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []
			if len(dates) != 1:
				return []
			else:
				end_date = dates[0][1]

			# Determine frequency
			idx_freq_token = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
			idx_start = sentence.find(' ', idx_freq_token) + 1
			# frequency = sentence[idx_start:].replace(' ', '').replace(',', '').replace('.', '')
			frequency = re.sub(re.compile('[^a-zA-Z]'), '', sentence[idx_start:])

			if len(frequency.split(' ')) > 1:
				# TODO uncovered use case: longer frequency expression or unrecognized
				return []
			if is_day_of_week(frequency):
				# happening every specified weekday between begin and end date
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], ""))
				return events
		except Exception as e:
			print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + from_to_every_pattern + "\" - Exception is: " + str(e))

	return []


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

	nf_items = list(filter(lambda item: ('NATIONAL SELECTION' in list(map(lambda c: c.text.upper(), item.findall('category')))), items))

	excluded_categories = [".*JUNIOR.*", ".*YOUNG MUSICIANS.*", ".*CHOIR.*", ".*YOUNG DANCERS.*"]
	combined = "(" + ")|(".join(excluded_categories) + ")"
	nf_items = [item for item in nf_items if not any(re.match(combined, category) for category in list(map(lambda c: c.text.upper(), item.findall('category'))))]

	stories = []
	event_suggestions = []

	for item in nf_items:
		story = create_story(item)
		if story.country != "":
			stories.append(story)

	for story in stories:
		sentences = story.text.split('.')
		sentences = list(filter(lambda s: is_temporal_sentence(s), sentences))
		events_for_story = []
		dates = []
		has_semi_finals = False

		for sentence in sentences:
			if "semi-final" in sentence.lower():
				has_semi_finals = True

			sentence_events = []
			sentence_events = check_for_repetition_expression(sentence)
			for event in sentence_events:
				event.country = story.country
				event.name = get_event_for_country(story.country)
				event.sourceLink = story.sourceLink
				events_for_story.append(event)

			if len(events_for_story) > 0:
				break
			else:
				sentence = re.sub(re.compile('(January|February|March|April|May|June|July|August|September|October|November|December) ([0-9]+(?:st|nd|rd|th)*) and ([0-9]+(?:st|nd|rd|th)*)'), r'\1 \2, \1 \3,', sentence)
				sentence = re.sub(re.compile('([0-9]+(?:st|nd|rd|th)*) and ([0-9]+(?:st|nd|rd|th)*) (January|February|March|April|May|June|July|August|September|October|November|December)'), r'\1 \3, \2 \3,', sentence)
				found_dates = search_dates(sentence, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or []

				# FIltering out the false positives
				found_dates = list(filter(lambda d: re.match(re.compile("[a-z ]*20[0-9]{2}[a-z ]*"), d[0]) == None, found_dates))
				found_dates = list(filter(lambda d: not(re.match(re.compile("^[a-zA-Z ]+$"), d[0]) != None and d[1].day == datetime.datetime.now().day), found_dates))
				found_dates = list(filter(lambda d: d[1] > datetime.datetime.now(), found_dates))
				found_dates = list(filter(lambda d: d[1].year <= datetime.datetime.now().year + 2, found_dates))
				dates.extend(list(map(lambda d: {'date': d[1].strftime("%Y-%m-%d") + "T20:00:00", 'context': d[0]}, found_dates)))

		filtered_dates = []
		for date in dates:
			if not any(d['date'] == date['date'] for d in filtered_dates):
				filtered_dates.append(date)
		filtered_dates = sorted(filtered_dates, key=lambda d: d['date'])

		if len(events_for_story) == 0:
			for i in range(1,len(filtered_dates)+1):
				date = filtered_dates[i-1]
				event_suggestion = EventSuggestion(story.country, get_event_for_country(story.country), ("Semi-final " if has_semi_finals else "Night ") + str(i) if i < len(filtered_dates) else "Final", [date], story.sourceLink)
				events_for_story.append(event_suggestion)

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
