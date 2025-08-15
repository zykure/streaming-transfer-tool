
#############################################################################

def simplifiedName(text: str):
    for c in "()[]{}-:;.,":
        text = text.replace(c, '')
    return text.strip()

#############################################################################

class _TypeTemplate:
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name.strip()
        self._dirty = False

    @property
    def dirty(self):
        return self._dirty

    def setDirty(self, flag: bool):
        self._dirty = flag

    @property
    def id(self):
        return str(self._id)

    @property
    def name(self):
        return self._name

    def simplifiedName(self):
        return simplifiedName(self.name)

#############################################################################

class Artist(_TypeTemplate):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)

    def __repr__(self):
        return f"Artist(id={self.id}, name={self._name})"

    def sortKey(self):
        return (self._name.lower(),)

#############################################################################

class Album(_TypeTemplate):
    def __init__(self, id: str, name: str, artist: str):
        super().__init__(id, name)
        self.artist = artist.strip()

    def __repr__(self):
        return f"Album(id={self.id}, name={self._name}, artist={self.artist})"

    @property
    def name(self):
        return f"{self.artist} - {self._name}"

    def sortKey(self):
        return (self.artist.lower(), self._name.lower(),)

#############################################################################

class Track(_TypeTemplate):
    def __init__(self, id: str, name: str, artist: str, album: str):
        super().__init__(id, name)
        self.artist = artist.strip()
        self.album = album.strip()

    def __repr__(self):
        return f"Track(id={self.id}, name={self._name}, artist={self.artist}, album={self.album})"

    @property
    def name(self):
        return f"{self.artist} - {self.album} - {self._name}"

    def sortKey(self):
        return (self.artist.lower(), self.album.lower(), self._name.lower())

#############################################################################

class Playlist(_TypeTemplate):
    def __init__(self, id: str, name: str, descr: str, tracks: list, public: bool = False, image_url: str = ""):
        super().__init__(id, name)
        self.description = descr.strip()
        self.public = public
        self.image_url = image_url
        self._tracks = tracks

    def __repr__(self):
        return f"Playlist(id={self.id}, name={self._name}, tracks={self._tracks!r})"

    def sortKey(self):
        return (self._name.lower(),)

    def clearTracks(self):
        self._tracks = []

    def getTracks(self, chunk_size=0):
        if chunk_size > 0:
            return self.__chunks(self._tracks, chunk_size)
        return self._tracks

    def addTrack(self, track: Track):
        self._tracks.append(track)

    def numTracks(self):
        return len(self._tracks)

    @staticmethod
    def __chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
