import typing
import sh
from . import fj, getCfj

#from .gpg import gnupgDir


def getRepreproCmds(*paths, _cwd) -> typing.Mapping[str, sh.Command]:
	cfj = getCfj(paths=paths, _cwd=_cwd)
	#cfjGpg = getCfj(gnupgDir, *paths, _cwd=_cwd)

	repreproCmd = cfj.reprepro.bake(v=True, _fg=True)
	#repreproGpgCmd = cfjGpg.reprepro.bake(v=True, _fg=True)
	repreproGpgCmd = sh.reprepro.bake(v=True, _fg=True)
	return {
		"includeDeb": repreproGpgCmd.includedeb,
		"removePackage": repreproCmd.remove,
		"export": repreproGpgCmd.export,
		"createSymlinks": repreproCmd.createsymlinks,
	}
