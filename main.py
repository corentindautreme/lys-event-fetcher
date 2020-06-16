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

def get_dynamo_data():
    events = []
    suggestions = []
    countries_data = {}
    suggestions_table = None

    try:
        dynamodb = boto3.resource('dynamodb')
        events_table = dynamodb.Table('lys_events')
        suggestions_table = dynamodb.Table('lys_suggested_events')
        country_ref_table = dynamodb.Table('lys_ref_country')

        events = events_table.scan()['Items']
        suggestions = suggestions_table.scan()['Items']
        for d in country_ref_table.scan()['Items']:
            countries_data[d['country']] = d
    except NameError:
        countries_data = get_countries_data()
        pass

    return events, suggestions, suggestions_table, countries_data


def create_story(item, countries):
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


def get_suggestion_for_story(story, current_datetime, country_data):
    if country_data is None:
        country_data = {'eventName': '-', 'stages': ['Night...', 'Final'], 'watchLink': '-'}
        print("WARNING: No referential data found for country " + story.country)
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
            found_dates.extend(list(map(lambda found_date: found_date + (sentence,), search_dates(sentence, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False}) or [])))

    # correcting the years for upcoming dates (post containing "on February 15" in November => February 15 of the next year)
    # we're only applying this correction if current month >= April (so we don't catch fake positives by mistake, e.g "The semi-final took place on February 8 and...")
    if current_datetime.month >= 4:
        for i, date in enumerate(found_dates):
            if date[1] < current_datetime and date[1].year == current_datetime.year and date[1].month <= 3:
                found_dates[i] = (date[0], date[1].replace(year=date[1].year+1), date[2])

    # filtering out the false positives
    # non-dates ("placed 12th in the final", "got 20% of the vote", etc.)
    found_dates = list(filter(lambda d: is_temporal_sentence(d[0]), found_dates))
    # too close (like this day next week or such)
    found_dates = list(filter(lambda d: not(re.match(re.compile("^[a-zA-Z ]+$"), d[0]) != None and d[1].day == current_datetime.day), found_dates))
    # past dates
    found_dates = list(filter(lambda d: d[1] > current_datetime, found_dates))
    # beyond 2 years in the future
    found_dates = list(filter(lambda d: d[1].year <= current_datetime.year + 2, found_dates))
    # before september or beyond march
    found_dates = list(filter(lambda d: d[1].month >= 9 and d[1].month <= 12 or d[1].month <= 3, found_dates))
    
    if len(found_dates) == 0:
        return None

    dates = []
    dates.extend(list(map(lambda d: {'dateTimeCet': d[1].strftime("%Y-%m-%d") + "T20:00:00", 'context': d[0], 'sentence': d[2]}, found_dates)))

    filtered_dates = []

    for date in dates:
        # filtering out duplicates
        if not any(d['dateTimeCet'] == date['dateTimeCet'] for d in filtered_dates):
            filtered_dates.append(date)
    filtered_dates = sorted(filtered_dates, key=lambda d: d['dateTimeCet'])

    return EventSuggestion(story.country, country_data['eventName'], filtered_dates, story.sourceLink, country_data['watchLink'])


def get_suggestion_for_saving(suggestion, suggestions_to_be_saved, events, suggestions):
    # remove dates for which an event with that name already exists in list
    suggestion.dateTimesCet = [date for date in suggestion.dateTimesCet if not any(e['dateTimeCet'][0:10] == date['dateTimeCet'][0:10] and e['name'] == suggestion.name for e in events)]
    # remove dates for which an event suggestion for that NF was already saved
    suggestion.dateTimesCet = [date for date in suggestion.dateTimesCet if not any(date['dateTimeCet'][0:10] in list(map(lambda d: d['dateTimeCet'][0:10], s['dateTimesCet'])) and s['name'] == suggestion.name for s in suggestions)]
    # remove dates for which an event for that NF was already suggested in the current run
    suggestion.dateTimesCet = [date for date in suggestion.dateTimesCet if not any(date['dateTimeCet'][0:10] in list(map(lambda d: d['dateTimeCet'][0:10], s.dateTimesCet)) and s.name == suggestion.name for s in suggestions_to_be_saved)]

    return suggestion if len(suggestion.dateTimesCet) > 0 else None


def fetch_events(lambda_event, is_local_env):
    IS_TEST = "isTest" in lambda_event or is_local_env

    (events, suggestions, suggestions_table, countries_data) = get_dynamo_data() if not is_local_env else ([], [], None, get_countries_data())
    
    countries = countries_data.keys()
    # grouping all nf names and alt names into one unique list of nf names
    nf_name_list = map(lambda d: [d['eventName']] + d['altEventNames'], list(countries_data.values()))
    nf_names = set([nf_name.lower() for name_list in nf_name_list for nf_name in name_list])

    seq_suggestion_id = 0
    try:
        seq_suggestion_id = max(e['id'] for e in suggestions) + 1
    except ValueError: pass

    source = "https://eurovoix.com/feed/"
    xml = requests.get(source).content
    root = ET.fromstring(xml)
    items = root.find('channel').findall('item')

    nf_items = get_nf_items_from_xml_items(items, nf_names)

    stories = []
    extracted_suggestions = []
    suggestions_to_be_saved = []

    for item in nf_items:
        story = create_story(item, countries)
        if story.country != "":
            stories.append(story)

    for story in stories:
        suggestion = get_suggestion_for_story(story, current_datetime=datetime.datetime.now(), country_data=countries_data[story.country])
        if suggestion is not None:
            extracted_suggestions.append(suggestion)

    print("Extracted suggestions:")
    for suggestion in extracted_suggestions:
        print(suggestion)
        s = get_suggestion_for_saving(suggestion, suggestions_to_be_saved, events, suggestions)
        if s is not None:
            s.id = seq_suggestion_id
            seq_suggestion_id += 1
            suggestions_to_be_saved.append(s)

    print("\nSaved suggestions:")
    for suggestion in suggestions_to_be_saved:
        print(suggestion.__str__())
        if(not IS_TEST):
            try:
                suggestions_table.put_item(Item=dict(suggestion))
            except Exception as e:
                print("* Unable to save suggestion " + str(suggestion) + " - Exception is " + str(e))


def main(event, context):
    fetch_events(lambda_event=event, is_local_env=False)


if __name__ == '__main__':
    fetch_events(lambda_event={}, is_local_env=True)
