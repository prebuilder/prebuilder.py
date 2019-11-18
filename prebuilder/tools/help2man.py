from pathlib import Path

import sh

help2manCmd = sh.Command("help2man")


def help2man(binFile: Path, **kwargs):
	proc = help2manCmd(binFile, **kwargs)
	return proc.stdout.decode("utf-8")
