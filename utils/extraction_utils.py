import re
from dateparser.search import search_dates


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
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
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
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
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
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=7)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
				return events
			elif frequency in ["day", "night", "evening"]:
				it_date = begin_date
				i = 1
				while it_date < end_date:
					events.append(EventSuggestion("", "", "Night " + str(i), [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
					it_date += datetime.timedelta(days=1)
					i += 1
				events.append(EventSuggestion("", "", "Final", [{'date': it_date.strftime("%Y-%m-%d") + "T20:00:00", 'context': ''}], "", ""))
				return events
		except Exception as e:
			print("Error parsing repetition expression \"" + sentence + "\" against pattern \"" + from_to_every_pattern + "\" - Exception is: " + str(e))

	return []