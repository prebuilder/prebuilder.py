from . import getCfj


def dpkgDebBuild(*files) -> None:
	return getCfj(paths=files).fakeroot.bake("dpkg-deb", "-Sextreme", b=True, _fg=True)(files)
