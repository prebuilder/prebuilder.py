#raise NotImplementedError("RHEL and Fedora are not yet implemented")
import re
import typing

__all__ = ("RPMBased",)
from ClassDictMeta import OrderedClassDictMeta
from FHS import FHS, Common
from File2Package import File2Package

from ...core.Distro import Distro
from ...core.NamingPolicy import Meta, Prefix, PrefixSuffix, Rest, Rx, Suffix
from ...core.Package import VersionedPackageRef
from ...extractors import ExtractedInfo
from ...namingPolicies import universalNamingPolicy
from ...tearers.FHSTearer import FHSTearer
from ...tools.pkgconfig import PyPKGResolver
from .. import nativeDistro


class FedoraConventions(Common):
	python2LibsDir = FHS.usr.lib / "python"
	python3LibsDir = FHS.usr.lib / "python3"


class redHatNamingPolicy(metaclass=OrderedClassDictMeta):
	python2 = Prefix("python2-")

	lua = Prefix("liblua-")
	lua_dev = Prefix("liblua-devel-")

	ocaml = Suffix("ocaml-")
	ocaml_dev = PrefixSuffix("ocaml-", "-devel")

	golang = Prefix("golang-")
	rust = PrefixSuffix("rust-", "-devel")

	perl = PrefixSuffix("lib", "-perl")
	emacs = Prefix("emacs-")

	dev = PrefixSuffix("lib", "-devel")


redHatNamingPolicy.update(universalNamingPolicy)


def decodeAnotherPackageRefIntoStr(distro: Distro, ref: typing.Union[VersionedPackageRef, str]) -> str:
	if isinstance(ref, VersionedPackageRef):
		decodedRef = distro.decodeRef(ref)
		res = decodedRef.name
		if isinstance(ref, VersionedPackageRef):
			res += " >=" + str(decodedRef.version)
		return res
	else:
		return ref


archsRemap = {
	64: {
		"EM_X86_64": "amd64",
		"EM_AARCH64": "arm64",
	},
	32: {
		"EM_X86_64": "x32",
		"EM_386": "i386",
	},
}

specialArchs = {
	"all": "all",
	"any": "any",
}

osABIRemap = {
	"ELFOSABI_SYSV": "",
	"ELFOSABI_LINUX": "",
}


def archTransformer(extractedInfo: ExtractedInfo) -> str:
	if not isinstance(extractedInfo, str):
		return osABIRemap[extractedInfo.OSABI] + archsRemap[extractedInfo.bitness][extractedInfo.arch]
	else:
		return specialArchs[extractedInfo]


RPMBased = Distro("Fedora", FedoraConventions, FHSTearer, redHatNamingPolicy, None, None, archTransformer, None, decodeAnotherPackageRefIntoStr)
