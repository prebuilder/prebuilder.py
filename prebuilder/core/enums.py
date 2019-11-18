from enum import IntFlag


class CleanBuild(IntFlag):
	repos = 1
	sources = 2
	builtTmpDir = 4
	packagesRoots = 8
	downloadsTmpDir = 16
	all = 0x1F
