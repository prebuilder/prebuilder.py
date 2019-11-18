__all__ = ("NinjaBS", "Ninja")
import os
import sys
import types
import typing
from pathlib import Path

from .. import globalPrefs
from ..core.BuildSystem import BuildSystem
from ..core.Package import PackageInstalledFiles, VersionedPackageRef, getPackageInstalledFilesFromRefAndParent
from ..styles import styles
from ..tearers.FHSTearer import FHSTearer, Tearer
from ..tools.ninja import ninja


class NinjaBS(BuildSystem):
	essentialFiles = ("build.ninja",)

	@classmethod
	def __call__(cls, sourceDir, ref: VersionedPackageRef, packagesRootsDir, gnuDirs, buildOptions=None, installRule="install", firejailCfg=()):
		print(styles.operationName("Building") + " with " + styles.entity("ninja") + "...")

		buildEnv = os.environ.copy()
		buildEnv.update(buildOptions)
		if globalPrefs.build:
			ninja(_cwd=sourceDir, _env=buildEnv, firejailCfg=firejailCfg)

		if globalPrefs.install and installRule is not None:
			print(styles.operationName("Installing") + "...")
			pkg = getPackageInstalledFilesFromRefAndParent(ref, packagesRootsDir, needsTearing=True)
			if isinstance(installRule, str):
				installEnv = os.environ.copy()
				installEnv["DESTDIR"] = str(pkg.root)
				firejailCfgInstall = type(firejailCfg)(firejailCfg)
				firejailCfgInstall["paths"].append(installRule)
				ninja(_cwd=sourceDir, _env=installEnv, firejailCfg=firejailCfgInstall)
			elif callable(installRule):
				installRule(sourceDir, pkg, gnuDirs)
			else:
				raise NotImplementedError("Please provide the installation instructions!")

			pkg.registerPath(pkg.root)

			return (pkg,)
		else:
			return ()


Ninja = NinjaBS()
