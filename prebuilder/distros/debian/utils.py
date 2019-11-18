import typing
import os

from ...core.Package import VersionedPackageRef, PackageRef
from ...core.Distro import Distro

debianPackageRelationKwargs = ("depends", "provides", "recommends", "suggests", "replaces", "conflicts", "breaks", "enhances")


def createConfigFromDict(d: typing.Mapping[str, str]) -> str:
	return os.linesep.join(str(k) + ": " + str(v) for k, v in d.items()) + os.linesep


def processDescriptionField(controlDict: typing.Mapping):
	ls = controlDict["description"].splitlines()
	if ls[0] != " ":
		shortDescr = ls[0]
		longDescr = []
		longDescrAccum = []
		for i in range(1, len(ls)):
			l = ls[i]
			if l[0] == " ":
				l = l.strip()
				if l == ".":
					l = "\n"
					longDescr.append(" ".join(longDescrAccum))
					longDescrAccum = []
				else:
					longDescrAccum.append(l)
			else:
				raise ValueError("Line " + str(i) + " of the `description` is not padded with spaces")
		if longDescrAccum:
			longDescr.append(" ".join(longDescrAccum))
			longDescrAccum = []
		longDescr = "\n".join(longDescr)
	else:
		raise ValueError("1st line of the `description` must not be padded, it is SHORT DESCRIPTION, it is MANDATORY")

	controlDict["descriptionShort"] = shortDescr
	controlDict["descriptionLong"] = longDescr
	del controlDict["description"]


def controlDictToArgs(d: typing.Mapping[str, typing.Any]):
	res = type(d)()
	for k, v in d.items():
		res[k.lower()] = v
	if "description" in res:
		processDescriptionField(res)
	if "architecture" in res:
		res["arch"] = res["architecture"]
		del res["architecture"]
	return res


def parsePackagesRelationsField(v):
	rels_ = v.split(",")
	rels = []
	for rel in rels_:
		rel = rel.strip()
		if "|" in rel:
			rel = set(alt.strip() for alt in rel.split("|"))
		rels.append(rel)
	return rels


def serializePackagesRelationsField(distro: Distro, v: typing.Set[str]) -> str:
	if not isinstance(v, str):
		_rels = []
		for c_ in v:
			#if isinstance(c_, (str, VersionedPackageRef)):
			if isinstance(c_, (str, PackageRef)):
				_rels.append(distro.decodeAnotherPackageRefIntoStr(c_))
			elif hasattr(c_, "__iter__"):
				_rels.append(" | ".join(distro.decodeAnotherPackageRefIntoStr(e) for e in c_))
			else:
				raise ValueError(repr(c_))
		v = ", ".join(_rels)
	return v
