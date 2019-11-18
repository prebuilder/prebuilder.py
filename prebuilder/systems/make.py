__all__ = ("MakeBS", "Make")
import typing
import types
import sys
from pathlib import Path
import os

import sh
import sh.contrib

from ..tools.make import make
from ..tools import getCfj
from ..core.Package import PackageInstalledFiles, VersionedPackageRef, getPackageInstalledFilesFromRefAndParent
from ..core.BuildSystem import BuildSystem
from ..styles import styles
from .. import globalPrefs


class MakeBS(BuildSystem):
	essentialFiles = ("Makefile",)

	@classmethod
	def __call__(cls, sourceDir, ref: VersionedPackageRef, packagesRootsDir: Path, gnuDirs, buildOptions=None, useKati: bool = False, configureScript: typing.Union[str, Path] = "./configure", configureInterpreter: typing.Optional[typing.Union[str, Path]] = None, installRule: typing.Union[str, typing.Callable[[Path, typing.Optional[Path], PackageInstalledFiles, Path], None]] = "install", makeArgs: typing.Iterable[typing.Union[str]] = (), firejailCfg: typing.Iterable[Path]=()):

		additionalOptions = []
		if buildOptions:
			buildOptions = type(buildOptions)(buildOptions)
		else:
			buildOptions = {}
		
		buildOptions.update(gnuDirs.toGnuArgs())

		for k, v in buildOptions.items():
			if isinstance(v, bool):
				additionalOptions.append("--" + ("" if v else "no-") + k)
			else:
				additionalOptions.extend(("--" + k + "=" + str(v),))

		if configureScript and globalPrefs.configure:
			print(styles.operationName("Configuring") + "...")
			if configureInterpreter:
				interpreter = getCfj(sourceDir, **firejailCfg).bake(configureInterpreter)
				configure = interpreter.bake(configureScript)
			else:
				if isinstance(configureScript, str):
					configureScript = Path(sourceDir / configureScript)
				configureScript = configureScript.absolute()
				configure = sh.Command(configureScript)
			configure(additionalOptions, _cwd=sourceDir)

		print(styles.operationName("Building") + "...")
		if globalPrefs.build:
			make(*makeArgs, useKati=useKati, _cwd=sourceDir, firejailCfg=firejailCfg)

		pkg = getPackageInstalledFilesFromRefAndParent(ref, packagesRootsDir, needsTearing=True)

		if globalPrefs.install:
			print(styles.operationName("Installing") + "...")
			if isinstance(installRule, str):
				installEnv = os.environ.copy()
				installEnv["DESTDIR"] = str(pkg.root)
				make(installRule, _cwd=sourceDir, _env=installEnv, firejailCfg=firejailCfg)
			elif callable(installRule):
				installRule(sourceDir, None, pkg, gnuDirs)
			else:
				raise NotImplementedError("Please provide the installation instructions!")

		pkg.registerPath(pkg.root)

		return (pkg,)


Make = MakeBS()
