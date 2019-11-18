import typing
from collections import defaultdict, OrderedDict
from pathlib import Path

from os import readlink, linesep, fchdir
import os
import shutil
import warnings
import sh

from ...core.FilesTracker import FilesTracker, TextLinesHashesSerializer

#from fsutilz import *
from ...core.Package import VersionedPackageRef, PackageInstallSpec
from ...core.BuiltPackage import BuiltPackage
from ...core.Distro import Distro
from FHS import FHS

from .utils import createConfigFromDict, controlDictToArgs, serializePackagesRelationsField, debianPackageRelationKwargs
from ...tools.dpkgDeb import dpkgDebBuild
from ...tools.dpkgSig import dpkgSig
from ... import globalPrefs
from ...core.Person import Maintainer

class DebPackageInstallSpec(PackageInstallSpec):
	__slots__ = ("lintianOverrides",)

	def __init__(self):
		super().__init__()
		self.lintianOverrides = None


fsRoot = Path("/")


class DebHashesSerializer(TextLinesHashesSerializer):
	@classmethod
	def createSumsFileLines(cls, hashes: typing.Iterator[typing.Any]) -> typing.Iterator[str]:
		for k, v in hashes:
			yield v + "  " + str(k.relative_to(fsRoot)) + linesep

	@classmethod
	def createSumsMetadata(cls, filesTracker: FilesTracker, outputDir: Path) -> None:
		for hashName, hashData in filesTracker.createHashDataPerHashFunc():
			cls.createSumsFile(outputDir / (hashName + "sums"), hashData)


class DebBuiltPackage(BuiltPackage):
	__slots__ = ()
	packageExtension = "deb"
	hashesSerializer = DebHashesSerializer

	@property
	def debian(self) -> Path:
		debDir = self.package.installation.root / "DEBIAN"
		debDir.mkdir(parents=True, exist_ok=True)
		return debDir

	def createControl(self) -> None:
		(self.debian / "control").write_text(createControlText(self.distro, self.package.metadata.ref, **self.getMetadataDict()))

	def createSumsMetadata(self) -> None:
		self.__class__.hashesSerializer.createSumsMetadata(self.package.installation.filesTracker, self.debian)

	def sign(self) -> None:
		if globalPrefs.signPackages:
			dpkgSig(self.builtPath)

	def _build(self, builtPath: Path) -> None:
		self.createControl()
		if globalPrefs.buildPackages:
			assert isinstance(self.package.installation.root, Path)
			dpkgDebBuild(self.package.installation.root, builtPath)


def createControlText_interface(ref: VersionedPackageRef, homepage=None, depends=None, provides=None, section="misc", priority="optional", maintainer=None, size=None, descriptionShort="", descriptionLong="", additionalProps=None, recommends=None, suggests=None, replaces=None, conflicts=None, breaks=None, enhances=None):
	pass


createControlText_interface.__name__ = "createControlText"


def createControlText(distro: Distro, ref: VersionedPackageRef, homepage: typing.Optional[str] = None, section: str = "misc", priority: str = "optional", maintainer: typing.Optional[Maintainer] = None, size: None = None, descriptionShort: str = "", descriptionLong: str = "", additionalProps: None = None, **kwargs) -> str:
	d = OrderedDict()
	
	ref = distro.decodeRef(ref)
	
	assert ref.group is None, ref # Here only processed refs must reach
	d["Package"] = ref.name.lower()
	d["Version"] = str(ref.version)
	d["Architecture"] = ref.arch
	if maintainer:
		d["Maintainer"] = str(maintainer)
	if size:
		d["Installed-Size"] = size
	d["Section"] = section
	d["Priority"] = priority
	if homepage:
		d["Homepage"] = homepage

	for pkgRelKwargName in debianPackageRelationKwargs:
		if pkgRelKwargName in kwargs and kwargs[pkgRelKwargName]:
			d[pkgRelKwargName.title()] = serializePackagesRelationsField(distro, kwargs[pkgRelKwargName])

	d["Description"] = descriptionShort

	if descriptionLong:
		d["Description"] += linesep + "".join("\t" + l for l in descriptionLong.splitlines())

	if additionalProps:
		d.update(additionalProps)

	return createConfigFromDict(d)


#createControlText.__wraps__ = createControlText_interface
