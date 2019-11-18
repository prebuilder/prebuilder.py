__all__ = ("BuildSystem", "detectBuildSystem")

import typing
from pathlib import Path

buildSystemsRegistry = []


class BuildSystemMeta(type):
	def __new__(cls, className, parents, attrs, *args, **kwargs):
		global buildSystemsRegistry
		res = super().__new__(cls, className, parents, attrs, *args, **kwargs)

		attrsNew = type(attrs)()
		if "essentialFiles" in attrs:
			esF = attrs["essentialFiles"]
			if esF:
				buildSystemsRegistry.append((esF, res))
		return res


class BuildSystem(metaclass=BuildSystemMeta):
	essentialFiles = None  # used for build system autodiscovery

	def __init__(self):
		pass

	@classmethod
	def __call__(cls, sourceDir, name: str, packagesRootsDir, gnuDirs, buildOptions=None, firejailCfg: typing.Mapping[str, typing.Any] = None):
		pass


def detectBuildSystem(srcDir: Path):
	for esFiles, bs in buildSystemsRegistry:
		for esF in esFiles:
			if (srcDir / esF).exists():
				return bs
