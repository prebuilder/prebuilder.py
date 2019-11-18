import typing
from pathlib import Path, PurePath
import re
from collections import defaultdict
from glob import glob

from pantarei import chosenProgressReporter

from fsutilz import isNestedIn, nestPath, symlink, isGlobPattern, relativePath
from .Package import VersionedPackageRef, PackageInstalledFiles, getPackageInstalledFilesFromRefAndParent
from FHS import FHS
from ..styles import styles
from ..actions import RipAction, SymlinkAction
from ..utils.VPath import VPath
from .Action import IAction, IFSAction


class Classifier:
	__slots__ = ("paths", "matchers", "isDir", "debug")

	def __init__(self, paths: typing.Iterable[Path], matchers: typing.Iterable[str] = None, isDir: bool = False, debug: bool = False) -> None:
		if isinstance(paths, Path):
			paths = (paths,)

		if isinstance(matchers, (str,)):
			matchers = (matchers,)

		self.paths = paths
		self.isDir = isDir
		self.debug = debug

		if matchers is None:
			self.matchers = matchers
		else:
			self.matchers = []
			for m in matchers:
				if isinstance(m, str):
					m = re.compile(m)
				self.matchers.append(m)

	def __call__(self, fileName: Path) -> bool:
		filesUnmatched = []
		filesOwn = []
		for p in self.paths:
			if isNestedIn(p, fileName):
				if self.debug:
					print("self.isDir == fileName.is_dir()", self.isDir == fileName.is_dir(), "self.isDir", self.isDir, "fileName.is_dir()", fileName.is_dir(), fileName)

				if not self.isDir:
					if not fileName.is_dir():
						name2Match = fileName.name
					else:
						continue
				else:
					p = relativePath(fileName, p)
					name2Match = p.parts[0]
				
				if self.matchers:
					for m in self.matchers:
						if self.debug:
							print("("+repr(m)+").search("+repr(name2Match)+")", m.search(name2Match))
						if m.search(name2Match):
							return True
				else:
					return True
		return False

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.paths) + ", " + repr(self.matchers) + ")"


class Splitter:
	__slots__ = ("classifiers", "name")

	def __init__(self, classifiers: typing.Iterable[Classifier], name: str) -> None:
		if isinstance(classifiers, Classifier):
			classifiers = (classifiers,)

		self.classifiers = []
		for c in classifiers:
			if isinstance(c, Path):
				c = Classifier(c)
			self.classifiers.append(c)
		self.name = name

	def __call__(self, files):
		filesMatched = []
		dirsDirectlyMatched = []
		for c in self.classifiers:
			filesUnmatched = []
			for f in files:
				#print("c(f)", c(f))
				if c(f):
					filesMatched.append(f)
					if f.is_dir():
						dirsDirectlyMatched.append(f)
				else:
					inMatchedDirs = False
					for d in dirsDirectlyMatched:
						if isNestedIn(d, f):
							inMatchedDirs = True
							break
					if inMatchedDirs:
						filesMatched.append(f)
					else:
						filesUnmatched.append(f)

			files = filesUnmatched
		return filesMatched, filesUnmatched

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.classifiers) + ", " + repr(self.name) + ")"


class TearingSpec:
	__slots__ = ("ref", "actions")

	def __init__(self, ref: VersionedPackageRef, actions: typing.Iterator[IAction] = None):
		self.ref = ref
		if actions is None:
			actions = []
		self.actions = actions

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.ref._metadataInnerReprStr() + ", " + repr(self.actions) + ")"

	def __call__(self, pkg: PackageInstalledFiles, root: typing.Optional[Path] = None):
		if root is None:
			root = pkg.root / "subpackages"
		childPkg = getPackageInstalledFilesFromRefAndParent(self.ref, root)

		with chosenProgressReporter(len(self.actions), "Doing actions for " + str(childPkg.ref)) as pb:
			for a in self.actions:
				#pb.print(str(a))
				a(pkg, childPkg)
				pb.report(str(a))
		assert childPkg.filesTracker.filesAndSymlinks
		return childPkg


class Tearer:
	def __init__(self, splitters: typing.Iterable[Splitter]) -> None:
		self.splitters = splitters

	def __call__(self, pkg):
		root = pkg.root
		pkgRef = pkg.ref

		files = [nestPath(FHS, f) for f in pkg.filesTracker.filesAndSymlinks]
		#print("files", files)
		splittedPackages = {}

		for s in self.splitters:
			filesMatched, files = s(files)
			if filesMatched:
				#print("Files", filesMatched, "matched for splitter", s)

				pkgRef = pkgRef.clone()
				pkgRef.group = s.name
				if pkgRef in splittedPackages:
					childTearingSpec = splittedPackages[pkgRef]
				else:
					splittedPackages[pkgRef] = childTearingSpec = TearingSpec(pkgRef)

				for f in filesMatched:
					childTearingSpec.actions.append(RipAction(VPath(f)))

		files = [f for f in files if not f.is_dir()]
		if files:
			raise Exception("Non-matched files", repr(files))

		#print(styles.entity("torn") + " " + styles.varContent(splittedPackages))
		return splittedPackages
