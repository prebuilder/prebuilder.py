import typing
from abc import abstractmethod, ABC
from glob import glob
from pathlib import Path, PurePath
from warnings import warn

from fsutilz import isGlobPattern, relativePath
from ..utils.VPath import VPath


class IAction(ABC):
	__slots__ = ()

	@abstractmethod
	def __call__(self, pkg, childPkg):
		raise NotImplementedError()


class IFSAction:
	__slots__ = ("globAllowed", "ignoreMissing", "src")

	def __init__(self, src: Path, globAllowed: bool = False, ignoreMissing: bool = False):
		self.globAllowed = globAllowed
		self.ignoreMissing = ignoreMissing
		self.src = src

	@abstractmethod
	def _internal(self, srcPath, srcRelative: str, pkg, childPkg):
		raise NotImplementedError()
	
	@property
	def isGlob(self):
		return isGlobPattern(self.src)

	def __call__(self, pkg, childPkg):
		srcPath = pkg.nest(self.src)
		if self.isGlob:
			if self.globAllowed:
				globExpr = str(srcPath)
				globbed = sorted(glob(globExpr))
				if not globbed:
					if not self.ignoreMissing:
						raise ValueError("Nothing has been globbed", globExpr, self)
					else:
						warn("Nothing has been globbed: " + repr(globExpr) + " " + repr(self))
						return
				for p in globbed:
					p = Path(p)
					self._internal(p, VPath(relativePath(p, pkg.root)), pkg, childPkg)  # nesting is checked in PackageInstallData module
			else:
				raise PermissionError("Glob expressions are not allowed for this action", self)
		else:
			self._internal(srcPath, self.src, pkg, childPkg)
