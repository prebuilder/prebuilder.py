__all__ = ("MesonBS", "Meson")
import typing
import sys
from pathlib import Path
from argparse import Namespace
import json

from .ninja import NinjaBS
from ..core.Package import PackageInstalledFiles, VersionedPackageRef, getPackageInstalledFilesFromRefAndParent
from ..core.BuildSystem import BuildSystem
from ..styles import styles
from .. import globalPrefs

import mesonbuild
from mesonbuild.minstall import Installer
from mesonbuild.coredata import parse_cmd_line_options, get_cmd_line_file
from mesonbuild.msetup import MesonApp
from mesonbuild.environment import Environment
from mesonbuild.mesonmain import CommandLineParser

from warnings import warn


class OurPackagerInstaller(Installer):
	def __init__(self, package: PackageInstalledFiles, *args, **kwargs):
		self.package = package
		super().__init__(*args, **kwargs)

	def do_copyfile(self, from_file, to_file):
		#self.package.copy(from_file, to_file)
		super().do_copyfile(from_file, to_file)
		self.package.registerPath(Path(to_file))
		return True

	def install_targets(self, installData: "mesonbuild.backend.backends.InstallData"):
		#print(installData.__dict__)
		#installData.source_dir = Path(installData.source_dir).absolute()
		installData.build_dir = Path(installData.build_dir).absolute()
		installData.prefix = self.package.nest(installData.prefix)
		installData.fullprefix = str(self.package.nest(installData.fullprefix))

		for t in installData.targets:
			t.fname = str(installData.build_dir / t.fname)
			#print(self.package.root)
			t.install_name_mappings = {s: self.package.nest(d) for s, d in t.install_name_mappings.items()}
			#print(t.__dict__)
		return super().install_targets(installData)

	def install_data(self, d):
		print("install_data", d)
		return super().install_data(d)

	def install_man(self, d):
		print("install_man", d)
		return super().install_man(d)

	def install_headers(self, d):
		print("install_headers", d)
		return super().install_headers(d)


p = CommandLineParser()


class MesonBS(NinjaBS):
	essentialFiles = ("meson.build",)

	@classmethod
	def __call__(cls, sourceDir, ref: VersionedPackageRef, packagesRootsDir, gnuDirs, buildOptions=None, firejailCfg=None):
		warn("Meson builds are not yet properly sandboxed! `ninja` invocation is, but `meson` rules (essentially python code) aren't!")
		
		buildDir = sourceDir / "build"
		buildDir.mkdir(exist_ok=True)

		if globalPrefs.configure:
			print(styles.operationName("Configuring") + "...")
			
			mesonbuild.mesonlib.set_meson_command("meson")

			setupOpts = p.commands["setup"].parse_known_args([])[0]
			parse_cmd_line_options(setupOpts)

			setupOpts.builddir = buildDir
			setupOpts.sourcedir = sourceDir
			
			buildOptions = type(buildOptions)(buildOptions)
			
			gnuDirsArgs = gnuDirs.toGnuArgs()
			for k,v in gnuDirsArgs.items():
				setattr(setupOpts, k, v)
			
			setupOpts.wipe = setupOpts.reconfigure = Path(get_cmd_line_file(buildDir)).exists()

			if buildOptions:
				setupOpts.cmd_line_options.update({k: json.dumps(v) for k, v in buildOptions.items()})

			setupOpts.cmd_line_options.update({
				"backend": "ninja",  # we build with ninja, it is hardcoded lower
				"buildtype": "release",
				"optimization": "3",
				**{k: str(v) for k,v in gnuDirsArgs.items()}  # DON'T REMOVE!
			})

			#print(setupOpts)
			#print(setupOpts.cmd_line_options)

			m = MesonApp(setupOpts)
			m.generate()
		
		firejailCfg1 = type(firejailCfg)(firejailCfg)
		firejailCfg1["paths"].append(sourceDir)
		
		super().__call__(buildDir, ref=ref, packagesRootsDir=packagesRootsDir, gnuDirs=gnuDirs, buildOptions={}, installRule=None, firejailCfg=firejailCfg1)
		
		pkg = getPackageInstalledFilesFromRefAndParent(ref, packagesRootsDir)
		pkg.needsTearing = True
		if globalPrefs.install:
			print(styles.operationName("Installing") + "...")
			installOpts = p.commands["install"].parse_known_args([])[0]
			inst = OurPackagerInstaller(pkg, installOpts, sys.stdout)
			inst.do_install(buildDir / "meson-private" / "install.dat")
			pkg.registerPath(pkg.root)

		return (pkg,)


Meson = MesonBS()
