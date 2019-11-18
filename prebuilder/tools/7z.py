import sh


def sevenZArgsProcessor(args, kwargs):
	argz = []
	kwargz = {}
	for k, v in kwargs.items():
		if isinstance(v, bool):
			kwargz[k] = v
		else:
			argz.append("-" + k + str(v))
	argz.extend(args)
	return argz, kwargz


sevenZ = sh.Command("7z").bake(_arg_preprocess=sevenZArgsProcessor, _long_prefix="-", _long_sep=" ")
