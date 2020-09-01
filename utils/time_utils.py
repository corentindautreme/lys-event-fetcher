def is_temporal_sentence(sentence):
    temporal_expressions = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "night", "evening", "tonight", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "week", "month"]
    return any(e in sentence for e in temporal_expressions)


def is_day_of_week(string):
    return string in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def correct_typos(sentence):
    corrections = {
        "feburary": "february"
    }
    for typo, correction in corrections.items():
        sentence = sentence.replace(typo, correction)
    return sentence