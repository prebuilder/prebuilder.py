import typing
from abc import abstractmethod, ABC
import os

from ..styles import styles
from .. import globalPrefs
from ..utils.ReprMixin import ReprMixin

from AnyVer import AnyVer
class Fetched(ReprMixin):
	__slots__ = ("time", "version")
	
	def __init__(self, time: float, version: AnyVer) -> None:
		self.time = time
		self.version = version

class IFetcher(ABC):
	__slots__ = ()

	@abstractmethod
	def __call__(self, dir, versionNeeded: bool=True) -> Fetched:
		raise NotImplementedError()


class IURIFetcher(IFetcher):
	__slots__ = ("uri",)

	def __init__(self, uri: str, refspec: typing.Optional[str] = None) -> None:
		self.uri = uri


class IRepoFetcher(IURIFetcher):
	__slots__ = ("refspec", "repo")

	def __init__(self, uri: str, refspec: typing.Optional[str] = None) -> None:
		super().__init__(uri)
		self.refspec = refspec
		self.repo = None


defaultRepoFetcher = None  # set in tools.git
