import typing
import sh
from pathlib import Path
import os
from collections import OrderedDict
from datetime import datetime, timedelta

from pantarei import chosenProgressReporter

from ...styles import styles
from ...core.Package import Package
from ...core.Repo import IRepo
from ...buildPipeline import DistroStream
from .BuiltPackage import DebBuiltPackage
from ...distros.debian.releases import knownReleases
from ...tools.reprepro import getRepreproCmds
from ...core.RunConfig import RunConfig

from .utils import createConfigFromDict
from .releases import DebianRelease

def createDistributionText(descr: str, release: DebianRelease, components: typing.Iterable[str] = ("contrib", "non-free"), archs: typing.Iterable[str] = ("amd64",), signatureKey: str = "default", compressions: typing.Iterable[str] = ("xz",), validForDays: int = None, notAutomatic: bool = True, butAutomaticUpgrades: bool=True) -> str:
	d = OrderedDict()
	d["Description"] = descr
	d["Origin"] = release.origin
	d["Suite"] = release.suite
	d["Codename"] = release.codenames[0]
	d["Version"] = release.version

	d["Architectures"] = " ".join(set(archs) - {"all", "any"})
	d["Components"] = " ".join(components)
	d["UDebComponents"] = d["Components"]

	compressions = " ".join("." + c for c in compressions)

	d["DebIndices"] = "Packages Release " + compressions
	d["DscIndices"] = "Sources Release " + compressions
	d["Contents"] = compressions
	d["SignWith"] = signatureKey
	if validForDays is not None:
		d["ValidFor"] = str(validForDays) + "d"
	if notAutomatic:
		d["NotAutomatic"] = "yes"
		if butAutomaticUpgrades:
			d["ButAutomaticUpgrades"] = "yes"
		else:
			d["ButAutomaticUpgrades"] = "no"
	return createConfigFromDict(d)


def createDistributionsText(descr: str, releases: typing.List[DebianRelease], components: typing.Iterable[str] = ("contrib", "non-free"), archs: typing.Iterable[str] = ("amd64",), signatureKey: str = "default", compressions: typing.Iterable[str] = ("xz",)) -> str:
	return (os.linesep * 2).join(createDistributionText(descr, release=r, components=components, archs=archs, signatureKey=signatureKey, compressions=compressions) for r in releases)


AddableT = typing.Union[DistroStream, DebBuiltPackage, Path]
AddableT = typing.Union[AddableT, typing.Iterable[AddableT]]


class DebRepo(IRepo):
	__slots__ = ("cfg", "distrsDict", "packages2add")
	kind = "deb"

	def __init__(self, cfg: RunConfig, descr: str, releases: timedelta = timedelta(3 * 365), **kwargs) -> None:
		self.cfg = cfg
		self.distrsDict = dict(**kwargs)
		self.distrsDict["descr"] = descr

		releases_ = []
		if releases is None:
			for distroReleases in knownReleases.values():
				releases_ += distroReleases
		elif isinstance(releases, int):
			for distroReleases in knownReleases.values():
				releases_ += distroReleases[:releases]
		elif isinstance(releases, timedelta):
			now = datetime.now()
			for distroReleases in knownReleases.values():
				for r in distroReleases:
					if r.time is None or now - r.time < releases:
						releases_.append(r)
		else:
			releases_ = releases
		releases = releases_

		self.distrsDict["releases"] = releases
		#print(releases, self.releases)

		self.packages2add = None

	@property
	def root(self) -> Path:
		return self.cfg.repoDir

	@property
	def archs(self):
		return self.distrsDict["archs"]

	@archs.setter
	def archs(self, v):
		self.distrsDict["archs"] = v

	@property
	def releases(self):
		return self.distrsDict["releases"]

	@releases.setter
	def releases(self, v):
		self.distrsDict["releases"] = v

	@property
	def mainRelease(self):
		#print(self.releases)
		return self.releases[-1]

	@property
	def suite(self):
		return self.mainRelease.suite

	@property
	def codename(self):
		return self.mainRelease.codename

	@property
	def conf(self) -> Path:
		rootDir = self.root / "conf"
		rootDir.mkdir(parents=True, exist_ok=True)
		return rootDir

	def createDistributionsFile(self) -> None:
		ctrlF = self.conf / "distributions"
		ctrlF.write_text(createDistributionsText(**self.distrsDict))

	def __enter__(self) -> "DebRepo":
		self.packages2add = []
		if "archs" not in self.distrsDict:
			self.distrsDict["archs"] = set()
		else:
			self.distrsDict["archs"] = set(self.distrsDict["archs"])

		return self

	def __iadd__(self, pkg: AddableT) -> "DebRepo":
		if hasattr(pkg, "__iter__"):
			for pkg in pkg:
				self += pkg
		else:
			#print("__iadd__ pkg", pkg)
			self.packages2add.append(pkg)
			if isinstance(pkg, DebBuiltPackage):
				if isinstance(pkg.package, Package):
					self.archs |= {pkg.package.ref.arch}
		return self

	def generateRepo(self) -> None:
		oldPath = Path.cwd()
		oldDescr = os.open(oldPath, os.O_RDONLY)
		rootDescr = None
		#try:
		print("self.packages2add", self.packages2add)
		rootDescr = os.open(self.root, os.O_RDONLY)
		os.fchdir(rootDescr)

		packagesPaths = []
		for pkg in self.packages2add:
			if isinstance(pkg, Path):
				pkgPath = pkg
			else:
				pkgPath = pkg.builtPath
			packagesPaths.append(pkgPath)

		repreproCmds = getRepreproCmds(self.root.parent, *packagesPaths, _cwd=self.root)
		repreproCmds["export"]()
		repreproCmds["createSymlinks"]()

		with chosenProgressReporter(len(packagesPaths), "Publishing as a deb repo") as pb:
			for pkgPath in packagesPaths:
				pb.print(styles.operationName("adding") + " " + styles.varContent(str(pkgPath)))
				for r in self.releases:
					for cn in r.codenames:
						repreproCmds["removePackage"](cn, pkgPath.stem)
						repreproCmds["includeDeb"](cn, pkgPath)
				pb.report(pkgPath)

		self.packages2add = []
		#except:
		#	raise
		#finally:
		if rootDescr is not None:
			os.close(rootDescr)
		os.fchdir(oldDescr)
		os.close(oldDescr)

	def __exit__(self, *args, **kwargs) -> None:
		self.createDistributionsFile()
		self.generateRepo()
