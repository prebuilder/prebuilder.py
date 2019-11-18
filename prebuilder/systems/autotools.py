__all__ = ("AutoToolsBS", "AutoTools")
from .make import MakeBS
from ..styles import styles
from ..tools import getCfj
from .. import globalPrefs
from ..utils.ReprMixin import ReprMixin


class AutoToolsBS(MakeBS):
	essentialFiles = ("configure.ac", "Makefile.am")

	@classmethod
	def __call__(cls, sourceDir, ref, packagesRootsDir, gnuDirs, buildOptions=None, firejailCfg=None, useKati: bool = False, **kwargs):
		print(styles.operationName("Generating") + " " + styles.entity("configure script") + "...")
		
		firejailCfg1 = type(firejailCfg)(firejailCfg)
		firejailCfg1["paths"].append(sourceDir)
		if globalPrefs.reconf:
			getCfj(**firejailCfg1).autoreconf(i=True, _cwd=sourceDir)

		firejailCfg1["apparmor"] = False
		
		return super().__call__(sourceDir, ref, packagesRootsDir, gnuDirs=gnuDirs, buildOptions=buildOptions, useKati=useKati, configureScript=(sourceDir / "configure"), firejailCfg=firejailCfg1, **kwargs)


AutoTools = AutoToolsBS()
