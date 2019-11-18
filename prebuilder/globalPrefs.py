__all__ = ()

from .core.enums import CleanBuild

"""Global prefs for debugging purposes. Allow to skip build and installation stages"""

shallowFetch = True  # True: shallow fetches without tags, False: full fetches + tags


clean = CleanBuild.all  # bit mask
#clean = CleanBuild.repos | CleanBuild.packagesRoots | CleanBuild.sources # bit mask
clean = CleanBuild.repos | CleanBuild.packagesRoots # bit mask
fetch = True
patch = True
reconf = True
configure = True
build = True
install = True
tear = True
buildPackages = True
signPackages = True
createRepos = True

if not (fetch and reconf and configure and build and install and tear and buildPackages and signPackages and createRepos and (clean != CleanBuild.all)):
	from warnings import warn

	warn("Some steps are disabled for debug purposes! This configuration is not intended for production use!")
