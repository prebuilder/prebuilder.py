__all__ = ("applyPatch", "gitPatch", "patchCmd")
from pathlib import Path
import warnings
try:
	import patch_ng as patch
except ImportError:
	import patch
	warnings.warn("patch_ng is not present, imported old broken and UNMAINTAINED `patch` by techtonik (the man is alive, but doesn't maintain)")

import sh
from MempipedPath import MempipedPathRead
from ..styles import styles

def _applyPatch_(patchFile: Path, root: Path = None):
	with patchFile.open("rb") as ps:
		p = patch.PatchSet(ps)
	res = p.apply(strip=0, root=root)
	if not res:
		raise Exception("Unable to apply patch!", patchFile, root)

def _applyPatch(patchFile: Path, root: Path = None):
	print(styles.operationName("Applying") + " " + styles.entity("patch") + " " + styles.varContent(patchFile) + " to " + styles.varContent(root))
	_applyPatch_(patchFile, root)

def applyPatch(patchFile: Path, root: Path = None):
	p = None
	if patchFile.is_dir():
		patchDir = patchFile
		seriesFile = patchDir / "series"
		if seriesFile.is_file():
			print(styles.operationName("Reading") + " " + styles.entity("series file"))
			for l in seriesFile.open("rt", encoding="utf-8"):
				if l:
					if l[-1] == "\n":
						l = l[:-1]
					patchFile = patchDir / l
					_applyPatch(patchFile, root)
		else:
			print(styles.error(styles.entity("Series file") + " is not present!"))
			for patchFile in sorted(patchDir.glob("*.patch")):
				_applyPatch(patchFile, root)
	else:
		_applyPatch(patchFile, root)


gitCmd = sh.git


def gitPatch(patchText: str, root: Path):
	with MempipedPathRead(patchText) as pipePath:
		gitCmd.apply(pipePath, **{"ignore-whitespace": True, "_cwd": root})


def patchCmd(patchText: str, fileToPatch: Path):
	sh.patch(fileToPatch, **{"ignore-whitespace": True, "_in": patchText})
