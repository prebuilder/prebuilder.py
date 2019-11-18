import typing
from collections import defaultdict, OrderedDict
from pathlib import Path
import inspect

from os import readlink, linesep, fchdir
import os
import shutil
import warnings
import sh

from AnyVer import AnyVer, _AnyVer
from File2Package.interfaces import VersionedPackageRef, BasePackageRef, PackageRef

from fsutilz import nestPath, copytree, movetree, symlink
from ..utils.ReprMixin import ReprMixin
from .FilesTracker import FilesTracker


class PackageInstallSpec:
	"""Shitty install speck that almost never needed. It is just a temporary storage for the raw data parsed from the things like debian directory"""

	__slots__ = ("install", "manpages", "docs", "dirs", "links", "symbols")

	def __init__(self):
		for n in __class__.__slots__:
			setattr(self, n, None)

#class PackageRef(PackageRef):
#	__slots__ = PackageRef.__slots__
#	def __init__(self, name: str, arch: str = "amd64", group: typing.Optional[str] = None, versionPostfix: int = 0):
#		from traceback import print_stack
#		print_stack()
#		super().__init__(name, arch, group, versionPostfix)
#	__init__.__wraps__ = PackageRef.__init__


class PackageMetadata:
	"""Stores metadata about package to be embedded into a package"""

	__slots__ = ("ref", "controlDict", "packagerSpecific")

	def __init__(self, ref: PackageRef, packagerSpecific: typing.Optional[defaultdict] = None, **kwargs) -> None:
		if isinstance(ref, str):
			ref = PackageRef(ref, None, None)
		self.ref = ref
		self.controlDict = dict()
		self.controlDict.update(kwargs)
		#if packagerSpecific is None:
		#	packagerSpecific = {}
		self.packagerSpecific = packagerSpecific

	@property
	def name(self):
		return self.ref.name

	@name.setter
	def name(self, val: str):
		self.ref.name = val

	@property
	def arch(self):
		return self.ref.arch

	@arch.setter
	def arch(self, val: str):
		self.ref.arch = val

	@property
	def version(self):
		return self.ref.version

	@version.setter
	def version(self, val: str):
		self.ref.version = val

	def _metadataInnerReprStr(self) -> str:
		return "ref=" + repr(self.ref) + ", **" + repr(self.controlDict) + ",.."

	def __repr__(self):
		return self.__class__.__name__ + "(" + self._metadataInnerReprStr() + ")"


class PackageInstalledFiles:
	"""Represents a dir where files installed by a package reside"""

	__slots__ = ("ref", "root", "filesTracker", "needsTearing", "depsResolver")

	def __init__(self, ref: VersionedPackageRef, root: Path, needsTearing: bool = False) -> None:
		self.ref = ref
		self.root = root
		self.filesTracker = FilesTracker()
		self.needsTearing = needsTearing

	def nest(self, p: Path) -> Path:
		return nestPath(self.root, p)

	def resolvePath(self, p: Path, recurseSymlinks=True) -> Path:
		while p.is_symlink():
			p = self.nest(readlink(p))

		return p.resolve()

	def registerPath(self, resPath: Path, hashes: None = None) -> None:
		return self.filesTracker.registerPath(resPath, self.root, hashes=None)

	def copy(self, src, dst, hashes=None):
		"""src is path, dst is an abstract path within root"""
		resPath = self.nest(dst)
		copytree(src, resPath)
		self.registerPath(resPath, hashes=hashes)

	def symlink(self, src, dst, relativeTo=None, symlinks=None):
		"""src is path, dst is an abstract path within root"""
		resPath = self.nest(dst)
		symlink(src, resPath, relativeTo)
		self.filesTracker.symlinks.append(resPath)

	def rip(self, src, dst, hashes=None):
		"""src is path, dst is an abstract path within root"""
		resPath = self.nest(dst)

		if (resPath.exists() or resPath.is_symlink()) and not (src.exists() or src.is_symlink()):
			warnings.warn(str(resPath) + " already exists")
		elif resPath.exists() and resPath.is_dir():
			self.copy(src, resPath)
		else:
			#print("src", src, "res", resPath, resPath.exists(), src.is_dir(), src.is_symlink())

			if src.is_dir():
				resPath.mkdir(parents=True, exist_ok=True)
			else:
				resPath.parent.mkdir(parents=True, exist_ok=True)

			src.rename(resPath)

			self.registerPath(resPath, hashes=hashes)

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.ref._metadataInnerReprStr() + ")"


def getPackageInstalledFilesFromRefAndParent(ref: VersionedPackageRef, parentDirOfPackageRoots: Path, needsTearing: bool = True) -> PackageInstalledFiles:
	return PackageInstalledFiles(ref, (parentDirOfPackageRoots / ref.toPath()).absolute(), needsTearing=needsTearing)

SubPackagingSpecT = typing.Iterable[typing.Tuple[typing.Union[VersionedPackageRef, PackageMetadata], "TearingSpec"]]

class PackagingSpec(ReprMixin):
	"""A set of info needed to tear a package into multiple packages, assigning individual metadata to each"""

	__slots__ = ("commonMetadata", "tearingSpecs")

	def __init__(self, commonMetadata: PackageMetadata, tearingSpecs: SubPackagingSpecT = None) -> None:
		assert commonMetadata is None or isinstance(commonMetadata, PackageMetadata)
		self.commonMetadata = commonMetadata
		self.tearingSpecs = tearingSpecs


class AssociateTearingSpecAndMetadata(ReprMixin):
	__slots__ = ("installation", "packagingSpec")

	def __init__(self, installation: PackageInstalledFiles, packagingSpec: PackagingSpec = None) -> None:
		assert isinstance(installation, PackageInstalledFiles)
		assert packagingSpec is None or isinstance(packagingSpec, PackagingSpec)
		self.installation = installation
		self.packagingSpec = packagingSpec

	@property
	def ref(self):
		return self.installation.ref

	@ref.setter
	def ref(self, val: str):
		self.installation.ref = val


class Package:
	"""A class representing a package that is not yet built with the tool building packages. Contains package metadata and its dir."""

	__slots__ = ("metadata", "installation", "deps", "depsResolver")

	def __init__(self, metadata: PackageMetadata, installation: PackageInstalledFiles = None) -> None:
		self.metadata = metadata
		self.installation = installation
		self.deps = None
		self.depsResolver = None

	@property
	def filesTracker(self) -> FilesTracker:
		return self.installation.filesTracker

	@property
	def ref(self):
		return self.metadata.ref

	@ref.setter
	def ref(self, val: str):
		self.metadata.ref = val

	@property
	def name(self):
		return self.metadata.name

	@name.setter
	def name(self, val: str):
		self.metadata.name = val

	@property
	def arch(self):
		return self.metadata.arch

	@arch.setter
	def arch(self, val: str):
		self.metadata.arch = val

	@property
	def version(self):
		return self.metadata.version

	@version.setter
	def version(self, val: str):
		self.metadata.version = val

	def nest(self, p: Path) -> Path:
		return self.installation.nest(p)

	def resolvePath(self, p: Path, recurseSymlinks=True) -> Path:
		return self.installation.resolvePath(p, recurseSymlinks)

	def registerPath(self, resPath):
		return self.installation.registerPath(resPath)

	def copy(self, src, dst):
		return self.installation.copy(src, dst)

	def rip(self, src, dst):
		return self.installation.rip(src, dst)

	def __repr__(self) -> str:
		return self.__class__.__name__ + "(" + self.metadata._metadataInnerReprStr() + ")"
