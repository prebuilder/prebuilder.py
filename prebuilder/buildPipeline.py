import typing
from pathlib import Path
from shutil import which, rmtree
from pantarei import chosenProgressReporter
from enum import IntFlag
from RichConsole import rsjoin

from .tools.determinism import DeterministicTimestamps
from .tools.patches import applyPatch
from .tools.ldconfig import commonLibDirs

#from .tools.help2man import help2man
from .core.Person import Maintainer
from TargetTriple import TargetTriple
from .core.Package import Package, BasePackageRef, PackageRef, VersionedPackageRef, PackageInstalledFiles, PackageMetadata, PackagingSpec, AssociateTearingSpecAndMetadata
from .core.BuiltPackage import BuiltPackage
from .core.BuildSystem import BuildSystem
from .core.Distro import Distro
from FHS.GNUDirs import getGNUDirs


#from .core.Tearer import *
from .core.Fetcher import IFetcher
from .core.RunConfig import RunConfig
from .styles import styles
from .extractors import DepsResolver
from .extractors.ELF import ELFExtractor, ELFDepsResolver, _ELFDepsResolver
from . import globalPrefs

DistroT = typing.Type[Distro]


archNeutralGroups = {"python2", "python3", "data", "docs"}
dependenciesExtractors = (
	({"tools", "libs", "dev", "lua_dev", "lua", "python2", "python3", "golang", "rust", "perl"}, ELFExtractor()),
)


class MultipackageELFDepsResolver(_ELFDepsResolver):
	__slots__ = ("filesDependenciesMaps",)

	def __init__(self, upstreamResolver: ELFDepsResolver, filesDependenciesMaps: typing.Dict[Path, VersionedPackageRef]) -> None:
		self.filesDependenciesMaps = filesDependenciesMaps
		super().__init__(upstreamResolver.order, None, commonLibDirs)

	#def report(self, cand, result):
	#	print("Resolving ", cand, result)

	def resolveFile(self, file: Path) -> typing.Optional[VersionedPackageRef]:
		return self.filesDependenciesMaps.get(file)


class DistroStream:
	"""Stream of half-built packages for the distro"""

	__slots__ = ("distro", "packagingSpec", "packages", "filesDependenciesMaps", "deversionedToPkgMap", "detectDependencies")

	def __init__(self, distro: Distro, packagingSpec: typing.Union[PackageMetadata, PackagingSpec], detectDependencies: bool= True) -> None:
		self.distro = distro
		self.packages = []
		self.filesDependenciesMaps = {}
		self.deversionedToPkgMap = {}
		if isinstance(packagingSpec, PackageMetadata):
			packagingSpec = PackagingSpec(packagingSpec, None)
		elif isinstance(packagingSpec, (list, tuple)): # it is tearing specs
			packagingSpec = PackagingSpec(None, packagingSpec)
		elif isinstance(packagingSpec, PackagingSpec):
			pass
		else:
			raise ValueError(packagingSpec)

		self.packagingSpec = packagingSpec
		self.detectDependencies = detectDependencies

	def collectPackagesFilesToDependenciesMap(self) -> None:
		filesDependenciesMaps = {}
		for pkgTorn in self.packages:
			assert isinstance(pkgTorn.metadata.ref, VersionedPackageRef), pkgTorn.metadata
			filez = sorted(pkgTorn.installation.filesTracker.filesAndSymlinks)
			assert filez, pkgTorn
			for f in filez:
				if f not in filesDependenciesMaps:
					filesDependenciesMaps[f] = pkgTorn.ref
				else:
					raise Exception("File " + str(f) + " was provided by " + str(pkgTorn) + " but was already provided by " + str(filesDependenciesMaps[f]) + "!")
		#print("filesDependenciesMaps", filesDependenciesMaps)

		self.filesDependenciesMaps = filesDependenciesMaps

	def __iadd__(self, pkg: Package) -> "DistroStream":
		assert isinstance(pkg.metadata.ref, VersionedPackageRef), pkg.metadata
		if pkg.metadata.packagerSpecific:
			if self.distro.builder.packageExtension in pkg.metadata.packagerSpecific:
				sp = pkg.metadata.packagerSpecific[self.distro.builder.packageExtension]
				if sp:
					if "name" in sp:
						ref = self.distro.toPackageRefWithGroupResolved(sp["name"])
						del sp["name"]
						pkg.metadata.ref.name, pkg.metadata.ref.group = ref.name, ref.group
					pkg.metadata.packagerSpecific = None
					pkg.metadata.controlDict.update(sp)
		else:
			pkg.metadata.packagerSpecific = None
		self.packages.append(pkg)
		self.deversionedToPkgMap[pkg.metadata.ref.clone(cls=PackageRef)] = pkg
		return self
	
	@classmethod
	def _applyMetadata(cls, packageMetadata: PackageMetadata, currentInstallData: PackageInstalledFiles, tr: AssociateTearingSpecAndMetadata):
		if not isinstance(packageMetadata.ref, VersionedPackageRef):
			packageMetadata.ref = packageMetadata.ref.clone(cls=VersionedPackageRef, version=tr.installation.ref.version)
	
		print("tr.packagingSpec.commonMetadata", tr.packagingSpec.commonMetadata)
		if tr.packagingSpec.commonMetadata is not None:
			metadataDict = type(tr.packagingSpec.commonMetadata.controlDict)(tr.packagingSpec.commonMetadata.controlDict)
		else:
			metadataDict = {}
		metadataDict.update(packageMetadata.controlDict)
		return Package(PackageMetadata(packageMetadata.ref, **metadataDict), currentInstallData)
	
	def _tearPackage(self, tr: AssociateTearingSpecAndMetadata):
		assert tr.installation.needsTearing
		splittedDir = tr.installation.root / "subpackages"
		tr.installation.ref  = self.distro.toPackageRefWithGroupResolved(tr.installation.ref)
		
		if tr.packagingSpec.tearingSpecs is None:
			tr.packagingSpec.tearingSpecs = self.distro.tearer(tr.installation).items()
		
		print(styles.entity("torn") + " " + rsjoin(", ", 
			(styles.varContent(str(individualMetadata if isinstance(individualMetadata, VersionedPackageRef) else individualMetadata.ref)) for individualMetadata, tearingSpec in tr.packagingSpec.tearingSpecs)
		))

		for individualMetadata, tearingSpec in tr.packagingSpec.tearingSpecs:
			tornInstalled = tearingSpec(tr.installation)  # of type PackageInstalledFiles
			if isinstance(individualMetadata, VersionedPackageRef):
				individualMetadata = PackageMetadata(individualMetadata)
			self += self.__class__._applyMetadata(individualMetadata, tornInstalled, tr)

	def tearPackage(self, installData: PackageInstalledFiles):
		if isinstance(installData, PackageInstalledFiles):
			#print("installData", installData, installData.needsTearing)
			print("self.packagingSpec", self.packagingSpec)
			tr = AssociateTearingSpecAndMetadata(installData, self.packagingSpec)
			if installData.needsTearing:
				self._tearPackage(tr)
			else:
				self += self.__class__._applyMetadata(PackageMetadata(installData.ref), installData, tr)
		else:
			self += installData

	def extractArchitectureAndDependenciesFromELF(self) -> None:
		for pkg in self.packages:
			assert isinstance(pkg, Package), repr(pkg)
			deps = set()
			
			for groups, extr in dependenciesExtractors:
				if pkg.ref.group in groups:
					print(styles.operationName("extracting") + " " + styles.entity("architecture-dependent info") + " from " + styles.varContent(str(pkg.ref)) + " using " + styles.entity(extr.__class__.__name__) + " ...")
					filez = sorted(pkg.filesTracker.files)
					assert filez
					
					with chosenProgressReporter(len(filez), str("extracting info")) as pb:
						for fp in filez:
							f = pkg.nest(fp)
							if f.is_file():
								#print(styles.operationName("extracting") + " " + styles.entity("architecture-dependent info") + " from " + styles.entity("file") + ": " + styles.varContent(str(f)))
								archAndDeps = extr(f)
								if archAndDeps:
									pkg.deps = archAndDeps.deps
									pkg.depsResolver = archAndDeps.depsResolver
									resultArch = self.distro.archTransformer(archAndDeps)
									if resultArch:
										if pkg.ref.arch is None:
											pkg.ref.arch = resultArch
										elif pkg.ref.arch != resultArch:
											raise ValueError("Package " + str(pkg.ref) + " contains binaries for different architectures, at least: " + pkg.ref.arch + " and " + resultArch)
							pb.report(fp)
						#print(styles.operationName("extracted") + ": " + styles.varContent(str(pkg.deps)))
				else:
					print(styles.entity(groups) + " " + styles.operationName("skipped") + ": " + styles.varContent(str(pkg.ref)) )

			if pkg.ref.arch is None:
				if pkg.ref.group in archNeutralGroups:
					#pkg.ref.arch = self.distro.archTransformer("any")
					pkg.ref.arch = self.distro.archTransformer("all")  # FUCK, `Error looking at 'package.deb': 'any' is not one of the valid architectures: 'amd64'`
				else:
					pkg.ref.arch = self.distro.archTransformer("all")

			#aggregatedControlDict = {}
			#aggregatedControlDict.update(self.packagingSpec.commonMetadata.controlDict)
			#pkg.metadata.controlDict = aggregatedControlDict

	def resolveDependencies(self) -> None:
		with self.distro.packageManager as packageManager:
			for pkgTorn in self.packages:
				assert isinstance(pkgTorn, Package)
				depsNew = {}

				if pkgTorn.deps:
					for d in pkgTorn.deps:
						# You may need to update ldconfig (`sudo ldconfig`) if you get any errors!!!
						resolvedDepPackage = None

						if resolvedDepPackage is None:
							r = MultipackageELFDepsResolver(pkgTorn.depsResolver, self.filesDependenciesMaps)
							resolvedDepPackage = r(d)

						if resolvedDepPackage is None:
							resolvedDepFile = pkgTorn.depsResolver(d)
							#print("resolvedDepFile", resolvedDepFile)
							if resolvedDepFile:
								resolvedDepPackage = packageManager.file2Package(resolvedDepFile)

						if resolvedDepPackage is None:
							raise KeyError(d)
						
						resolvedDepPackage = self.distro.toPackageRefWithGroupResolved(resolvedDepPackage)
						depsNewKey = resolvedDepPackage.clone(cls=PackageRef)
						if depsNewKey in depsNew and depsNew[depsNewKey] != resolvedDepPackage:
							raise ValueError("Duplicated the same dependency (probably with different versions) :" + (depsNew[depsNewKey], resolvedDepPackage))
						depsNew[depsNewKey] = resolvedDepPackage

				if "depends" not in pkgTorn.metadata.controlDict:
					oldDeps = set()
				else:
					oldDeps = pkgTorn.metadata.controlDict["depends"]
				
				if not isinstance(oldDeps, set):
					oldDeps = set(oldDeps)
				
				def mergeDeps(oldDeps):
					oldDeps = []
					addedDeps = []
					for dep in oldDeps:
						if not isinstance(dep, VersionedPackageRef):
							depsNewKey = dep.clone(cls=PackageRef)
							if depsNewKey in depsNew:
								dep = depsNew[depsNewKey]
								del depsNew[depsNewKey]
							elif depsNewKey in self.deversionedToPkgMap:
								dep = self.deversionedToPkgMap[depsNewKey].ref
							else:
								dep = packageManager[dep]
							oldDeps.append(dep)
					return set(oldDeps)
				
				oldDeps = mergeDeps(oldDeps)
				addedDeps = set(depsNew.values())
				joinedDeps = oldDeps | addedDeps
				
				if addedDeps:
					print(styles.operationName("found") + " " + styles.entity("additional deps") + " for " + styles.varContent(str(pkgTorn.metadata.ref)) + ": " + styles.varContent(", ".join(str(d) for d in addedDeps)))
				
				pkgTorn.metadata.controlDict["depends"] = joinedDeps

	def augmentMetadata(self) -> None:
		if self.detectDependencies:
			self.extractArchitectureAndDependenciesFromELF()
			self.collectPackagesFilesToDependenciesMap()
			self.resolveDependencies()

	def buildPackages(self, builtDir: Path) -> None:
		assert isinstance(builtDir, Path)
		packagesBuilt = []
		for pkg in self.packages:
			assert isinstance(pkg, Package)
			pkg.ref = self.distro.decodeRef(pkg.ref)
			builtPkg = self.distro.builder(pkg, builtDir, self.distro)
			assert builtPkg
			#builtPkg.build() # Do not uncomment! Triggered lazily and automatically!
			packagesBuilt.append(builtPkg)

		self.packages = packagesBuilt

	def __iter__(self) -> None:
		yield from self.packages

	def __repr__(self) -> str:
		return self.__class__.__name__ + "<" + repr(self.distro) + ", " + repr(self.packages) + ">"


class BuildRecipy:
	"""Encapsulates the details needeed to build a piece of software"""
	__slots__ = ("fetcher", "subdir", "buildOptions", "firejailCfg", "buildSystemAdditionalArgs", "patches", "buildSystem", "timestamp", "gnuDirs", "triple", "dependencies")

	def __init__(self, buildSystem: typing.Optional[BuildSystem], fetcher: IFetcher, prefixOrGNUDirs: str = "/usr", buildOptions: typing.Optional[typing.Dict[str, bool]] = None, subdir: None = None, patches: typing.Iterable[Path] = None, firejailCfg=None, triple: TargetTriple = None, dependencies: typing.Iterable[PackageRef] = None, **buildSystemAdditionalArgs) -> None:
		if isinstance(fetcher, str):
			fetcher = defaultRepoFetcher(fetcher)
		elif isinstance(fetcher, tuple):
			fetcher = defaultRepoFetcher(*fetcher)

		self.fetcher = fetcher

		self.subdir = subdir
		self.buildOptions = buildOptions
		
		if firejailCfg is None:
			firejailCfg = {}
		if "paths" not in firejailCfg:
			firejailCfg["paths"] = []
		
		self.firejailCfg = firejailCfg
		self.buildSystemAdditionalArgs = buildSystemAdditionalArgs
		self.patches = patches
		self.buildSystem = buildSystem
		self.timestamp = None
		
		if triple is None:
			triple = TargetTriple()
		
		self.triple = triple
		if dependencies is None:
			dependencies = []
		self.dependencies = dependencies
		
		if isinstance(prefixOrGNUDirs, str):
			self.gnuDirs = getGNUDirs(prefixOrGNUDirs, self.triple)
		else:
			self.gnuDirs = prefixOrGNUDirs
	
	def patchSources(self, fetchedDir):
		with DeterministicTimestamps(self.timestamp):
			if self.patches:
				patchingMsg = styles.operationName("Patching") + " ..."
				print(patchingMsg)
				with chosenProgressReporter(len(self.patches), str(patchingMsg)) as pb:
					for p in self.patches:
						applyPatch(p, fetchedDir)
						pb.report(p)

	def __call__(self, pkgRef: VersionedPackageRef, runConfig: RunConfig):
		fetchedDir = runConfig.sourcesDir / pkgRef.name

		versionNeeded = not isinstance(pkgRef, VersionedPackageRef)
		
		f = self.fetcher(fetchedDir, runConfig.fetchConfig, versionNeeded=versionNeeded)  # type: Fetched
		self.timestamp = f.time
		if versionNeeded:
			print("f.version", f.version)
			pkgRef = pkgRef.clone(cls=VersionedPackageRef, version=f.version)

		if globalPrefs.patch:
			self.patchSources(fetchedDir)

		firejailCfg = type(self.firejailCfg)(self.firejailCfg)

		if self.subdir:
			if callable(self.subdir):
				sourceDir = self.subdir(fetchedDir, pkgRef)
			elif isinstance(self.subdir, str):
				sourceDir = fetchedDir / self.subdir
			else:
				raise ValueError()
			firejailCfg["paths"].append(fetchedDir)
		else:
			sourceDir = fetchedDir

		with DeterministicTimestamps(self.timestamp):
			if self.buildSystem is None:
				self.buildSystem = detectBuildSystem(sourceDir)
				if self.buildSystem:
					print(styles.entity("Build system") + " " + styles.operationName("detected") + ": " + styles.varContent(self.buildSystem.__name__))
				else:
					raise Exception("Build system is not detected!")
			else:
				#print(styles.entity("Build system") + " " + "provided: " + styles.varContent(self.buildSystem.__name__))
				pass

			#print("pkgRef", pkgRef)
			#print("sourceDir", sourceDir)
			#print(firejailCfg["allowedDirs"])
			#print(self.gnuDirs)
			print(self.buildSystem)
			
			return self.buildSystem(sourceDir=sourceDir, ref=pkgRef, packagesRootsDir=runConfig.packagesRootsDir, gnuDirs=self.gnuDirs, buildOptions=self.buildOptions, firejailCfg=firejailCfg, **self.buildSystemAdditionalArgs)


class BuildPipeline:
	__slots__ = ("buildRecipy", "runConfig", "distros2metadata", "pkgRef", "pkgs", "distrosStreams", "detectDependencies", "refsRemap")
	def __init__(self, buildRecipy: BuildRecipy, distros2metadata: typing.Iterable[typing.Tuple[DistroT, PackageMetadata]], refsRemap: typing.Mapping[typing.Union[PackageRef, str], PackageRef]=None, detectDependencies:bool=True) -> None:
		self.buildRecipy = buildRecipy
		self.runConfig = None
		self.distros2metadata = distros2metadata
		self.detectDependencies = detectDependencies
		if refsRemap is None:
			refsRemap = {}
		self.refsRemap = refsRemap
		
		firstDistro = self.distros2metadata[0]
		firstDistroTearingAndMetadata = firstDistro[1]
		if isinstance(firstDistroTearingAndMetadata, PackageMetadata):
			firstDistroFirstSubpackageMetadata = firstDistroTearingAndMetadata
		elif isinstance(firstDistroTearingAndMetadata, PackagingSpec):
			firstDistroFirstSubpackageMetadata = firstDistroTearingAndMetadata.commonMetadata
		elif isinstance(firstDistroTearingAndMetadata, (list, tuple)):
			for firstDistroFirstSubpackageMetadata, firstDistroFirstSubpackageTearingSpec in firstDistroTearingAndMetadata:
				break
		else:
			raise ValueError()
		#print("firstDistroFirstSubpackageMetadata", firstDistroFirstSubpackageMetadata)
		
		self.pkgRef = firstDistroFirstSubpackageMetadata.ref

		self.pkgs = None
		self.distrosStreams = None

	def tearIntoDistroSpecificComponents(self) -> None:
		streams = [DistroStream(distro, packagingSpec, self.detectDependencies) for distro, packagingSpec in self.distros2metadata]
		
		for pkg in self.pkgs:

			if isinstance(pkg.ref, str):
				pkgRefIndex = pkg.ref
			else:
				pkgRefIndex = pkg.ref.clone(BasePackageRef)

			if pkgRefIndex in self.refsRemap:
				pkg.ref = self.refsRemap[pkgRefIndex]


			if isinstance(pkg.ref, str):
				pkg.ref = VersionedPackageRef(pkg.ref, version=self.pkgRef.version, arch=self.pkgRef.arch, group=self.pkgRef.group)

			if isinstance(pkg, PackageInstalledFiles):
				for s in streams:
					s.tearPackage(pkg)
			elif isinstance(pkg, AssociateTearingSpecAndMetadata):
				for s in streams:
					s._tearPackage(pkg)
			elif isinstance(pkg, Package):
				for s in streams:
					s += pkg
			#elif isinstance(pkg, BuiltPackage):
			#	s.packages.append(pkg)
			else:
				raise ValueError("Incorrect type of package: " + repr(pkg.__class__) + " " + repr(pkg))
		yield from streams

	def augmentMetadata(self) -> None:
		with chosenProgressReporter(len(self.distrosStreams), "Augmenting metadata") as pb:
			for s in self.distrosStreams:
				s.augmentMetadata()
				pb.report(s.distro.name)

	def buildDistroSpecificPackages(self) -> None:
		with chosenProgressReporter(len(self.distrosStreams), "Building packages (probably lazily)") as pb:
			for s in self.distrosStreams:
				s.buildPackages(self.runConfig.builtDir)
				pb.report(s.distro.name)

	def __call__(self, runConfig: typing.Optional[RunConfig] = None) -> typing.List[DistroStream]:
		if runConfig is None:
			runConfig = RunConfig()
		self.runConfig = runConfig

		self.runConfig.fetchConfig.dontFetch = not globalPrefs.fetch
		self.runConfig.fetchConfig.shallow = globalPrefs.shallowFetch

		"""
		if isinstance(cfg, (list, tuple)):
			pkgs = list(self.pkgs)
			if len(pkgs) != 1:
				raise Exception("multiple specs are provided (this means we rip them according to a spec embedded inro each cfg) but the build system emitted multiple packages")
		else:
		"""

		self.pkgs = list(self.buildRecipy(self.pkgRef, self.runConfig))
		print(styles.operationName("Tearing") + "...")

		self.distrosStreams = list(self.tearIntoDistroSpecificComponents())
		#print(styles.entity("torn") + " " + styles.varContent(repr(self.distrosStreams)))
		self.augmentMetadata()
		self.buildDistroSpecificPackages()
		return self.distrosStreams


class BuildPipelineMeta(type):
	def __new__(cls, className, parents, attrs, *args, **kwargs):
		attrsNew = type(attrs)()
		return super().__new__(cls, className, parents, {"delayed": attrsNew}, *args, **kwargs)
