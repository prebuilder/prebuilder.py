if __name__ == "__main__":
	import sys
	from pprint import pprint

	pprint(parseDebhelperDebianDir(Path(sys.argv[1])))
