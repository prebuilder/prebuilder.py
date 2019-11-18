import sh
import sh.contrib
from . import fj, getCfj


from sh import RunningCommand
def ninja(*args, _cwd=None, firejailCfg=None, **kwargs) -> RunningCommand:
	cfj = getCfj(_cwd=_cwd, **firejailCfg)
	#print(cfj.realpath(".", _cwd=_cwd).stdout.decode("utf-8"))
	try:
		return cfj.ninja(*args, _cwd=_cwd, v=True, **kwargs)
	except Exception as ex:
		print("STDOut", ex.stdout.decode("utf-8"))
		print("STDErr:", ex.stderr.decode("utf-8"))
		raise
