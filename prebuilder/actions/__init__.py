import typing
from pathlib import Path, PurePath
from fsutilz import symlink, relativePath
from ..core.Package import VersionedPackageRef, PackageInstalledFiles
from ..core.Action import IAction, IFSAction
from warnings import warn

class RipAction(IFSAction):
	__slots__ = ("dst",)

	def __init__(self, src, dst=None, globAllowed: bool = False, ignoreMissing: bool = False):
		super().__init__(src, globAllowed=globAllowed, ignoreMissing=ignoreMissing)
		self.dst = dst

	def _internal(self, srcPath, srcRelative, pkg, childPkg):
		if self.dst is not None:
			dst = self.dst
		else:
			dst = srcRelative
		
		if self.ignoreMissing:
			if not srcPath.exists():
				warn("Missing file/dir " + repr(srcPath) + " is ignored by action " + repr(self))
				return
		
		intoDir = (dst.is_dir() and not srcPath.is_dir())
		
		if intoDir:
			dstPath = childPkg.nest(dst)
			dstPath.mkdir(parents=True, exist_ok=True)
			dstFilePathStr = relativePath(dstPath / srcPath.name, childPkg.root)
			childPkg.copy(srcPath, dstFilePathStr, {dstFilePathStr : pkg.filesTracker.hashsums[srcRelative]})
		else:
			childPkg.copy(srcPath, dst, {dst : pkg.filesTracker.hashsums[srcRelative]})

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.src) + (", " + repr(self.dst) if self.dst else "") + ")"
	
	def __str__(self):
		return str(self.src) + " 🚛 " + (str(self.dst) if self.dst else "")


class SymlinkAction(IFSAction):
	__slots__ = ("dst", "relativeTo")

	def __init__(self, src: Path, dst, relativeTo=None, globAllowed: bool = False):
		super().__init__(src, globAllowed=globAllowed)
		self.dst = dst
		self.relativeTo = relativeTo

	def _internal(self, srcPath, srcRelative, pkg, childPkg):
		if self.dst is not None:
			dst = self.dst
		else:
			dst = srcRelative
		
		intoDir = (dst.is_dir() and not srcPath.is_dir())
		
		rt = childPkg.nest(self.relativeTo) if self.relativeTo is not None else None
		
		if intoDir:
			dstPath = childPkg.nest(dst)
			dstPath.mkdir(parents=True, exist_ok=True)
			dstFilePathStr = relativePath(dstPath / srcPath.name, childPkg.root)
			childPkg.symlink(childPkg.nest(srcRelative), dstFilePathStr, rt)
		else:
			childPkg.symlink(childPkg.nest(srcRelative), dst, rt)

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.src) + ", " + repr(self.dst) + ")"

	def __str__(self):
		return str(self.src) + " ⤤ " + (str(self.dst) if self.dst else "")
