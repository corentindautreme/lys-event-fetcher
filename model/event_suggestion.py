class EventSuggestion():
    def __init__(self, country, name, dateTimesCet, sourceLink, watchLink):
        self.id = 0
        self.country = country
        self.name = name
        self.dateTimesCet = dateTimesCet
        self.sourceLink = sourceLink
        self.watchLink = watchLink
        self.accepted = False
        self.processed = False

    def __iter__(self):
        yield 'id', self.id
        yield 'country', self.country
        yield 'name', self.name
        yield 'dateTimesCet', self.dateTimesCet
        yield 'sourceLink', self.sourceLink
        yield 'watchLink', self.watchLink
        yield 'accepted', self.accepted
        yield 'processed', self.processed

    def __str__(self):
        return "{" + str(self.id) + ", " + self.country + ", " + self.name + ", " + str(self.dateTimesCet) + ", " + self.sourceLink + ", " + self.watchLink + "}"
