__all__ = ("nativeDistro",)
from importlib import import_module

try:
	from platform import linux_distribution
	def get_distro():
		return linux_distribution()[0]
except ImportError:
	from lsb_release import get_distro_information
	def get_distro():
		info = get_distro_information()
		return info["ID"]


distrosRemap = {
	"Ubuntu": ("debian", "Debian"),
	"Debian": ("debian", "Debian"),
	"Fedora": ("rpm_based", "RPMBased"),
}

def getNativeDistro():
	distro = get_distro()
	if distro in distrosRemap:
		pkgNm, clsNm = distrosRemap[distro]
		pkg = import_module("."+pkgNm, __spec__.name)
		res = getattr(pkg, clsNm)
		if hasattr(pkg, "nativeDistro") and pkg.nativeDistro is None:
			pkg.nativeDistro = res
		return res

nativeDistro = None # Dont' remove!!!
nativeDistro = getNativeDistro()
