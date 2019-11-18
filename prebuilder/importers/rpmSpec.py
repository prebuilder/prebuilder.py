import typing
import platform
import re

from pyrpm.spec import Spec, _parse, _tags
from pathlib import Path
from AnyVer import AnyVer

from ..core.Tearer import TearingSpec, RipAction, SymlinkAction
from ..distros import nativeDistro
from ..distros.rpm_based import RPMBased, PyPKGResolver
from ..distros.debian.utils import controlDictToArgs, debianPackageRelationKwargs
from ..core.Package import PackageMetadata, VersionedPackageRef, PackagingSpec, BasePackageRef, PackageRef
from ..utils.VPath import VPath

from ..namingPolicies import universalNamingPolicy
from FHS.GNUDirs import getGNUDirs
from FHS import Common as CommonDirs

r = PyPKGResolver(nativeDistro.packageManager)


funcNameRx = re.compile("^(\w+)\(([^\(\)]+)\)$")
def processPkgConfigName(name):
	res = r(name)
	print(res)
	return res
	

funcsRemap = {
	"pkgconfig": processPkgConfigName
}


def processRelationGroup(grpName, metadata, spec):
	src = getattr(spec, grpName)
	res = []
	for pkgDepSpc in src:
		rn = pkgDepSpc.name
		m = funcNameRx.match(rn)
		if m:
			funcN, args = m.groups()
			print(funcN, args)
			args = tuple(a.strip() for a in args.split(","))
			refs = funcsRemap[funcN](*args)
			refs = [nativeDistro.toPackageRefWithGroupResolved(rn) for r in refs]
		else:
			refs = (RPMBased.toPackageRefWithGroupResolved(rn),)
		
		for ref in refs:
			if pkgDepSpc.version:
				ref = PackageRef.clone(ref, cls=VersionedPackageRef, version=AnyVer(pkgDepSpc.version))
			#print(pkgDepSpc, ref)
			res.append(ref)
	metadata[grpName] = set(res)

gnuDirs = getGNUDirs("/usr")

def initializeSpecDirs():
	res = {}
	for k, v in gnuDirs.toGnuArgs().items():
		res["_" + k] = str(v)
	res["python3_sitearch"] = str(gnuDirs.lib / "python3/dist-packages/")
	res["python2_sitearch"] = str(gnuDirs.lib / "python2.7/dist-packages/")
	res["python2_sitelib"] = "/usr/lib/python2.7/dist-packages/"
	res["python3_sitelib"] = "/usr/lib/python3/dist-packages/"
	res["_unitdir"] = str(CommonDirs.systemdUnitsDir)
	return res


def parseSpec(path):
	return Spec.from_file(Path(path), initializeSpecDirs())


metadataFields = ( 'group', 'license',  'name',  'summary', 'url', 'version', 'epoch', 'release',)
relationsGroups = ( 'obsoletes', 'requires', 'conflicts', 'provides', 'build_requires')

def makeTearingSpec(ref, p) -> TearingSpec:
	actions = []

	for groupName in ("files", "dir", "doc", "config"):
		for src in getattr(p, groupName):
			actions.append(RipAction(src, globAllowed=True, ignoreMissing=True))

	#for src, dst in p.links.items():
	#    actions.append(SymlinkAction(VPath(src), VPath(dst), globAllowed=True))
	#spec.symbols
	#spec.lintianOverrides

	return TearingSpec(ref, actions)


def parseRPMSpec(fileName: Path):
	spec = parseSpec(fileName)
	pkgs = {}
	metadataFields = ( 'group', 'license',  'name',  'summary', 'url', 'epoch', 'release',)
	relationsGroups = ( 'obsoletes', 'requires', 'conflicts', 'provides', 'build_requires')

	packages = [spec] + spec.packages
	for p in packages:
		pkgRef = RPMBased.toPackageRefWithGroupResolved(p.name)
		try:
			pkgRef = pkgRef.clone(cls=VersionedPkgRef, version=AnyVer(p.version))
		except:
			pass
		
		p.version = None
		metadata = PackageMetadata(pkgRef)
		
		for rgName in relationsGroups:
			processRelationGroup(rgName, metadata.controlDict, p)
		for nm in metadataFields:
			if hasattr(p, nm):
				metadata.controlDict[nm] = getattr(p, nm)
		pkgs[metadata] = makeTearingSpec(pkgRef, p)
	
	return {"source": None, "pkgs": tuple(pkgs.items())}
