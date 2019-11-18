import typing
import sys
from pathlib import Path
from .core.Package import Package, PackageRef, VersionedPackageRef
from .core.Distro import Distro
from .core.RunConfig import RunConfig
from .buildPipeline import BuildPipeline
from collections import OrderedDict
from . import globalPrefs

thisDir = Path(".").absolute()


class RepoPipeline:
	__slots__ = ("distros", "pipelines", "cfg", "repoDescrTemplate", "order", "ref2pipeline", "name2pipeline", "installed")

	def __init__(self, distros: typing.Iterable[Distro], repoDescrTemplate: str = "It's {maintainerName}'s {repoKind} repo for {distroName}") -> None:
		self.distros = list(distros)
		self.pipelines = OrderedDict()
		self.repoDescrTemplate = repoDescrTemplate
		self.order = None
		self.ref2pipeline = {}
		self.name2pipeline = {}
		self.installed = set()
		
		for pl in self.pipelines.values():
			r = pl.pkgRef
			self.ref2pipeline[r] = pl
			self.name2pipeline[r.name] = pl

	def __setitem__(self, key: str, pkgPipelineOrFunc: typing.Union[BuildPipeline, typing.Callable[[], BuildPipeline]]) -> "RepoPipeline":
		print("pkgPipelineOrFunc", pkgPipelineOrFunc, isinstance(pkgPipelineOrFunc, BuildPipeline))
		if isinstance(pkgPipelineOrFunc, BuildPipeline):
			pkgPipeline = pkgPipelineOrFunc
		else:
			pkgPipeline = pkgPipelineOrFunc()

		assert isinstance(pkgPipeline, BuildPipeline), pkgPipeline
		self.pipelines[key] = pkgPipeline
		return self
	
	def __getitem__(self, key: typing.Union[PackageRef, str]) -> BuildPipeline:
		if isinstance(key, PackageRef):
			if key in self.ref2pipeline:
				return self.ref2pipeline[key]
			else:
				return self.name2pipeline[key.name]
		elif isinstance(key, str):
			if key in self.name2pipeline[key.name]:
				return self.name2pipeline[key]
			else:
				return pipelines[key]
		else:
			raise TypeError("Key must be either a `str` or a `PackageRef", type(key))

	def topo_sort_dependencies(self):
		res = []
		roots = []
		visited = set()
		loopDetect = {}
		pathStack = []
		res = []
		
		def visit(pl):
			nonlocal pathStack
			if pl.pkgRef in visited:
				return
			if pl.pkgRef in loopDetect:
				raise ValueError("Cyclical dependency chain is detected!", pathStack[loopDetect[pl.pkgRef]:])
			loopDetect[pl.pkgRef] = len(pathStack)
			pathStack.append(pl.pkgRef)
			for r1 in pl.buildRecipy.dependencies:
				pl1 = self[r1]
				#print(pl.pkgRef, "->", pl1.pkgRef)
				visit(pl1)
			pathStack = pathStack[:loopDetect[pl.pkgRef]]
			del loopDetect[pl.pkgRef]
			visited.add(pl.pkgRef)
			res.append(pl)
		
		while len(visited) < len(self.ref2pipeline):
			for pl in self.ref2pipeline.values():
				visit(pl)
		return list(res)

	def executePipeline(self, pl, cfg):
		for dep in pl.buildRecipy.dependencies:
			if dep not in self.installed:
				currentDistro.install(dep)
				self.installed.add(dep)
		return pl(cfg)
	
	def prepare(self):
		for pl in self.pipelines.values():
			r = pl.pkgRef
			self.ref2pipeline[r] = pl
			self.name2pipeline[r.name] = pl
		self.order = self.topo_sort_dependencies()

	def __call__(self, cfg: RunConfig = None):
		if cfg is None:
			cfg = RunConfig()
		
		self.prepare()
		
		#print("self.order", [pl.pkgRef for pl in self.order])
		#raise Exception()

		streams = []
		for pl in self.order:
			streams.extend(self.executePipeline(pl, cfg))

		if globalPrefs.createRepos:
			for distro in self.distros:
				with distro.repoClass(cfg=cfg, descr=self.repoDescrTemplate.format(maintainerName=cfg.maintainer.name, repoKind=distro.repoClass.kind, distroName=distro.name)) as r:
					r += streams
		else:
			if globalPrefs.buildPackages:
				for stream in streams:
					for pkg in stream:
						pkg.build()


def RepoPipelineMeta(className: str, parents: typing.Tuple, attrs: typing.Dict[str, typing.Union[str, typing.Tuple[Distro], typing.Callable]], *args, **kwargs) -> RepoPipeline:
	print("attrs", attrs)
	# it's used as a metaclass to create a package
	pipelineArgs = {}
	attrsRemap = {"DISTROS": "distros", "CFG": "cfg", "__doc__": "repoDescrTemplate"}

	pkgs = OrderedDict()

	for k, v in attrs.items():
		if k in attrsRemap:
			pipelineArgs[attrsRemap[k]] = v
		else:
			if k[0] != "_":
				pkgs[k] = v

	print("pipelineArgs", pipelineArgs)
	distros = pipelineArgs["distros"]  # positional
	del pipelineArgs["distros"]
	res = RepoPipeline(distros, **pipelineArgs)

	for k, pkg in pkgs.items():
		res[k] = pkg

	return res
