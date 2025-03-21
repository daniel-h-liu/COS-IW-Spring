class Concert:
    def __init__(self, id, programID, orchestra, season, concerts, works):
        self.id = id
        self.programID = programID
        self.orchestra = orchestra
        self.season = season
        self.concerts = concerts
        self.works = works
    
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "programID": self.programID,
    #         "orchestra": self.orchestra,
    #         "season": self.season,
    #         "concerts": self.concerts,
    #         "works": self.works
    #     }

class Work:
    def __init__(self, id, programID, composer, title, movement, conductor, soloists):
        self.id = id
        self.programID = programID
        self.composer = composer
        self.title = title
        self.movement = movement
        self.conductor = conductor
        self.soloists = soloists

    # def to_dict(self):
    #     return {
    #         "ID": self.id,
    #         "composer": self.composer,
    #         "title": self.title,
    #         "movement": self.movement,
    #         "conductor": self.conductor,
    #         "soloists": self.soloists
    #     }