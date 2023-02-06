__all__ = ("DummyBS", "Dummy")
import typing
from pathlib import Path

from ..core.BuildSystem import BuildSystem
from ..core.Package import PackageInstalledFiles, VersionedPackageRef


class DummyBS(BuildSystem):
	essentialFiles = ()

	@classmethod
	def __call__(cls, sourceDir: Path, ref: VersionedPackageRef, packagesRootsDir: Path, gnuDirs, buildOptions: typing.Optional[typing.Dict[str, bool]] = None, firejailCfg: typing.List[typing.Any] = ()):
		res = PackageInstalledFiles(ref, sourceDir, needsTearing=True)
		res.registerPath(res.root)
		return (res,)


Dummy = DummyBS()
