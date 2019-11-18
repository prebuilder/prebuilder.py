import typing
import os
from pathlib import Path

from elftools.elf.dynamic import DynamicSection
from elftools.elf.elffile import ELFFile
from elftools.common.exceptions import ELFError
from elftools.elf.enums import ENUM_DT_FLAGS_1

#from ELFMachine import ELFMachine

from ..tools.ldconfig import ldconfigCache

from . import Extractor, ExtractedInfo

from collections import defaultdict
from pathlib import PosixPath
from typing import Any, List, Optional, Tuple, Union
ldLibPaths = os.environ.get("LD_LIBRARY_PATH")
if ldLibPaths:
	ldLibPaths = [Path(p) for p in ldLibPaths.split(":")]

fallbackPaths = [Path("/lib"), Path("/usr/lib")]

bitnessMapping = {"ELFCLASS" + str(b): b for b in (32, 64)}


class _ELFDepsResolver:
	__slots__ = ("order", "ldconfigCache", "fallbackPaths", "debug")

	def __init__(self, order: typing.List[Any], ldconfig: typing.Optional[defaultdict], fallbackPaths: typing.Iterable[Path]) -> None:
		self.order = order
		self.ldconfigCache = ldconfigCache
		self.fallbackPaths = fallbackPaths
		self.debug = False

	def resolveFile(self, file: Path) -> typing.Optional[Path]:
		file = file.absolute().resolve()
		return file if file.is_file() else None

	def report(self, cand: Path, result: typing.Optional[Path]) -> None:
		if self.debug:
			print(cand, result)

	def __call__(self, d: str) -> typing.Optional[Path]:
		for p in self.order:
			cand = p / d
			r = self.resolveFile(cand)
			self.report(cand, r)
			if r:
				return r

		if self.ldconfigCache:  # You may want to rebuild ldconfig cache!!! (sudo ldconfig)
			if d in self.ldconfigCache:
				for f in ldconfigCache[d]:
					r = self.resolveFile(f)
					self.report(f, r)
					if r:
						return r

		if self.fallbackPaths:
			for p in self.fallbackPaths:
				cand = p / d
				r = self.resolveFile(cand)
				self.report(cand, r)
				if r:
					return r


class ELFDepsResolver(_ELFDepsResolver):
	__slots__ = ()

	def __init__(self, rpath: typing.Iterable[Any], runpath: typing.Iterable[Any], ldLibPaths: None, noDefLib: int) -> None:
		order = []
		if rpath and not DT_RUNPATH:
			order.extend([Path(p) for p in rpath])
		if ldLibPaths:
			order.extend(ldLibPaths)
		if runpath:
			order.extend([Path(p) for p in runpath])
		super().__init__(order, None if noDefLib else ldconfigCache, None if noDefLib else fallbackPaths)


class ELFExtractor(Extractor):
	def __call__(self, fp: Path) -> ExtractedInfo:
		res = ExtractedInfo()
		rpath = []
		runpath = []
		noDefLib = False
		try:
			with fp.open("rb") as f:
				e = ELFFile(f)
				res.arch = e.header.e_machine
				res.OSABI = e.header.e_ident.EI_OSABI
				res.bitness = bitnessMapping[e.header.e_ident.EI_CLASS]

				for s in e.iter_sections():
					if isinstance(s, DynamicSection):
						dt = s
						for t in dt.iter_tags():
							if t.entry.d_tag == "DT_NEEDED":
								res.deps.append(t.needed)
							elif t.entry.d_tag == "DT_RPATH":
								rpath.extend(t.rpath)
							elif t.entry.d_tag == "DT_RUNPATH":
								runpath.extend(t.runpath)
							elif t.entry.d_tag == "DT_FLAGS_1":
								noDefLib = t.entry.d_val & ENUM_DT_FLAGS_1["DF_1_NODEFLIB"]

			res.depsResolver = ELFDepsResolver(rpath, runpath, ldLibPaths, noDefLib)
			return res
		except ELFError as ex:  # file is not elf
			return None
