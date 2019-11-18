import typing
from pathlib import Path
from File2Package import File2Package
from fuckapt import *

from ...packageManagers import File2PackageBackedPackageManager
from ...core.Package import BasePackageRef


class AptDpkg(File2PackageBackedPackageManager):
	__slots__ = ()
	
	def __init__(self):
		super().__init__(File2Package("dpkg"))

	def installByRef(self, packages:typing.Iterable[BasePackageRef]):
		aptGetInstall(p.name for p in packages)

	def installByFile(self, packages:typing.Iterable[Path]):
		dpkgInstall(packages)
	
	def download(self, downloadDir:Path, packages:typing.Iterable[BasePackageRef]) -> typing.Iterable[Path]:
		"""Downloads the packages into the dir AND CHECKS THEIR INTEGRITY!!!!"""
		raise NotImplementedError()
	
	def remove(self, packages:typing.Iterable[BasePackageRef]):
		aptGetRemove(p.name for p in packages)
		aptGetPurge()
