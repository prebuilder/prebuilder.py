from pathlib import Path
import os

import sh
from datetime import datetime

class DeterministicTimestamps:
	__slots__ = ("ts", "prevTs", "prevZeroArDate")

	def __init__(self, ts: float) -> None:
		if isinstance(ts, datetime):
			ts = round(ts.timestamp())
		self.ts = int(ts)
		self.prevTs = None
		self.prevZeroArDate = None

	def __enter__(self) -> "DeterministicTimestamps":
		self.prevTs = os.environ.get("SOURCE_DATE_EPOCH")
		self.prevZeroArDate = os.environ.get("ZERO_AR_DATE")
		os.environ["SOURCE_DATE_EPOCH"] = str(self.ts)
		os.environ["ZERO_AR_DATE"] = "1"
		return self

	def __exit__(self, *args, **kwargs) -> None:
		if self.prevTs is not None:
			os.environ["SOURCE_DATE_EPOCH"] = self.prevTs
		else:
			del os.environ["SOURCE_DATE_EPOCH"]
		if self.prevZeroArDate is not None:
			os.environ["ZERO_AR_DATE"] = self.prevZeroArDate
		else:
			del os.environ["ZERO_AR_DATE"]


stripNondeterminismCmd = sh.Command("strip-nondeterminism")


def stripNondeterminism(ts, files: Path):
	if isinstance(files, Path):
		if files.is_dir():
			files = list(files.glob("**/*"))
		else:
			files = [files]
	stripNondeterminismCmd.bake(timestamp=ts)(files)
