import typing
from pathlib import Path
from collections import OrderedDict
import re
from pprint import pprint
from warnings import warn

from ..core.Tearer import TearingSpec, RipAction, SymlinkAction
from ..distros.debian import Debian
from ..distros.debian.utils import controlDictToArgs, debianPackageRelationKwargs
from ..distros.debian.BuiltPackage import DebPackageInstallSpec
from ..core.Package import PackageMetadata, VersionedPackageRef, PackagingSpec
from ..utils.VPath import VPath

relationsKwargsRawSet = {(a[0].upper() + a[1:].lower()) for a in debianPackageRelationKwargs} | {"Build-Depends"}  # assummes no dashes in original stuff

def processDebControlList(listText: str):
	for d in listText.split(","):
		if d:
			yield d.strip()

def parseControlText(controlText: str):
	from email import message_from_string

	control = []

	while controlText:
		msg = message_from_string(controlText)
		h = OrderedDict(msg._headers)
		for listName in relationsKwargsRawSet:
			if listName in h:
				res = []
				for dl in h[listName].splitlines():
					res.extend(processDebControlList(dl))
				h[listName] = res
		control.append(h)
		controlText = msg._payload
	return control

spacesRx = re.compile("\\s+")
commentRx = re.compile("#.+$")
def parseMultiFieldFile(f: Path):
	if f.exists():
		res = []
		with f.open("rt") as f:
			for l in f:
				if l[-1] == "\n":
					l = l[:-1]
				m = commentRx.search(l)
				if m:
					l = l[:m.span()[0]]
				if not l:
					continue
				res.append(tuple(spacesRx.split(l)))
		return res
	else:
		return []


def parseMappingFile(f: Path):
	return OrderedDict(parseMultiFieldFile(f))


embeddedExprRx = re.compile("\\$\\{[^\\}\\{\\$\\n]+\\}")
embeddedConditionRx = re.compile("\\[[^\\[\\]\\n]+\\]")


def stripVersionConditionFromPackageRelation(res):
	bracePos = res.rfind("(")
	if bracePos > 0:
		res = res[:bracePos].strip()
	return res

def binaryVersionVariableProcessor(m, el, metadata, spec):
	"""Just strips version specifier."""
	res = el[: m.span()[0]]
	res = stripVersionConditionFromPackageRelation(res)
	warn("version specifier stripped: `" + el +"` -> `" + res + "`")
	return res


def dummyVariableProcessor(m, el, metadata, spec):
	"""Just removes the field with this variable"""
	warn("embedded variable ignored: " + el)
	return None


variablesRemap = {
	"sphinxdoc:Depends": dummyVariableProcessor,
	"shlibs:Depends": dummyVariableProcessor,
	"misc:Depends": dummyVariableProcessor,
	"perl:Depends": dummyVariableProcessor,
	"python:Depends": dummyVariableProcessor,
	"python:Provides": dummyVariableProcessor,
	"python:Breaks": dummyVariableProcessor,
	"python3:Depends": dummyVariableProcessor,
	"python3:Provides": dummyVariableProcessor,
	"python3:Breaks": dummyVariableProcessor,
	
	"source:Version": binaryVersionVariableProcessor,
	"binary:Version": binaryVersionVariableProcessor,
}

def processRelationGroup(grp, metadata, spec):
	res = []
	for el in grp:
		m = embeddedConditionRx.search(el)
		if m:
			warn("embedded condition ignored: " + el)
			continue
		while el:
			m = embeddedExprRx.search(el)
			if m:
				#print(evalEmbExpr, m.group(0))
				expr = m.group(0)
				assert expr[0:2] == "${"
				assert expr[-1] == "}"
				exprName = expr[2:-1]
				#print("exprName", exprName, exprName in self.ns)
				el = variablesRemap[exprName](m, el, metadata, spec)
			else:
				break
		if isinstance(el, str):
			el = Debian.toPackageRefWithGroupResolved(el)
		if el:
			res.append(el)
	return res


def debianInstallSpecToTearingSpec(ref, spc: DebPackageInstallSpec) -> TearingSpec:
	actions = []
	
	for groupName in ("install", "manpages", "docs", "dirs"):
		for f in getattr(spc, groupName):
			if len(f) > 2:
				raise ValueError(groupName, f)
			src = VPath(f[0])
			if len(f) == 2:
				dst = VPath(f[1])
				dst._is_dir = True
				
				act = RipAction(src, dst, globAllowed=True, ignoreMissing=True)
			else:
				act = RipAction(src, globAllowed=True, ignoreMissing=True)
			actions.append(act)

	for src, dst in spc.links.items():
		actions.append(SymlinkAction(VPath(src), VPath(dst), globAllowed=True))
	#spec.symbols
	#spec.lintianOverrides

	return TearingSpec(ref, actions)


def parseDebhelperDebianDir(path: Path):
	controlFile = path / "control"

	controls = parseControlText(controlFile.read_text())
	sourceControl = None

	pkgs = OrderedDict()
	for i, parsedControl in enumerate(controls):
		parsedControl = controlDictToArgs(parsedControl)
		if "source" in parsedControl:
			if sourceControl is None:
				sourceControl = parsedControl
			else:
				raise ValueError("More than 1 Source in a control file")
		elif "package" in parsedControl:
			pkgName = parsedControl["package"]
			del parsedControl["package"]

			# TODO: path sanitization
			spec = DebPackageInstallSpec()
			for propName in ("install", "dirs", "manpages", "docs"):
				setattr(spec, propName, parseMultiFieldFile(path / ".".join((pkgName, propName))))

			spec.links = parseMappingFile(path / (pkgName + ".links"))
			spec.symbols = parseMultiFieldFile(path / (pkgName + ".symbols"))
			spec.lintianOverrides = parseMultiFieldFile(path / (pkgName + ".lintian-overrides"))
			#print(parsedControl)

			pkgRef = Debian.toPackageRefWithGroupResolved(pkgName)
			metadata = PackageMetadata(pkgRef, **parsedControl)

			for relationGroupName in debianPackageRelationKwargs:
				if relationGroupName in metadata.controlDict:
					metadata.controlDict[relationGroupName] = processRelationGroup(metadata.controlDict[relationGroupName], metadata, spec)

			print(spec)
			pkgs[metadata] = debianInstallSpecToTearingSpec(metadata.ref, spec)

	return {"source": sourceControl, "pkgs": tuple(pkgs.items())}
