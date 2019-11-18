from abc import abstractmethod, ABC
from pathlib import Path


class DepsResolver(ABC):
	@abstractmethod
	def __call__(self, dep):
		raise NotImplementedError()


class ExtractedInfo:
	__slots__ = ("arch", "bitness", "OSABI", "deps", "depsResolver")

	def __init__(self) -> None:
		self.arch = None
		self.OSABI = None
		self.bitness = None
		self.deps = []
		self.depsResolver = None

	def __repr__(self):
		return self.__class__.__name__ + repr((self.arch, self.deps))


class Extractor:
	def __init__(self) -> None:
		pass

	@abstractmethod
	def __call__(self, fp: Path) -> ExtractedInfo:
		raise NotImplementedError()
