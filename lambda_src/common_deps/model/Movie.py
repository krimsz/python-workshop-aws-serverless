
class Movie:
    def __init__(self, id, primaryTitle, originalTitle, isAdult, startYear, runtimeMinutes, genres):
        self._id = id
        self._primaryTitle = primaryTitle
        self._originalTitle = originalTitle
        self._isAdult = isAdult
        self._startYear = startYear
        self._runtimeMinutes = runtimeMinutes
        self._genres = genres

    @property
    def id(self):
        return self._id

    @property
    def primaryTitle(self):
        return self._primaryTitle

    @property
    def originalTitle(self):
        return self._originalTitle

    @property
    def isAdult(self):
        return self._isAdult

    @property
    def startYear(self):
        return self._startYear

    @property
    def runtimeMinutes(self):
        return self._runtimeMinutes

    @property
    def genres(self):
        return self._genres

    def to_dict(self):
        return {
            "id": self.id,
            "primaryTitle": self.primaryTitle,
            "originalTitle": self.originalTitle,
            "isAdult": self.isAdult,
            "startYear": self.startYear,
            "runtimeMinutes": self.runtimeMinutes,
            "genres": self.genres
        }