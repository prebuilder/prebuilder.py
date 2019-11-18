import typing
from pathlib import Path
from collections import OrderedDict, defaultdict

from CMake import CMakeInterpreter

from ..distros.debian import Debian
from ..utils.ReprMixin import ReprMixin
from ClassDictMeta import ClassDictMeta

from ..distros.debian.utils import debianPackageRelationKwargs
from .debhelper import processDebControlList, stripVersionConditionFromPackageRelation


def getCPackPackageNameRegularExpression(buildDir: Path, name: str):
	return re.compile("^CPack: - package: (" + re.escape(str((buildDir / name).absolute())) + ".+\\.deb) generated\\.$")


def getCPackPackageNames(buildDir: Path, name: str, stdout: str):
	re = getCPackPackageNameRegularExpression(buildDir, name)
	for l in stdout.splitlines():
		m = re.match(l)
		if m:
			pkgPath = Path(m.group(1))
			if pkgPath.is_file():
				yield pkgPath


class CPackSpec(ReprMixin):
	__slots__ = ("id", "dic", "packagerSpecific")
	constructable = False

	def __init__(self):
		self.id = None
		self.dic = {}
		self.packagerSpecific = defaultdict(OrderedDict)

	def finalize(self):
		self.packagerSpecific = dict(self.packagerSpecific)


class CPackComponents(ReprMixin):
	__slots__ = ("main", "sub")
	constructable = False
	
	def __init__(self):
		self.main = CPackSpec()
		self.sub = defaultdict(CPackSpec)

	def finalize(self):
		self.main.finalize()
		for el in self.sub.values():
			el.finalize()
		self.sub = dict(self.sub)


class PackagerSpecificPostprocessor():
	distro = None
	def __call__(self, dic: typing.Mapping):
		raise NotImplementedError()

class DebianSpecificPostprocessor(PackagerSpecificPostprocessor):
	distro = Debian
	
	def __call__(self, dic: typing.Mapping):
		for n in debianPackageRelationKwargs:
			if n in dic:
				dic[n] = [self.__class__.distro.toPackageRefWithGroupResolved(stripVersionConditionFromPackageRelation(pn)) for pn in processDebControlList(dic[n])]

generatorRemap = {
	"DEBIAN": DebianSpecificPostprocessor(),
	#"RPM": "rpm",
}

namesRemaps = {
	"DESCRIPTION_SUMMARY": "descriptionShort",
	"VENDOR": "maintainer",
	"HOMEPAGE_URL": "homepage",
	"VERSION": "version",
	"NAME": "name"
}

namesInherited = ("version", "descriptionShort")


class namesConstructors(metaclass=ClassDictMeta):
	def homepage(packageProp):
		if "CONTACT" in packageProp and packageProp["CONTACT"].startswith("https://"):
			return packageProp["CONTACT"]


	def descriptionLong(packageProp):
		if "DESCRIPTION_FILE" in packageProp:
			return Path(packageProp["DESCRIPTION_FILE"]).read_text()


def cpackInterpreter(buildDir):
	cpackConfigPath = buildDir / "CPackConfig.cmake"

	cm = CMakeInterpreter()
	cm.interpret(cpackConfigPath)

	cpackConfig = cm.ns
	
	if "CPACK_COMPONENTS_ALL" in cpackConfig:
		componentsAll = cpackConfig["CPACK_COMPONENTS_ALL"].split(";")
	else:
		componentsAll = ()

	componentsMapping = {k.upper(): k for k in componentsAll}

	cpackMarker = "CPACK_"
	packagePropMarker = "PACKAGE_"
	componentPropMarker = "COMPONENT_"
	componentGeneratorSpecificPropMarker = "_PACKAGE"
	generatorSpecificNameSpaceKey = "$generator_specific"

	filtered = OrderedDict()
	
	res = CPackComponents()
	mainPackage = res.main
	components = res.sub
	

	for k, v in cpackConfig.items():
		namespace = filtered
		itWasDistroSpecific = False
		itWasComponentSpecific = False
		
		if k.startswith(cpackMarker):
			k = k[len(cpackMarker) :]
		if k.startswith(packagePropMarker):
			k = k[len(packagePropMarker) :]
			namespace = mainPackage.dic
		elif k.startswith(componentPropMarker):
			k = k[len(componentPropMarker) :]
			compNameEnd = k.find("_")
			compName = k[:compNameEnd]
			if compName in componentsMapping:
				compName = componentsMapping[compName]
				k = k[compNameEnd + 1 :]
				namespace = components[compName].dic
				itWasComponentSpecific = True
		else:
			for generatorCmakeName, postProcessor in generatorRemap.items():
				distro = postProcessor.distro
				if k.startswith(generatorCmakeName + "_"):
					k = k[len(generatorCmakeName) + 1 :]

					#generatorSpecificNameSpaceKey
					namespace = mainPackage.packagerSpecific[distro.builder.packageExtension]
					itWasDistroSpecific = True

					compNameEnd = k.find(componentGeneratorSpecificPropMarker)
					if compNameEnd > -1:
						compName = k[:compNameEnd]
						
						if compName in componentsMapping:
							compName = componentsMapping[compName]
							k = k[compNameEnd + 1 + len(componentGeneratorSpecificPropMarker) :]
							namespace = components[compName].packagerSpecific[distro.builder.packageExtension]
							itWasComponentSpecific = True
					break


		if k in namesRemaps:
			k = namesRemaps[k]
		namespace[k] = v

	mainPackage.id = filtered.get("CMAKE_INSTALL_DEFAULT_COMPONENT_NAME", "Unspecified")
	print("mainPackage.id", mainPackage.id)

	def processComponentDic(pkgDict, pn=None):
		for name in namesInherited:
			if name not in pkgDict and name in mainPackage.dic:
				pkgDict[name] = mainPackage.dic[name]

		for name, ctor in namesConstructors.items():
			print(name, name not in pkgDict)
			if name not in pkgDict:
				res = ctor(mainPackage.dic)
				if res:
					pkgDict[name] = res


		if "name" not in pkgDict:
			pkgDict["name"] = mainPackage.dic["name"].lower() + ("-" + pn.lower() if pn and pn != mainPackage.id else "")
	
	def processPackagerSpecificOfComponent(packagerSpecific):
		if packagerSpecific:
			for postProcessor in generatorRemap.values():
				ext = postProcessor.distro.builder.packageExtension
				if ext in packagerSpecific:
					postProcessor(packagerSpecific[ext])

	def processComponent(component, pn):
		processComponentDic(component.dic, pn)
		processPackagerSpecificOfComponent(component.packagerSpecific)
		if pn:
			component.id = pn


	processComponent(mainPackage, None)
	
	for pn, component in components.items():
		processComponent(component, pn)

	res.finalize()
	return res
