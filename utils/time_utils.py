def is_temporal_sentence(sentence):
	temporal_expressions = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "night", "evening", "tonight", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "week", "month"]
	return any(e in sentence for e in temporal_expressions)


def is_day_of_week(string):
	return string in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]