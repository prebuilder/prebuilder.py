import typing
import os


class Person:
	__slots__ = ("name", "email")

	def __init__(self, name: str, email: str) -> None:
		self.name = name
		self.email = email

	def __str__(self) -> str:
		res = self.name
		if res and self.email:
			res += " <" + self.email + ">"
		return res

	def __repr__(self):
		return str(self)


class Maintainer(Person):
	__slots__ = ()

	def __init__(self, name: typing.Optional[str] = None, email: typing.Optional[str] = None) -> None:
		if not name:
			name = os.environ.get("DEBFULLNAME", "Anonymous")

		if not email:
			email = os.environ.get("DEBEMAIL", None)

		super().__init__(name, email)
