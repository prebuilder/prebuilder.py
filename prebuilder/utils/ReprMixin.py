import typing


class ReprMixin:
	__slots__ = ()
	constructable = True

	def __repr__(self):
		if self.__class__.constructable:
			op, cl = "()"
		else:
			op, cl = "<>"
		return "".join((self.__class__.__name__, op, ", ".join(repr(getattr(self, k)) for k in self.__class__.__slots__), cl))
