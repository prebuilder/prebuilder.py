__all__ = ("IPackageManager",)
import typing
from .Package import BasePackageRef, PackageRef, VersionedPackageRef
from abc import abstractmethod, ABC
from pathlib import Path
from contextlib import AbstractContextManager

from File2Package.database import File2Package
from .NamingPolicy import NamingRule


class _IPackageManager(AbstractContextManager):
	__slots__ = ()

	@abstractmethod
	def installByRef(self, packages:typing.Iterable[BasePackageRef]):
		"""Installs the requested packages in form of RESOLVED package refs into the system"""
		raise NotImplementedError()

	@abstractmethod
	def installByFile(self, packages:typing.Iterable[Path]):
		"""Installs the requested packages in form of files into the system"""
		raise NotImplementedError()

	@abstractmethod
	def download(self, downloadDir:Path, packages:typing.Iterable[BasePackageRef]) -> typing.Iterable[Path]:
		"""Downloads the packages into the dir AND CHECKS THEIR INTEGRITY!!!!"""
		raise NotImplementedError()
	
	@abstractmethod
	def remove(self, packages:typing.Iterable[BasePackageRef]):
		"""Installs the requested packages into the system"""
		raise NotImplementedError()
	
	@abstractmethod
	def check(self, packages:typing.Iterable[typing.Union[BasePackageRef]]) -> typing.Iterable[BasePackageRef]:
		"""Checks whether the packages are installed in the system and returns refs for the ones that are installed"""
		raise NotImplementedError()
	
	@abstractmethod
	def file2Package(self, file: Path):
		"""Determines the package to which file belongs"""
		raise NotImplementedError()
	
	#@abstractmethod
	def package2Files(self, pkg:BasePackageRef):
		"""Determines the package to which file belongs"""
		raise NotImplementedError()



methodsNeedInitialization = {"installByRef", "installByFile", "download", "remove", "check", "file2Package", "package2Files"}
class PackageManagerMeta(AbstractContextManager.__class__):
	def __new__(cls, className, parents, attrs, *args, **kwargs):
		attrsNew = {}
		for k, v in attrs.items():
			if k in methodsNeedInitialization and callable(v):
				def wrapper(self, *args, **kwargs):
					self.checkEntered()
					return v(self, *args, **kwargs)
				wrapper.__name__ = v.__name__ + "_checkEnteredWrapper"
				wrapper.__wraps__ = v
				attrsNew[k] = wrapper
		if attrsNew:
			attrsNew2 = type(attrs)(attrs)
			attrsNew2.update(attrsNew)
		else:
			attrsNew2 = attrs
		return super().__new__(cls, className, parents, attrsNew2, *args, **kwargs)


class IPackageManager(_IPackageManager, metaclass=PackageManagerMeta):
	__slots__ = ()
	
	def __init__(self):
		pass

	def __enter__(self):
		return self
	
	@property
	@abstractmethod
	def isInitialized(self):
		raise NotImplementedError()

	@abstractmethod
	def lazyEnter(self):
		raise NotImplementedError()

	def checkEntered(self):
		if not self.isInitialized:
			self.lazyEnter()

	@abstractmethod
	def lazyExit(self, *args, **kwargs):
		raise NotImplementedError()
	
	def __exit__(self, *args, **kwargs):
		if self.isInitialized:
			self.lazyExit(*args, **kwargs)
