import typing
from pathlib import Path
import os
import sh
from warnings import warn

from fsutilz import isNestedIn

from MempipedPath import currentProcFileDescriptors

from sh import Command
fj = sh.firejail.bake("--caps.drop=all", "--private-dev", "--disable-mnt", "--ipc-namespace", "--machine-id", noblacklist=str(currentProcFileDescriptors))  # x11="none", private=True


def getCfj(paths=None, _cwd=None, whitelistMode=False, network=False, seccomp=True, apparmor=True, noautopulse=True, nodbus=True, nodvd=True, no3d=True, nou2f=True, notv=True, novideo=True, nosound=True, nonewprivs=True, disable=False) -> Command:
	"""`_allowedDirs` is set via a dict,"""
	if disable == True:
		warn("Firejail isolation disabled!!!")
		return sh
	
	
	dirz = set()
	if _cwd:
		dirz |= {_cwd}
	
	def addPath(p):
		nonlocal dirz
		skip = False
		for pp in dirz:
			if isNestedIn(pp, p):
				skip = True
		if skip:
			return
		if not p.is_dir():
			p = p.parent
		dirz |= {p}

	for p in paths:
		assert isinstance(p, Path)
		addPath(p)

	ro = set()
	rw = set()
	for p in dirz:
		ro |= {p.parent}
		rw |= {p}
	ro -= rw

	argz = []
	for p in ro:
		if whitelistMode:
			argz.extend(("--whitelist=" + str(p),))
		else:
			argz.extend(("--noblacklist=" + str(p),))
		argz.extend(("--read-only=" + str(p),))

	for p in rw:
		if whitelistMode:
			argz.extend(("--whitelist=" + str(p),))
		else:
			argz.extend(("--noblacklist=" + str(p),))
		argz.extend(("--read-write=" + str(p),))

	if _cwd:
		argz.append("--private-cwd=" + str(_cwd))

	if not network:
		argz.append("--net=none")

	argz.append("--quiet")

	#print(argz)

	return fj.bake(*argz, seccomp=seccomp, apparmor=apparmor, noautopulse=noautopulse, nodbus=nodbus, nodvd=nodvd, no3d=no3d, nou2f=nou2f, notv=notv, novideo=novideo, nosound=nosound, nonewprivs=nonewprivs)
