import typing
from pathlib import PurePosixPath, Path
from os.path import sep

class VPath(PurePosixPath):
	__slots__ = ("_is_dir",)
	
	def __new__(cls, *args, **kwargs):
		res = super().__new__(cls, *args, **kwargs)
		if isinstance(args[-1], str):
			res._is_dir = args[-1][-1] == sep
		elif isinstance(args[-1], (Path, __class__)):
			res._is_dir = args[-1].is_dir()
		else:
			res._is_dir = None
		return res
	
	def is_dir(self):
		return self._is_dir
	
	def is_file(self):
		return not self._is_dir
