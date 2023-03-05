import abc


class ConnectorBase(abc.ABC):
    """
    Connector base class. From this base, we will
    connector objects for TMDB, Supabase, and RapidApi
    """

    @classmethod
    @abc.abstractproperty
    def AUTH_TOKEN(cls) -> str:
        pass

    @classmethod
    @abc.abstractproperty
    def URL_BASE(cls) -> str:
        pass

    def __init__(self) -> None:
        super().__init__()
