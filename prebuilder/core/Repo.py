__all__ = ("IRepo",)
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from ..buildPipeline import DistroStream
from .BuiltPackage import BuiltPackage
from .Package import Package

AddableT = typing.Union[DistroStream, BuiltPackage, Path]
AddableT = typing.Union[AddableT, typing.Iterable[AddableT]]


class IRepo(ABC):
	__slots__ = ()
	kind = None

	@abstractmethod
	def __init__(self, cfg, descr, *args, **kwargs):
		raise NotImplementedError()

	@abstractmethod
	def __enter__(self):
		raise NotImplementedError()

	@abstractmethod
	def __iadd__(self, pkg: AddableT):
		raise NotImplementedError()

	@abstractmethod
	def __exit__(self, *args, **kwargs):
		raise NotImplementedError()
