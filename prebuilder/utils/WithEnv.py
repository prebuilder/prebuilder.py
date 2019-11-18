import os


class WithEnv:
	__slots__ = ("patch", "backup")

	def __init__(self, **kwargs):
		self.patch = kwargs
		self.backup = None

	def __enter__(self):
		self.backup = os.environ.copy()
		os.environ.update(self.patch)
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		os.environ = self.backup
