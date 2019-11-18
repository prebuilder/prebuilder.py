from .ninja import *
from pathlib import Path
from ..styles import styles
from . import fj


def make(*rules, _cwd: Path, useKati: bool = False, firejailCfg=(), **kwargs):
	firejailCfgKati = type(firejailCfg)(firejailCfg)
	firejailCfgKati["apparmor"] = True
	firejailCfgKati["network"] = False
	cfjCkati = getCfj(_cwd=_cwd, **firejailCfgKati)
	cfjMake = getCfj(_cwd=_cwd, **firejailCfg)
	try:
		ckati = cfjCkati.ckati.bake("--ninja", "--color_warnings", "--detect_depfiles")  # --gen_all_targets
	except BaseException:
		ckati = False

	if ckati and useKati:
		try:
			print("Trying to " + styles.operationName("convert to " + styles.entity("ninja")) + " using " + styles.entity("kati") + "...")
			ckati(*rules, _cwd=_cwd, **kwargs)
			katiOk = True
			print(styles.success("Success!"))
		except Exception as ex:
			katiOk = False
			print(styles.error("Fail!"))
			print(ex.stdout.decode("utf-8"))
			print(ex.stderr.decode("utf-8"))
			print(ex)
	else:
		katiOk = False

	try:
		if katiOk:
			print(styles.operationName("Building") + " with " + styles.entity("ninja") + "...")
			ninja(_cwd=_cwd, firejailCfg=firejailCfg)
		else:
			print(styles.operationName("Building") + " with " + styles.entity("GNU Make") + "...")
			cfjMake.make(*rules, _cwd=_cwd, **kwargs)
	except Exception as ex:
		print(ex.stdout.decode("utf-8"))
		print(ex.stderr.decode("utf-8"))
		raise
