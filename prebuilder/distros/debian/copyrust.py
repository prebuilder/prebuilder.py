import typing

currentVersionURI = "https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/"


class License:
	__slots__ = ("spdx", "text")

	def __init__(self, spdx, text: str = None, fetch: bool = False):
		self.spdx = spdx
		self.text = text
		if fetch:
			raise NotImplementedError("Fetching not yet implemented")


class Copyright:
	__slots__ = ("years", "holder")

	def __init__(self, years: typing.Union[int, (int, int)], holder: "Person"):
		self.years = years
		self.holder = holder


class CopyrightRecord:
	__slots__ = ("files", "copyrights", "license")

	def __init__(self, files: typing.Iterable[Path, str], copyrights: typing.Iterable[Copyright], license: typing.Union[License, str]):
		self.files = files
		self.copyrights = copyrights
		self.license = license


class CopyrightFile:
	__slots__ = ("format", "upstreamName", "upstreamContact", "source", "disclaimer", "comment", "records")

	def __init__(self, upstreamName, source, upstreamContact=None, comment=None, records=None):
		self.format = currentVersionURI
		self.upstreamName = upstreamName
		self.upstreamContact = upstreamContact
		self.source = source
		self.disclaimer = disclaimer
		self.comment = comment
		self.records = []


class Copyrust:
	__slots__ = ("file", "tree", "licenses")

	def __init__(self, upstreamName, source, upstreamContact=None, comment=None, records=None):
		self.file = CopyrightFile(upstreamName, source, upstreamContact, comment, records)
		self.tree = tree
		self.licenses = {}

	def __iadd__(self, lic):
		pass
