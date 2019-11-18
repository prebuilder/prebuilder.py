import typing
from abc import abstractmethod, ABC
from pathlib import Path
from .Person import Maintainer
from .Package import Package, VersionedPackageRef
from .Distro import Distro
from ..styles import styles
from ..extractors.ELF import ELFExtractor
from shutil import which


class BuiltPackage(ABC):
	__slots__ = ("package", "_builtPath", "builtDir", "distro")
	packageExtension = None
	hashesSerializer = None

	"""
	@property
	def _builtPath(self):
		#import traceback
		#traceback.print_stack(tb[, limit[, file]])
		return self.__builtPath

	@_builtPath.setter
	def _builtPath(self, v):
		import traceback
		traceback.print_stack()
		self.__builtPath = v
	"""

	def __init__(self, package: Package, builtDir: Path, distro: Distro):
		self.package = package
		self._builtPath = None
		self.builtDir = builtDir
		self.distro = distro

	@property
	def builtPath(self):
		print(styles.entity("builtPath") + " " + styles.varContent(self._builtPath))
		if not self._builtPath:
			assert self.package, repr(self.package)
			assert self.builtDir, repr(self.builtDir)
			self.build(self.builtDir)
		return self._builtPath

	def generateBuiltFileName(self):
		assert self.package.name, self.package.metadata
		assert self.package.version, self.package.metadata
		assert self.package.arch, self.package.metadata
		return self.package.name + "_" + self.package.version + "_" + self.package.arch + "." + self.__class__.packageExtension

	@abstractmethod
	def createSumsMetadata(self):
		raise NotImplementedError()

	@abstractmethod
	def _build(self):
		raise NotImplementedError()

	def registerPath(self, resPath):
		return self.package.filesTracker.registerPath(resPath, self.root)

	def sign(self):
		raise NotImplementedError()

	def getMetadataDict(self):
		controlDict = type(self.package.metadata.controlDict)(self.package.metadata.controlDict)
		assert self.package.metadata.packagerSpecific is None, repr(self.package.metadata.packagerSpecific)
		#print("getMetadataDict controlDict", controlDict)

		if "maintainer" not in controlDict:
			controlDict["maintainer"] = Maintainer()
		return controlDict

	def build(self, builtPath: Path=None):
		self.createSumsMetadata()
		if not builtPath:
			if self.builtDir:
				builtPath = self.builtDir
		else:
			assert isinstance(builtPath, Path)

		if builtPath.is_dir():
			builtPath = builtPath / self.generateBuiltFileName()

		self._build(builtPath)
		self._builtPath = builtPath.resolve()
		self.sign()
		return builtPath
	
	def __repr__(self):

		return self.__class__.__name__ + "(" + self.package.ref._metadataInnerReprStr() + (", _builtPath=" + str(self._builtPath) if self._builtPath else "") + ")"
