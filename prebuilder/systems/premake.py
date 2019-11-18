from .make import *
from ..styles import styles
from ..tools import getCfj
from .. import globalPrefs


class PremakeBS(MakeBS):
	version = None

	@classmethod
	def __call__(cls, sourceDir, name, packagesRootsDir, gnuDirs, buildOptions=None, apparmor: bool=True, firejailCfg=(), useKati: bool = True, outOfSourceBuildOption:str = None, **kwargs):
		if buildOptions is None:
			buildOptions = {}
		if outOfSourceBuildOption:
			buildDir = sourceDir / "build"
			buildDir.mkdir(exist_ok=True)
			buildOptions[outOfSourceBuildOption] = buildDir
			if "installRule" in kwargs:
				if callable(kwargs["installRule"]):
					kwargs = type(kwargs)(kwargs)
					installRuleBackup = kwargs["installRule"]
					def installRule(sourceDir, buildDirNone, pkg, prefix):
						return installRuleBackup(sourceDir, buildDir, pkg, prefix)
					kwargs["installRule"] = installRule
		else:
			buildDir = sourceDir

		if globalPrefs.configure:
			print(styles.operationName("Configuring") + " " + styles.entity("makefile") + "...")
			firejailCfg1 = type(firejailCfg)(firejailCfg)
			firejailCfg1["apparmor"] = True
			getattr(getCfj(sourceDir, buildDir, _cwd=sourceDir, **firejailCfg1), "premake" + str(self.__class__.version)).bake(**buildOptions)(self.__class__.generatorName)

		yield from super().__call__(buildDir, name, packagesRootsDir, gnuDirs=gnuDirs, useKati=useKati, apparmor=apparmor, firejailCfg=firejailCfg, **kwargs)


class Premake5BS(PremakeBS):
	version = 5
	generatorName = "gmake2"
	essentialFiles = ("premake5.lua",)


Premake5 = Premake5BS()


class Premake4BS(PremakeBS):
	version = 4
	generatorName = "gmake"
	essentialFiles = ("premake4.lua",)


Premake4 = Premake4BS()
