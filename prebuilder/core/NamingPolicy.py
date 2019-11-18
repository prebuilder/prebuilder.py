import typing
from abc import abstractmethod, ABC
import re
from .Package import VersionedPackageRef


class NamingRule(ABC):
	@abstractmethod
	def match(self, name: str):
		raise NotImplementedError()

	@abstractmethod
	def gen(self, ref: VersionedPackageRef):
		raise NotImplementedError()


class RestClass(NamingRule):
	def match(self, name: str) -> str:
		return name

	def gen(self, ref: VersionedPackageRef) -> str:
		return ref.toName()


Rest = RestClass()


class Prefix(NamingRule):
	def __init__(self, pfx: str) -> None:
		self.pfx = pfx

	def match(self, name: str) -> typing.Optional[str]:
		if name.startswith(self.pfx):
			return name[len(self.pfx) :]

	def gen(self, ref: VersionedPackageRef):
		return "".join((self.pfx, ref.toName()))


class Suffix(NamingRule):
	__slots__ = ("sfx",)

	def __init__(self, sfx: str) -> None:
		self.sfx = sfx

	def match(self, name: str) -> typing.Optional[str]:
		if name.endswith(self.sfx):
			return name[: -len(self.sfx)]

	def gen(self, ref: VersionedPackageRef):
		return "".join((ref.toName(), self.sfx))


class PrefixSuffix(NamingRule):
	__slots__ = ("pfx", "sfx")

	def __init__(self, pfx: str, sfx: str) -> None:
		self.pfx = pfx
		self.sfx = sfx

	def match(self, name: str) -> typing.Optional[str]:
		if name.startswith(self.pfx) and name.endswith(self.sfx):
			return name[len(self.pfx) : -len(self.sfx)]

	def gen(self, ref: VersionedPackageRef):
		return "".join((self.pfx, ref.toName(), self.sfx))


class Meta(NamingRule):
	__slots__ = ("rules",)

	def __init__(self, *rules) -> None:
		self.rules = rules

	def match(self, name: str) -> typing.Optional[str]:
		for r in self.rules:
			res = r.match(name)
			if res:
				return res

	def gen(self, ref: VersionedPackageRef):
		return self.rules[0].gen(ref)


class Rx(NamingRule):
	__slots__ = ("rx", "group", "genFunc")

	def __init__(self, rx: typing.Union[re.Pattern, str], genFunc: callable, group: int = 1) -> None:
		if isinstance(rx, str):
			rx = re.compile(rx)
		self.rx = rx
		self.group = group

	def match(self, name: str) -> typing.Optional[str]:
		m = self.rx.match(name)
		if m:
			return m.group(self.group)

	def gen(self, ref: VersionedPackageRef):
		return self.genFunc(ref)


class Func(NamingRule):
	__slots__ = ("match", "gen")

	def __init__(self, match, gen):
		self.gen = gen
		self.match = match
