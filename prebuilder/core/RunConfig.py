import typing
from pathlib import Path, PurePath
import re
from collections import defaultdict
from fsutilz import isNestedIn, nestPath, symlink, isGlobPattern

from fetchers.FetchConfig import FetchConfig

from .Person import Maintainer
from .. import globalPrefs
from shutil import rmtree

from .enums import CleanBuild


class RunConfig:
	"""Encapsulates the info used to run the stuff"""

	__slots__ = ("sourcesDir", "packagesRootsDir", "builtDir", "repoDir", "maintainer", "cleanBuild", "fetchConfig")

	def doCleanup(self):
		if (self.cleanBuild & CleanBuild.sources) == CleanBuild.sources and self.sourcesDir.exists():
			rmtree(self.sourcesDir)
		if (self.cleanBuild & CleanBuild.repos) == CleanBuild.repos and self.repoDir.exists():
			rmtree(self.repoDir)
		if (self.cleanBuild & CleanBuild.builtTmpDir) == CleanBuild.builtTmpDir and self.builtDir.exists():
			rmtree(self.builtDir)
		if (self.cleanBuild & CleanBuild.downloadsTmpDir) == CleanBuild.downloadsTmpDir:
			self.fetchConfig.doCleanup()
		if (self.cleanBuild & CleanBuild.packagesRoots) == CleanBuild.packagesRoots and self.packagesRootsDir.exists():
			rmtree(self.packagesRootsDir)

	def doPreparations(self):
		if self.cleanBuild:
			self.doCleanup()

		self.sourcesDir.mkdir(exist_ok=True, parents=True)
		self.fetchConfig.doPreparations()
		self.builtDir.mkdir(exist_ok=True, parents=True)
		self.packagesRootsDir.mkdir(exist_ok=True, parents=True)

	def __init__(self, sourcesDir: typing.Optional[Path] = None, packagesRootsDir: typing.Optional[Path] = None, builtDir: typing.Optional[Path] = None, fetchConfig: typing.Optional[Path] = None, repoDir: typing.Optional[Path] = None, maintainer: typing.Optional[Maintainer] = None, cleanBuild: CleanBuild = CleanBuild.all):
		self.cleanBuild = cleanBuild & globalPrefs.clean
		thisDir = Path(".").absolute()

		if sourcesDir is None:
			sourcesDir = Path(thisDir / "sources").absolute()

		if packagesRootsDir is None:
			packagesRootsDir = thisDir / "packagesRoots"

		if fetchConfig is None:
			fetchConfig = FetchConfig(downloadsTmp=thisDir / "downloads")

		if builtDir is None:
			builtDir = thisDir / "packages"

		if repoDir is None:
			repoDir = thisDir / "public" / "repo"

		if maintainer is None:
			maintainer = Maintainer()

		self.sourcesDir = sourcesDir
		self.packagesRootsDir = packagesRootsDir
		self.fetchConfig = fetchConfig
		self.builtDir = builtDir
		self.repoDir = repoDir
		self.maintainer = maintainer
		self.doPreparations()
