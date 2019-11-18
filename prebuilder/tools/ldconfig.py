import typing
from pathlib import Path
import sh
import re
from collections import defaultdict

from pathlib import PosixPath

__all__ = ("ldconfigCache", "commonLibDirs")

ldconfig = sh.Command("ldconfig")

ldconfigCacheRx = re.compile("^\\s*(.+) \\(.+?\\) => (.+)\\s*$")


def getLdconfigCache() -> defaultdict:
	res = defaultdict(list)
	for l in ldconfig("-p", _env={"LANG": "C"}).stdout.decode("utf-8").splitlines():
		m = ldconfigCacheRx.match(l)
		if m:
			k, v = m.groups()
			res[k].append(Path(v))
			pass
		else:
			#print(l)
			pass
	return res


ldconfigCache = getLdconfigCache()


def heuristicallyDetectCommonLibsDirs(treshold: int = 5) -> typing.Iterable[PosixPath]:
	dirs = defaultdict(int)
	for ps in ldconfigCache.values():
		for p in ps:
			dirs[p.parent] += 1
	return tuple(k for k, v in sorted(dirs.items(), key=lambda x: x[1]) if v >= treshold)


commonLibDirs = heuristicallyDetectCommonLibsDirs(2)
