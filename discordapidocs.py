from typing import Self

class DiscordAPiDocs():
    BASE_URL = "https://discord.com/developers/docs"

    def __init__(self, url: str):
        self._url = url
    
    @classmethod
    def _construct_url(cls, field: str, module: str) -> Self:
        return cls(
            f"{cls.BASE_URL}/{field.lower()}/{module}"
        )
    
    @classmethod
    def _construct_url_with_query(cls, field: str, module: str, query:str) -> Self:
        return cls(
            f"{cls.BASE_URL}/{field.lower()}/{module}#{query}"
        )

    @property
    def url(self) -> str:
        return self._url
