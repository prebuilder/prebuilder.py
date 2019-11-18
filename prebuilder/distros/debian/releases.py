import typing
from collections import OrderedDict
from datetime import datetime
from ...core.Distro import CodenamedDistroRelease


class DebianRelease(CodenamedDistroRelease):
	"""None `time` means not yet released"""

	__slots__ = ("codenames",)
	origin = "Debian"

	def __init__(self, version: typing.Tuple[int, int] = (9, 0), time: datetime = None, codenames: typing.Iterable[str] = ("stretch", "stable")) -> None:
		self.codenames = codenames
		self.version = version
		if isinstance(time, tuple):
			time = datetime(*time)
		self.time = time

	@property
	def suite(self) -> str:
		return self.codenames[-1]


class UbuntuRelease(DebianRelease):
	origin = "Ubuntu"

	def __init__(self, version: typing.Tuple[int, int] = (20, 4), time: datetime = None, codenames: typing.Iterable[str] = ("focal",)) -> None:
		if time is None:
			time = (2000 + version[0], version[1], 20)
		super().__init__(version, time, codenames)


class MintRelease(DebianRelease):
	origin = "Mint"

knownReleases = OrderedDict((
	("Mint", (
		MintRelease((20, 0), (2020, 6, 27), ("ulyana",)),
		MintRelease((19, 3), (2019, 12, 18), ("tricia",)),
		MintRelease((19, 2), (2019, 8, 2), ("tina",)),
		MintRelease((19, 1), (2018, 12, 19), ("tessa",)),
		MintRelease((19, 0), (2018, 6, 29), ("tara",)),
	
		MintRelease((18, 3), (2017, 11, 27), ("sylvia",)),
		MintRelease((18, 2), (2017, 7, 2), ("sonya",)),
		MintRelease((18, 1), (2016, 12, 16), ("serena",)),
		MintRelease((18, 0), (2016, 6, 30), ("sarah",)),
	)),
	("Ubuntu", (
		UbuntuRelease((20, 10), (2020, 10, 22), ("groovy",)),
		UbuntuRelease((20, 4), (2020, 4, 23), ("focal",)),
		UbuntuRelease((19, 10), (2019, 10, 17), ("eoan",)),
		UbuntuRelease((19, 4), (2019, 4, 18), ("disco",)),
		UbuntuRelease((18, 10), (2018, 10, 18), ("cosmic",)),
		UbuntuRelease((18, 4), (2018, 4, 26), ("bionic",)),
		UbuntuRelease((17, 10), (2017, 10, 19), ("artful",)),
		UbuntuRelease((17, 4), (2017, 4, 13), ("zesty",)),
		UbuntuRelease((16, 10), (2016, 10, 13), ("yakkety",)),
		UbuntuRelease((16, 4), (2016, 4, 21), ("xenial",))
	)),
	("Debian", (
		DebianRelease((12, 0), None, ("bookworm",)),
		DebianRelease((11, 0), None, ("sid", "unstable")),
		DebianRelease((11, 0), None, ("bullseye", "testing")),
		DebianRelease((10, 0), (2019, 7, 6), ("buster", "stable")),
		DebianRelease((9, 0), (2017, 6, 17), ("stretch", "oldstable")),
		DebianRelease((8, 0), (2015, 4, 26), ("jessie", "oldoldstable")),
		DebianRelease((7, 0), (2013, 5, 4), ("wheezy", "oldoldoldstable"))
	))
))
