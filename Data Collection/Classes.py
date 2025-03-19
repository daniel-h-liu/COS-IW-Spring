class Concert:
    def __init__(self, id, season, concertInfo, works):
        self.id = id
        self.season = season
        self.concertInfo = concertInfo
        self.works = works

class Work:
    def __init__(self, id, composer, title, conductor, soloists):
        self.id = id
        self.composer = composer
        self.title = title
        self.conductor = conductor
        self.soloists = soloists