import typing
import re

__all__ = ("Debian",)

from ...core.Package import PackageRef, VersionedPackageRef
from ...core.Distro import Distro
from ...core.NamingPolicy import PrefixSuffix, Prefix, Suffix, Meta, Rx, Rest
from ...extractors import ExtractedInfo
from ...namingPolicies import universalNamingPolicy

from .Repo import DebRepo
from .AptDpkg import AptDpkg
from .BuiltPackage import DebBuiltPackage

from FHS import FHS, Common
from ...tearers.FHSTearer import FHSTearer
from ClassDictMeta import OrderedClassDictMeta

from File2Package import File2Package


javaFlavours = {
	"graalvm": lambda javaVersion: "graalvm-ce-" + str(version) + "-" + arch,
	"openjdk": lambda javaVersion: "java-" + str(version) + "-openjdk-" + arch
}


class DebianConventions(Common):
	docCommonLocation = FHS.usr.share.doc

	@classmethod
	def copyrightLocation(cls, pkgRef: str):
		return cls.docCommonLocation / pkgRef.name / "copyright"

	@classmethod
	def changelogLocation(cls, pkgRef: VersionedPackageRef):
		return cls.docCommonLocation / pkgRef.name / "NEWS.gz"

	javaRuntimes = FHS.usr.lib / "jvm"
	javaClasspath = FHS.usr.share / "java"
	javaGcj = FHS.usr.lib / "gcj"
	javaJNILibs = FHS.usr.lib / "jni"
	javaDefaultRuntime = javaRuntimes / "default-java"

	jsLibsDir = FHS.usr.share / "javascript"

	python2LibsDir = FHS.usr.lib / "python"
	python3LibsDir = FHS.usr.lib / "python3"

	fontsGeneral = FHS.usr.share / "fonts"
	fontsTTF = fontsGeneral / "truetype"
	fontsOTF = fontsGeneral / "opentype"
	TexMF = FHS.usr.share / "texmf"

	@classmethod
	def jvmLocation(cls, pkgRef: VersionedPackageRef, arch="amd64", flavour="openjdk"):
		return cls.javaRuntimes / javaFlavours[flavour](pkgRef.version[0])

	@classmethod
	def javaLibLocation(cls, pkgRef: VersionedPackageRef):
		return cls.javaClasspath / pkgRef.name

	@classmethod
	def javaLibDocLocation(cls, pkgRef: VersionedPackageRef):
		pkgDocLoc = cls.docCommonLocation / pkgRef.name / "api"
		# or pkgDocLoc /api-<component>/.
		return pkgDocLoc


def rustNameGen(ref: VersionedPackageRef, featureName=""):
	versionStr = str(ref.version[0])
	if ref.version[0] == 0:
		for versionDigit in ref.version[1:]:
			versionStr += "." + str(versionDigit[0])
			if versionDigit != 0:
				break

	return "librust-" + ref.name + "-" + versionStr + ("-" + featureName if featureName else "") + "-dev"

class debianNamingPolicy(metaclass=OrderedClassDictMeta):
	lua = Prefix("lua-")
	lua_dev = PrefixSuffix("lua-", "-dev")

	ocaml = Suffix("-ocaml")
	ocaml_dev = Suffix("-ocaml-dev")

	perl = PrefixSuffix("lib", "-perl")
	java = PrefixSuffix("lib", "-java")
	javascript = Prefix("libjs-")
	cLisp = Prefix("clisp-module-")

	golang = PrefixSuffix("golang-gopkg-", "-dev")
	
	bash_completion = Suffix("-bash-completion")
	zsh = Prefix("zsh-")
	vim = Prefix("vim-")
	emacs = Suffix("-emacs")

	rust = Rx("^librust-(?:([^+]+)(?:\\+(.+))?|([^-]+)(?:-(.+))?)-dev$", rustNameGen)
	
	dev = PrefixSuffix("lib", "-dev")

debianNamingPolicy.update(universalNamingPolicy)
debianNamingPolicy["python2"] = Prefix("python-")
debianNamingPolicy["python3"] = Prefix("python3-")


def decodeAnotherPackageRefIntoStr(distro: Distro, ref: typing.Union[VersionedPackageRef, str]) -> str:
	if isinstance(ref, PackageRef):
		decodedRef = distro.decodeRef(ref)
		res = decodedRef.name
		if isinstance(ref, VersionedPackageRef):
			res += ("(>=" + str(decodedRef.version) + ")")
		return res
	else:
		return ref


archsRemap = {
	64:{
		"EM_X86_64": "amd64",
		"EM_AARCH64": "arm64",
		"EM_PPC64": "ppc64el",
		"EM_RISCV": "riscv64",
		11: "sparc64",
	},
	32:{
		"EM_X86_64": "x32",
		"EM_386": "i386",
		"EM_AVR32": "AVR32",
		"EM_M32R": "m32",
		"EM_IAMCU": "i686",
		"EM_ARM": "armhf",
		"EM_MIPS": "mips",
		"EM_ALPHA": "alpha",
		"EM_SPARC": "sparc",

		"EM_SPARC32PLUS": "sparc",
		"EM_S390": "s390x",
		"EM_OPENRISC": "or1k",
		"EM_68K": "m68k",
		"EM_SH": "sh4"
	}
}

specialArchs = {
	"all" : "all",
	"any" : "any",
}

osABIRemap = {
	"ELFOSABI_SYSV": "",
	"ELFOSABI_LINUX": "",
	"ELFOSABI_HURD": "hurd-",
	"ELFOSABI_FREEBSD": "kfreebsd-",
	"ELFOSABI_NETBSD": "netbsd-",
}

def archTransformer(extractedInfo: ExtractedInfo) -> str:
	if not isinstance(extractedInfo, str):
		return osABIRemap[extractedInfo.OSABI] + archsRemap[extractedInfo.bitness][extractedInfo.arch]
	else:
		return specialArchs[extractedInfo]



Debian = Distro("Debian", DebianConventions, FHSTearer, debianNamingPolicy, DebBuiltPackage, AptDpkg(), archTransformer, DebRepo, decodeAnotherPackageRefIntoStr)
