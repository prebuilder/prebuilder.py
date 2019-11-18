prebuilder.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![GitLab Build Status](https://gitlab.com/KOLANICH/prebuilder.py/badges/master/pipeline.svg)](https://gitlab.com/prebuilder/prebuilder.py/-/jobs/artifacts/master/raw/dist/prebuilder.py-0.CI-py3-none-any.whl?job=build)
[![Coveralls Coverage](https://img.shields.io/coveralls/prebuilder/prebuilder.py.svg)](https://coveralls.io/r/prebuilder/prebuilder.py)
![GitLab Coverage](https://gitlab.com/KOLANICH/prebuilder.py/badges/master/coverage.svg)
[![Libraries.io Status](https://img.shields.io/librariesio/github/prebuilder/prebuilder.py.svg)](https://libraries.io/github/prebuilder/prebuilder.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://github.com/KOLANICH-tools/antiflash.py)

A deeply opinionated packages build system.

Why?
----

I am deeply dissatisfied with all the systems of building packages for distros.

* They are makefile-based and bash-based. These scripting languages are too limited to do something complex. Especially if the upstream is uncooperative.
* They often require a source archive. When it is not present they refuse to build.
* They are often buggy.
* They often have unneeded stages.

See [the manifesto](./Manifesto.md) for more info.


Requirements
------------
* Python 
    * [`sh`](https://github.com/amoffat/sh)[![PyPi Status](https://img.shields.io/pypi/v/sh.svg)](https://pypi.org/pypi/sh)[![Travis build](https://img.shields.io/travis/amoffat/sh/master.svg)](https://travis-ci.org/amoffat/sh)[![Coveralls Coverage](https://img.shields.io/coveralls/amoffat/sh.svg)](https://coveralls.io/r/amoffat/sh)[![Libraries.io Status](https://img.shields.io/librariesio/github/amoffat/sh.svg)](https://libraries.io/github/amoffat/sh)![Licence](https://img.shields.io/github/license/amoffat/sh.svg)
    * [`gpg`me](https://code.launchpad.net/pygpgme)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/python:gpg.svg)](https://packages.debian.org/stable/python:gpg)[![latest packaged version(s)](https://repology.org/badge/latest-versions/python:gpg.svg)](https://repology.org/metapackage/python:gpg/versions)[![GNU General Public License v3](https://www.gnu.org/graphics/gplv3-88x31.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)
    * [`patch`](https://github.com/techtonik/python-patch)[![PyPi Status](https://img.shields.io/pypi/v/patch.svg)](https://pypi.org/pypi/patch)[![Travis build](https://img.shields.io/travis/techtonik/python-patch/master.svg)](https://travis-ci.org/techtonik/python-patch)[![Libraries.io Status](https://img.shields.io/librariesio/github/techtonik/python-patchsvg)](https://libraries.io/github/techtonik/python-patch)![Licence](https://img.shields.io/github/license/techtonik/python-patch.svg)
    * [`AnyVer`](https://github.com/KOLANICH/AnyVer.py)[![PyPi Status](https://img.shields.io/pypi/v/AnyVer.svg)](https://pypi.org/pypi/AnyVer)![GitLab Build Status](https://gitlab.com/KOLANICH/AnyVer.py/badges/master/pipeline.svg)[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/AnyVer.py.svg)](https://coveralls.io/r/prebuilder/AnyVer.py)![GitLab Coverage](https://gitlab.com/KOLANICH/AnyVer.py/badges/master/coverage.svg)[![Libraries.io Status](https://img.shields.io/librariesio/github/prebuilder/AnyVer.py.svg)](https://libraries.io/github/prebuilder/AnyVer.py)
    * [`pyelftools`](https://github.com/eliben/pyelftools) ![Licence](https://img.shields.io/github/license/eliben/pyelftools.svg) [![PyPi Status](https://img.shields.io/pypi/v/pyelftools.svg)](https://pypi.python.org/pypi/pyelftools) [![TravisCI Build Status](https://travis-ci.org/eliben/pyelftools.svg?branch=master)](https://travis-ci.org/eliben/pyelftools) [![Libraries.io Status](https://img.shields.io/librariesio/github/eliben/pyelftools.svg)](https://libraries.io/github/eliben/pyelftools)
    * [`File2Package.py`](https://gitlab.com/File2Package.py/File2Package.py)[![PyPi Status](https://img.shields.io/pypi/v/File2Package.svg)](https://pypi.org/pypi/File2Package)![GitLab Build Status](https://gitlab.com/File2Package.py/File2Package.py/badges/master/pipeline.svg)[![Coveralls Coverage](https://img.shields.io/coveralls/File2Package/File2Package.py.svg)](https://coveralls.io/r/File2Package/File2Package.py)![GitLab Coverage](https://gitlab.com/File2Package.py/File2Package.py/badges/master/coverage.svg)[![Libraries.io Status](https://img.shields.io/librariesio/github/File2Package/File2Package.py.svg)](https://libraries.io/github/File2Package/File2Package.py)
        * [`File2Package.backend.dpkg`](https://gitlab.com/File2Package.py/File2Package.backend.dpkg)[![PyPi Status](https://img.shields.io/pypi/v/File2Package.backend.dpkg.svg)](https://pypi.org/pypi/File2Package.backend.dpkg)![GitLab Build Status](https://gitlab.com/File2Package.py/File2Package.backend.dpkg/badges/master/pipeline.svg)[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/File2Package.backend.dpkg.svg)](https://coveralls.io/r/File2PackageFile2Package.backend.dpkg)![GitLab Coverage](https://gitlab.com/File2Package.py/File2Package.backend.dpkg/badges/master/coverage.svg)[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/File2Package.backend.dpkg.svg)](https://libraries.io/github/File2Package/File2Package.backend.dpkg)
    * [`CMake.py`](https://gitlab.com/KOLANICH/CMake.py)[![PyPi Status](https://img.shields.io/pypi/v/CMake.py.svg)](https://pypi.org/pypi/AnyVer)![GitLab Build Status](https://gitlab.com/KOLANICH/CMake.py/badges/master/pipeline.svg)[![Coveralls Coverage](https://img.shields.io/coveralls/prebuilder/CMake.py.svg)](https://coveralls.io/r/prebuilder/CMake.py)![GitLab Coverage](https://gitlab.com/KOLANICH/CMake.py/badges/master/coverage.svg)[![Libraries.io Status](https://img.shields.io/librariesio/github/prebuilder/CMake.py.svg)](https://libraries.io/github/prebuilder/CMake.py)
    * [`GitPython`](https://github.com/gitpython-developers/GitPython)[![PyPi Status](https://img.shields.io/pypi/v/GitPython)](https://pypi.org/pypi/GitPython)[![Travis build](https://travis-ci.org/gitpython-developers/GitPython.svg)](https://travis-ci.org/gitpython-developers/GitPython)[![Appveyor build](https://ci.appveyor.com/api/projects/status/0f3pi3c00hajlrsd/branch/master?svg=true&passingText=windows%20OK&failingText=windows%20failed)](https://ci.appveyor.com/project/Byron/gitpython/branch/master)[![Code Climate](https://codeclimate.com/github/gitpython-developers/GitPython/badges/gpa.svg)](https://codeclimate.com/github/gitpython-developers/GitPython)[![codecov coverage](https://codecov.io/gh/gitpython-developers/GitPython/branch/master/graph/badge.svg)](https://codecov.io/gh/gitpython-developers/GitPython)![Libraries.io Status](https://img.shields.io/librariesio/github/gitpython-developers/GitPython.svg)](https://libraries.io/github/gitpython-developers/GitPython)![Licence](https://img.shields.io/github/license/gitpython-developers/GitPython.svg)

* build systems
    * [GNU `make`](https://github.com/mirror/make)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/make.svg)](https://packages.debian.org/stable/make)[![latest packaged version(s)](https://repology.org/badge/latest-versions/make.svg)](https://repology.org/metapackage/make/versions)[![GNU General Public License v3](https://www.gnu.org/graphics/gplv3-88x31.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)
    * [`ninja`](https://github.com/ninja-build/ninja)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/ninja.svg)](https://packages.debian.org/stable/ninja-build)[![latest packaged version(s)](https://repology.org/badge/latest-versions/ninja.svg)](https://repology.org/metapackage/ninja/versions)![Licence](https://img.shields.io/github/license/ninja-build/ninja.svg)
    * [`meson`](https://github.com/mesonbuild/meson)[![PyPI](https://img.shields.io/pypi/v/meson.svg)](https://pypi.python.org/pypi/meson)[![Travis](https://travis-ci.org/mesonbuild/meson.svg?branch=master)](https://travis-ci.org/mesonbuild/meson)[![Build Status](https://dev.azure.com/jussi0947/jussi/_apis/build/status/mesonbuild.meson)](https://dev.azure.com/jussi0947/jussi/_build/latest?definitionId=1)[![Codecov](https://codecov.io/gh/mesonbuild/meson/coverage.svg?branch=master)](https://codecov.io/gh/mesonbuild/meson/branch/master)[![Code Quality: Python](https://img.shields.io/lgtm/grade/python/g/mesonbuild/meson.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/mesonbuild/meson/context:python)[![Total Alerts](https://img.shields.io/lgtm/alerts/g/mesonbuild/meson.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/mesonbuild/meson/alerts)![Licence](https://img.shields.io/github/license/mesonbuild/meson.svg)
    * [`ckati`](https://github.com/google/kati)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/kati.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/kati.svg)](https://repology.org/metapackage/kati/versions)![Licence](https://img.shields.io/github/license/google/kati.svg)
    * [`CMake`](https://gitlab.kitware.com/cmake/cmake)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/cmake.svg)](https://packages.debian.org/stable/cmake)[![latest packaged version(s)](https://repology.org/badge/latest-versions/cmake.svg)](https://repology.org/metapackage/cmake/versions)[![BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt)
    * [autotools](https://github.com/autotools-mirror)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/autotools.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/autotools.svg)](https://repology.org/metapackage/autotools/versions)
        * [`automake`](https://github.com/autotools-mirror/automake)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/automake.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/automake.svg)](https://repology.org/metapackage/automake/versions)![Licence](https://img.shields.io/github/license/autotools-mirror/automake.svg)
        * [`autoconf`](https://github.com/autotools-mirror/autoconf)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/autoconf.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/autoconf.svg)](https://repology.org/metapackage/autoconf/versions)![Licence](https://img.shields.io/github/license/autotools-mirror/autoconf.svg)
        * [`m4`](https://github.com/autotools-mirror/m4)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/m4.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/m4.svg)](https://repology.org/metapackage/m4/versions)![Licence](https://www.gnu.org/graphics/gplv3-88x31.png)


* CLI tools
    * [`firejail`](https://github.com/netblue30/firejail)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/firejail.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/firejail.svg)](https://repology.org/metapackage/firejail/versions)[![Test Status](https://travis-ci.org/netblue30/firejail.svg?branch=master)](https://travis-ci.org/netblue30/firejail)[![Build Status](https://gitlab.com/Firejail/firejail_ci/badges/master/pipeline.svg)](https://gitlab.com/Firejail/firejail_ci/pipelines/)![Licence](https://img.shields.io/github/license/netblue30/firejail.svg)
    * [`git`](https://github.com/git/git)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/git.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/git.svg)](https://repology.org/metapackage/git/versions)![Licence](https://img.shields.io/github/license/git/git.svg)
    * [`7z`](https://www.7-zip.org/download.html)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/p7zip.svg)]()[![latest packaged version(s)](https://repology.org/badge/latest-versions/p7zip.svg)](https://repology.org/metapackage/p7zip/versions)
    * [`aria2c`](https://github.com/aria2/aria2)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/aria2.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/aria2.svg)](https://repology.org/metapackage/aria2/versions)[![GNU General Public License v2](https://img.shields.io/github/license/aria2/aria2.svg)](https://www.gnu.org/licenses/gpl-2.0.en.html);
    * [`alien`](https://sourceforge.net/projects/alien-pkg-convert/files/)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/alien.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/alien.svg)](https://repology.org/metapackage/alien/versions)[![GNU General Public License v2](https://img.shields.io/badge/license-GPL--2.0-fe7d37.svg)](https://www.gnu.org/licenses/gpl-2.0.en.html)
    * [`strip-nondeterminism`](https://salsa.debian.org/reproducible-builds/strip-nondeterminism)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/strip-nondeterminism.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/strip-nondeterminism.svg)](https://repology.org/metapackage/strip-nondeterminism/versions)[![GNU General Public License v3](https://www.gnu.org/graphics/gplv3-88x31.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)
    * [`fakeroot`](https://salsa.debian.org/clint/fakeroot)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/fakeroot.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/fakeroot.svg)](https://repology.org/metapackage/fakeroot/versions)[![GNU General Public License v3](https://www.gnu.org/graphics/gplv3-88x31.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)
    * [`reprepro`](https://salsa.debian.org/brlink/reprepro)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/reprepro.svg)![latest packaged version(s)](https://repology.org/badge/latest-versions/reprepro.svg)](https://repology.org/metapackage/reprepro/versions)[![GNU General Public License v2](https://img.shields.io/badge/license-GPL--2.0%2B-fe7d37.svg)](https://www.gnu.org/licenses/gpl-2.0.en.html)
    * [`dpkg-sig`](https://sources.debian.org/src/dpkg-sig/)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/dpkg-sig.svg)](https://packages.debian.org/stable/dpkg-sig)[![latest packaged version(s)](https://repology.org/badge/latest-versions/dpkg-sig.svg)](https://repology.org/metapackage/dpkg-sig/versions)[![GNU General Public License v2+](https://img.shields.io/badge/license-GPL--2.0-fe7d37.svg)](https://sources.debian.org/src/dpkg-sig/0.13.1+nmu4/copyright/)
    * [`dpkg-dev`](https://git.dpkg.org/cgit/dpkg/dpkg.git)[![Debian Stable package](https://repology.org/badge/version-for-repo/debian_stable/dpkg-dev.svg)](https://packages.debian.org/stable/dpkg-dev)[![latest packaged version(s)](https://repology.org/badge/latest-versions/dpkg-dev.svg)](https://repology.org/metapackage/dpkg-dev/versions)[![GNU General Public License v2](https://img.shields.io/badge/license-GPL--2.0%2B-fe7d37.svg)](https://www.gnu.org/licenses/gpl-2.0.en.html)

Tutorial
--------

Reading the source code of the essential parts is strictly needed. This tool is not a ready-made stuff. It is a **framework** allowing you do do the stuff **easily**. It does lot of things for you, but you need to understand what it does. It is not `bash`.  It is **object-oriented**. It is poorly documented, the docs is the code itself. You cannot use it without mastering it. But mastering it IMHO worth. And and the stuff was designed to be easy to master. So, roll up your sleeves and prepare to get your hands dirty.


** All the stuff done by build scripts and systems is explicitly trusted. Don't build software from untrusted sources.**


* Get known the purpose of classes and modules:
	* Some misc shit you usually don't want to touch directly:
		* `.tools` - just wrappers around command-line and not-so-command-line tools. Some of them use subrocesses. Some of them are not command line tools, but just python bindings (and we wanna rewrite as much of them to use bindings). This subpackage is just a semantic way to organize them. If you wanna need to use some CLI tool during your build, just check that subpackage first.
		* `.utils` - just miscellaneous utils.
		* `.webServices` - interactions to services likr GitHub, GitLab, BitBucket and Launchpad.
	
	* The global shit you likely need to touch:
		* `RunConfig` - some args to the tool. Temporary dirs mostly. You likely don't need to touch it directly, the defaults are sensible.
			* `.core.Person` - an entity with nickname o email. `core.Maintainer` is a person which fields are automatically captured from environment variables.
		* `.buildPipeline.BuildPipeline` - A build pipeline for a single piece of software
		* `.repoPipeline.RepoPipeline` - A pipeline creating a single repository.
	
	* In order to build a software you need to construct `BuildPipeline`:
		* `PackageMetadata` - Each package must have metadata. Some of it is retrieved automatically. Some is not. Highly depends on what is provided by the build system. The metadata provided here is merged to the metadata provided by build system. You can specify different metadata for each distro.
			* `PackageRef` - you need to call the package somehow.
			* interpackage relations.
			* descriptions
		
		* `BuildRecipy` - describes how to **build** a certain piece of software.
			* `IFetcher` - an interface describing how to get source code (or data) for building a package. Also responsible for extraction of some metadata (more precisely, a version).
				* `DiscoverDownloadVerifyUnpackFetcher` - Discovers an archive with the latest release, downloads it, verifies its integrity, then unpacks it. As the name suggests, combines 4 components:
					* `Discoverer` - Interacts with various services.
						* `GithubReleasesDiscoverer` - discovers releases on GitHub.
					* `Downloader` - Downloads the software using `aria2c`.
					* `Verifier` - verifies integrity.
						* `GPGVerifier` - checks an OpenPGP signature.
						* `HashesVerifier` - checks hashes against the file with them. Integrity of that file must be verified with an another verifier.
					* `Unpacker` - unpacks archives.
				* `GitRepoFetcher` - Clones a git repo.
		
			* `BuildSystem` - A class abstracting a build system. You usually don't need to instantiate them. It
				* configures packages
				* builds them
				* installs them into a dedicated dir
					* `Action` is the stuff describing what to do in order to install a piece of package.
					* `core.FilesTracker.FilesTracker` tracks files, symlinks and dirs. It also generates checksums.
					* Some build systems emit subpackages and actions.
			* `.systems` - contains build systems. Each one has own arguments. Read the code.
				* A special `Dummy` build system builds nothing. Useful when repackaging already built stuff.
			* `buildOptions` - you may add options applied on configuration stage as a dict.
			* `patches` - you may want to apply some patches.
			
	
	* Once you have built the software, it is transformed into packages and packed into repos:
		* `.tearers` - split packages into subpackages having certain roles, we call them `group`s. For example, when you build a software and install it, you can get a library, a command-line interface to that library, syntax highlighting to its configs, bash autocompletion, and docs. They are usually mixed int a pile. Tearers are what automatically split this pile into different packages.
		
		* `Distro` - Each distro has a set of conventions how to split the software into multiple packages and where to install them. This object incapsulates these conventions.
		* `.distros` - contains descriptions of distros and distro-specific code. Such as Debian, Fedoara, Arch and pseudodistros as Android, Windows, etc... You usually don't need to interact to them directly, you only need to specify them, and the pipeline will do most of stuff itself`.
			* Each distro has an own naming conventions on how to name packages belonging to each group. For example, packages having libs are usually have names beginning with `lib` and packages containing python packages have names beginning from `python3`. These contains the code to convert names to distro-specific and back. `core.NamingPolicy` is a class encapsulating stuff needed for that. Some widespread naming transformations can be found in `.namingPolicies`.
			* Each distro has own locations where to put files belonging to different packages.
			* Each distro has own release cycle and names of releases.
			* Each distro uses some package manager and uses some tools to build packages and repositories. We abstract it too.
		
		* `RepoPipelineMeta` is a special metaclass providing syntax sugar allowing creation of `RepoPipeline` to look like a class.
	
	* `.importers` - sometimes you already have the metadata in the format of other tools, this submodule contains the tools to transform these metadata into the format available to `prebuilder`:
		* `debhelper` `debian` directory.
		* `RPM` `spec` files.
* Import everything you need
* Create a
```python
class build(metaclass=RepoPipelineMeta):
	pass
```
* Add there a function for every software you need packages for. For [example]
```python
	def comps(): # just a convenient name for us. Prfix with `_` in order to disable
		repoURI = "https://github.com/rpm-software-management/libcomps" # GitHub Repo URI
		class cfg(metaclass=ClassDictMeta): # special syntax sugar for making a dict definition look like a class definition. Here we define our metadata
			descriptionShort = "Libcomps is a pure C alternative for yum.comps library."
			descriptionLong = "And there are bindings for python2 and python3."
			section = "devel"
			homepage = repoURI
		
		buildRecipy = BuildRecipy(
			CMake, # the stuff use CMake as a build system
			GitRepoFetcher(repoURI, refspec="master"), # git the source from a git repo
			
			patches = [(thisDir / "patches" / "libcomps")], # apply patches. libcomps is a dir, so apply the patches in it.
			buildOptions = { # pass the following additional options to CMake
				"PYTHON_DESIRED": 3,
				"ENABLE_TESTS": False,
				"ENABLE_DOCS": False,
			},
			subdir="libcomps" # usually unneeded. In our case CMakeLists is not in the root of the repo.
		)
		metadata = PackageMetadata("comps", **cfg) # Create a metadata object. The first arg should be a `PackageRef` but here it is OK provide string, it will do everything needed itself. THE NAME IS WITHOUT ANY PREFIXES AND SUFFIXES! IT WILL GENERATE THEM ITSELF.
		
		# we must return a BuildPipeline
		return BuildPipeline(
			buildRecipy,
			(
				(Debian, metadata), # we need to build packages for Debian having metadata `metadata`
			)
		)
```
