import re

def get_nf_items_from_xml_items(items, nf_names):
	# NF items = items that have the "National selection" category or that have the name of a NF in their title
	nf_items = list(filter(lambda item: ('NATIONAL SELECTION' in list(map(lambda c: c.text.upper(), item.findall('category')))) or (any(nf_name in item.find('title').text.lower() for nf_name in nf_names)), items))

	# filtering out the items that are related to the sister Eurovision events (JESC, EYM, EYD, Choir)
	excluded_categories = [".*JUNIOR.*", ".*YOUNG MUSICIANS.*", ".*CHOIR.*", ".*YOUNG DANCERS.*"]
	combined = "(" + ")|(".join(excluded_categories) + ")"
	nf_items = [item for item in nf_items if not any(re.match(combined, category) for category in list(map(lambda c: c.text.upper(), item.findall('category'))))]

	return nf_items