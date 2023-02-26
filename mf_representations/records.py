import abc

from mf_representations.enums import RecordType


class RecordBase(abc.ABC):
    """
    Base class for all type of movie, actor, genre, tmdb records
    """

    @abc.abstractproperty
    @classmethod
    def RECORD_TYPE(cls) -> str:
        """
        Indicates for which type of record this class has
        been created

        Returns:
            str: type of the record
        """
        pass

    def __init__(self, record_name: str, record_id: str) -> None:
        self.record_name = record_name
        self.record_id = record_id
        self.unique_id = self.RECORD_TYPE + self.record_id


class TmdbRecord(RecordBase):
    """
    Class for generating TMDB record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.TMDB

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)


class MovieRecord(RecordBase):
    """
    Class for generating Movie record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.MOVIE

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)


class SeriesRecord(RecordBase):
    """
    Class for generating Series record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.SERIES

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)


class ArtistRecord(RecordBase):
    """
    Class for generating people/actor/actress/director objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.ARTIST


class NetworkRecord(RecordBase):
    """
    Class for generating Network record objects
    such as a record for Universal/Paramount etc. network
    This class probably will not be used for now
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.NETWORK

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)
