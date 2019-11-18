import typing
from pathlib import Path

from File2Package import File2Package

from ..core.Package import BasePackageRef
from ..core.PackageManager import IPackageManager


class File2PackageBackedPackageManager(IPackageManager):
	__slots__ = ("f2p",)
	
	def __init__(self, f2p: File2Package):
		self.f2p = f2p
	
	def check(self, packages:typing.Iterable[typing.Union[BasePackageRef]]) -> typing.Iterable[BasePackageRef]:
		for r in packages:
			res = self.f2p[r]
			if res:
				yield res

	@property
	def isInitialized(self):
		return bool(self.f2p.db)

	def lazyEnter(self):
		self.f2p = self.f2p.__enter__()

	def lazyExit(self, *args, **kwargs):
		self.f2p.__exit__(*args, **kwargs)

	def file2Package(self, path: Path):
		return self.f2p[path]
