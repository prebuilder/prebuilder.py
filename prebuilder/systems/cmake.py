__all__ = ("CMakeBS", "CMake")
import typing
import sys
from pathlib import Path
import re
import shlex
from pprint import pprint
import os

from collections import OrderedDict, defaultdict

from .ninja import NinjaBS
from ..core.Package import VersionedPackageRef, Package, PackageMetadata, PackageInstalledFiles, getPackageInstalledFilesFromRefAndParent, PackagingSpec, AssociateTearingSpecAndMetadata
from ..core.BuildSystem import BuildSystem
from ..core.BuiltPackage import BuiltPackage

from ..tools import getCfj

from ..importers.cpack import cpackInterpreter
from .. import globalPrefs
from ..styles import styles


class CMakeBS(NinjaBS):
	essentialFiles = ("CMakeLists.txt",)
	
	@classmethod
	def ripPackageWithCMake(cls, pkgInst, buildDir, firejailCfg, installEnv, componentCMakeId):
		installEnv["DESTDIR"] = str(pkgInst.root)
		firejailCfg1 = type(firejailCfg)(firejailCfg)
		firejailCfg1["apparmor"] = True
		firejailCfg1["paths"].extend((pkgInst.root, buildDir))
		args = ["-DCOMPONENT=" + shlex.quote(str(componentCMakeId)), "-P", "cmake_install.cmake"]
		
		getCfj(_cwd=buildDir, **firejailCfg).cmake(*args, _cwd=buildDir, _env=installEnv)  # IMPORTANT, only relative path to cmake_install.cmake here! Otherwise doesn't work!
		pkgInst.registerPath(pkgInst.root)

	@classmethod
	def __call__(cls, sourceDir: Path, ref: VersionedPackageRef, packagesRootsDir: Path, gnuDirs, buildOptions: typing.Optional[typing.Dict[str, bool]] = None, firejailCfg: typing.List[typing.Any] = (), ripWithCMake: bool = True) -> typing.Iterator[Package]:
		
		cmakeCLIOptions = ["-GNinja", "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DCMAKE_VERBOSE_MAKEFILE=1"]
		buildOptions = type(buildOptions)(buildOptions)
		
		for k, v in gnuDirs.toGnuArgs().items():
			buildOptions["CMAKE_INSTALL_" + k.upper()] = v

		if buildOptions:
			for k, v in buildOptions.items():
				if isinstance(v, bool):
					v = "ON" if v else "OFF"
				cmakeCLIOptions.append("=".join(("-D" + k, str(v))))

		buildDir = sourceDir / "build"
		buildDir.mkdir(exist_ok=True)
		
		firejailCfgConfigure = type(firejailCfg)(firejailCfg)
		firejailCfgConfigure["paths"].extend((sourceDir, buildDir))
		firejailCfgConfigure["apparmor"] = False
		cfjBuild = getCfj(_cwd=buildDir, **firejailCfgConfigure)
		cmake = cfjBuild.cmake

		ninjaPackagingRes = None
		try:
			if globalPrefs.configure:
				print(styles.operationName("Configuring") + "...")
				print(cmakeCLIOptions)
				cmake(sourceDir, cmakeCLIOptions, _cwd=buildDir)

			super().__call__(buildDir, ref=ref, packagesRootsDir=packagesRootsDir, gnuDirs=gnuDirs, buildOptions={}, installRule=None, firejailCfg=firejailCfgConfigure)

			
			print(styles.operationName("Packaging") + "...")

			installEnv = os.environ.copy()
			tearingSpecs = OrderedDict()
			
			cpackComponents = cpackInterpreter(buildDir)
			
			print("cpackComponents", cpackComponents)
			
			def components2Packages(componentz):
				for cmakeComponentPackageSpec in componentz:
					pkgRef = VersionedPackageRef(cmakeComponentPackageSpec.dic["name"], version=cmakeComponentPackageSpec.dic["version"])
					del cmakeComponentPackageSpec.dic["name"], cmakeComponentPackageSpec.dic["version"]

					metadata = PackageMetadata(pkgRef, **cmakeComponentPackageSpec.dic, packagerSpecific=cmakeComponentPackageSpec.packagerSpecific)

					if ripWithCMake:
						pkgInst = getPackageInstalledFilesFromRefAndParent(pkgRef, packagesRootsDir)
						if globalPrefs.install:
							cls.ripPackageWithCMake(pkgInst, buildDir, firejailCfg, installEnv, cmakeComponentPackageSpec.id)
						yield (metadata, pkgInst)
					else:
						raise NotImplementedError()
			
			if not len(cpackComponents.sub):
				metadata, inst = next(components2Packages((cpackComponents.main,)))
				inst.needsTearing = True
				yield AssociateTearingSpecAndMetadata(inst, PackagingSpec(metadata))
			else:
				for metadata, inst in components2Packages(cpackComponents.sub.values()):
					yield Package(metadata, inst)

			if not ripWithCMake:
				return PackagingSpec()  # __init__(self, commonMetadata, tearingSpecs: typing.Mapping[typing.Union[VersionedPackageRef, PackageMetadata], "TearingSpec"] = None)

		except Exception as ex:
			if hasattr(ex, "stdout") and hasattr(ex, "stderr"):
				print(ex.stdout.decode("utf-8"))
				print(ex.stderr.decode("utf-8"))
			raise


CMake = CMakeBS()
