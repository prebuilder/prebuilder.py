import typing
from .Package import BasePackageRef, PackageRef, VersionedPackageRef
from datetime import datetime

from .NamingPolicy import NamingRule
from .Tearer import Tearer
from .PackageManager import IPackageManager

class DistroRelease:
	"""None `time` means not yet released"""

	__slots__ = ("version", "time")

	def __init__(self, version, time: datetime = None):
		self.version = version
		self.time = time

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.version) + ")"


class CodenamedDistroRelease(DistroRelease):
	"""None `time` means not yet released"""

	__slots__ = ("codenames",)

	origin = "Debian"

	def __init__(self, version, time: datetime = None, codenames=("stretch", "stable")):
		self.codenames = codenames
		super().__init__(version, time)

	@property
	def codename(self):
		return self.codenames[0]

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.codenames) + ", " + repr(self.version) + ")"


class Distro:
	__slots__ = ("name", "dirsConventions", "tearer", "namingPolicy", "builder", "packageManager", "archTransformer", "repoClass", "decodeAnotherPackageRefIntoStr_")

	def __init__(self, name: str, dirsConventions: typing.Type, tearer: Tearer, namingPolicy: typing.Dict[str, NamingRule], builder: typing.Type["BuiltPackage"], packageManager: IPackageManager, archTransformer: typing.Callable, repoClass: typing.Type["Repo"], decodeAnotherPackageRefIntoStr: typing.Callable) -> None:
		self.name = name
		self.dirsConventions = dirsConventions
		self.tearer = tearer
		self.namingPolicy = namingPolicy
		self.builder = builder
		self.packageManager = packageManager
		self.archTransformer = archTransformer
		self.repoClass = repoClass
		self.decodeAnotherPackageRefIntoStr_ = decodeAnotherPackageRefIntoStr

	def decodeAnotherPackageRefIntoStr(self, ref: VersionedPackageRef) -> str:
		return self.decodeAnotherPackageRefIntoStr_(self, ref)

	def decodeRef(self, ref: PackageRef) -> VersionedPackageRef:
		if isinstance(ref, VersionedPackageRef):
			pass
		elif isinstance(ref, BasePackageRef):
			return ref
		else:
			raise ValueError(repr(ref.__class__) + " is not a valid input type")
		if ref.group:
			res = ref.clone()
			res.name = self.namingPolicy[ref.group].gen(ref)
			res.group = None
			return res
		else:
			return ref

	def toPackageRefWithGroupResolved(self, pkgRef: typing.Union[VersionedPackageRef, str]) -> VersionedPackageRef:
		if isinstance(pkgRef, str):
			name = pkgRef
			resRef = PackageRef(name)
		elif isinstance(pkgRef, VersionedPackageRef):
			if pkgRef.group is not None:
				#raise ValueError("pkgRef.group must be undetermined! It is what we want to detect!")
				return pkgRef.clone()
			else:
				name = pkgRef.name
				resRef = pkgRef.clone()
		elif isinstance(pkgRef, BasePackageRef):
			name = pkgRef.name
			resRef = PackageRef(pkgRef.name, arch=pkgRef.arch)
		else:
			raise ValueError("pkgRef must be either a `str` or a `VersionedPackageRef`", pkgRef, pkgRef.__class__)

		for groupId, namingRule in self.namingPolicy.items():
			normalizedName = namingRule.match(name)
			#print(groupId, namingRule, normalizedName)
			if normalizedName:
				resRef.name = normalizedName
				resRef.group = groupId
				return resRef

	def __repr__(self) -> str:
		return self.__class__.__name__ + "<" + self.name + ">"
