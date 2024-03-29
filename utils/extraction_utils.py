import datetime
import re
import traceback
from dateparser.search import search_dates

from utils.time_utils import is_day_of_week
from model.event_suggestion import EventSuggestion


def check_for_repetition_expression(sentence):
    if not any(char.isdigit() for char in sentence):
        # no number in the sentence = no full date in the sentence, no need to go any further
        return []
    start_every_end_pattern = ".*(start|begin|commence|commencing).*(every|each|for ([1-9]|one|two|three|four|five|six|seven|eight|nine) weeks).*(until|end|finish|culminate|culminating).*"
    every_from_to_pattern = ".*(every|each).*(start|from|between|begin).*(end|to|until|and).*"
    from_to_every_pattern = ".*(from|between).*(to|until|and).*((every|each).*)*"

    start_every_end = re.compile(start_every_end_pattern)
    every_from_to = re.compile(every_from_to_pattern)
    from_to_every = re.compile(from_to_every_pattern)

    begin_date = None
    end_date = None
    event_dates = []
    current_datetime = datetime.datetime.now()

    if re.match(start_every_end, sentence) != None:
        try:
            # Find beginning of cycle
            idx_start = min(i for i in [sentence.find(token) for token in ["start", "begin", "commence", "commencing"]] if i > -1)
            idx_end = min(i for i in [sentence.find(token) for token in ["every", "each", "for"]] if i > -1)
            begin_expression = sentence[idx_start:idx_end]
            dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                begin_date = dates[0][1]
            idx_start_repetition_expression = idx_start

            # Find end of cycle
            idx_start = min(i for i in [sentence.find(token) for token in ["until", "end", "finish", "culminate", "culminating"]] if i > -1)
            idx_end = re.search(r"(January|February|March|September|October|November|December) [0-9]{,2}( [0-9]{4})*", sentence[idx_start:]).end()
            end_expression = sentence[idx_start:idx_start+idx_end]
            dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                end_date = dates[0][1]
            idx_end_repetition_expression = idx_start + idx_end

            # Determine frequency
            idx_start = sentence.find(' ', min(i for i in [sentence.find(token) for token in ["every", "each", "for"]] if i > -1)) + 1
            idx_end = min(i for i in [sentence.find(token) for token in ["until", "end", "finish", "culminate", "culminating"]] if i > -1) -1
            frequency = sentence[idx_start:idx_end].strip()

            if len(frequency.split(' ')) > 1:
                if re.match(re.compile("(.*) weeks"), frequency) != None:
                    frequency = 'Saturday'  # defautling to a random day of the week - we know it's running once a week, which day doesn't matter
                                            # since we have start & end date
                else:
                    # TODO uncovered use case: longer frequency expression or unrecognized
                    return []
            
            context = sentence[idx_start_repetition_expression:idx_end_repetition_expression]

            if is_day_of_week(frequency):
                # happening every specified weekday between begin and end date
                it_date = begin_date

                # correcting the year for upcoming dates (post containing "on February 15" in November => February 15 of the next year)
                if it_date < current_datetime and it_date.year == current_datetime.year and it_date.month <= 3:
                    it_date = it_date.replace(year=it_date.year+1)
                    end_date = end_date.replace(year=end_date.year+1)

                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=7)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
            elif frequency in ["day", "night", "evening"]:
                it_date = begin_date
                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=1)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
        except Exception as e:
            print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + start_every_end_pattern + "\" - Exception is: " + str(e))
            traceback.print_exc()


    elif re.match(every_from_to, sentence) != None:
        try:
            # Determine frequency
            idx_freq_token = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
            idx_start = sentence.find(' ', idx_freq_token) + 1
            idx_end = re.search(r'[^a-zA-Z]', sentence[idx_start:]).start()
            frequency = sentence[idx_start:idx_start+idx_end]
            idx_start_repetition_expression = idx_freq_token

            # Find beginning of cycle
            idx_start = min(i for i in [sentence.find(token) for token in ["start", "between", "from", "begin"]] if i > -1)
            idx_end = idx_start + min(i for i in [sentence[idx_start:].find(token) for token in [" end", " to", " until", " and"]] if i > -1)
            begin_expression = sentence[idx_start:idx_end]
            dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                begin_date = dates[0][1]

            # Find end of cycle
            idx_start = idx_end + min(i for i in [sentence[idx_end:].find(token) for token in ["end", "to", "until", "and"]] if i > -1)
            idx_end = re.search(r"( [a-z])|\.|$", sentence[idx_start:]).start()
            end_expression = sentence[idx_start:idx_start+idx_end]
            dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                end_date = dates[0][1]
            idx_end_repetition_expression = idx_start + idx_end

            context = sentence[idx_start_repetition_expression:idx_end_repetition_expression]
            
            if len(frequency.split(' ')) > 1:
                # TODO uncovered use case: longer frequency expression or unrecognized
                return []
            if is_day_of_week(frequency):
                # happening every specified weekday between begin and end date
                it_date = begin_date

                # correcting the year for upcoming dates (post containing "on February 15" in November => February 15 of the next year)
                if it_date < current_datetime and it_date.year == current_datetime.year and it_date.month <= 3:
                    it_date = it_date.replace(year=it_date.year+1)
                    end_date = end_date.replace(year=end_date.year+1)

                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=7)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
            elif frequency in ["day", "night", "evening"]:
                it_date = begin_date
                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=1)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
        except Exception as e:
            print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + every_from_to_pattern + "\" - Exception is: " + str(e))
            traceback.print_exc()

    elif re.match(from_to_every, sentence) != None:
        try:
            contains_frequency = any(token in sentence for token in ["each", "every"])
            # Find beginning of cycle
            idx_start = min(i for i in [sentence.find(token) for token in ["from", "between"]] if i > -1)
            idx_end = idx_start + min(i for i in [sentence[idx_start:].find(token) for token in ["to", "until", "and"]] if i > -1)
            begin_expression = sentence[idx_start:idx_end]
            dates = search_dates(begin_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                begin_date = dates[0][1]
            idx_start_repetition_expression = idx_start

            # Find end of cycle
            idx_start = idx_end + min(i for i in [sentence[idx_end:].find(token) for token in ["to", "until", "and"]] if i > -1)
            if contains_frequency:
                idx_end = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
                end_expression = sentence[idx_start:idx_end]
            else:
                end_expression = sentence[idx_start:]

            dates = search_dates(end_expression, languages=['en'], settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DAY_OF_MONTH': 'last'}) or []
            if len(dates) != 1:
                return []
            else:
                end_date = dates[0][1]

            # Determine frequency
            if contains_frequency:
                idx_freq_token = min(i for i in [sentence.find(token) for token in ["every", "each"]] if i > -1)
                idx_start = sentence.find(' ', idx_freq_token) + 1
                idx_end = re.search(r'[^a-zA-Z]|$', sentence[idx_start:]).start()
                frequency = sentence[idx_start:idx_start+idx_end]
                idx_end_repetition_expression = idx_start + idx_end
            else:
                # if no frequency expression, default to one event per night
                frequency = "night"
                idx_end_repetition_expression = len(sentence)

            context = sentence[idx_start_repetition_expression:idx_end_repetition_expression]

            if len(frequency.split(' ')) > 1:
                # TODO uncovered use case: longer frequency expression or unrecognized
                return []
            if is_day_of_week(frequency):
                # happening every specified weekday between begin and end date
                it_date = begin_date

                # correcting the year for upcoming dates (post containing "on February 15" in November => February 15 of the next year)
                if it_date < current_datetime and it_date.year == current_datetime.year and it_date.month <= 3:
                    it_date = it_date.replace(year=it_date.year+1)
                    end_date = end_date.replace(year=end_date.year+1)

                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=7)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
            elif frequency in ["day", "night", "evening"]:
                if end_date - begin_date > datetime.timedelta(days=14):
                    # the NF happens daily for more than 14 consecutive days - that seems unlikely
                    return []
                it_date = begin_date
                i = 1
                while it_date < end_date:
                    event_dates.append((context, it_date, sentence))
                    it_date += datetime.timedelta(days=1)
                    i += 1
                event_dates.append((context, it_date, sentence))
                return event_dates
        except Exception as e:
            print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + from_to_every_pattern + "\" - Exception is: " + str(e))
            traceback.print_exc()

    return []