import typing
from ..core.NamingPolicy import PrefixSuffix, Prefix, Suffix, Meta, Rx, Rest

from ClassDictMeta import OrderedClassDictMeta

class universalNamingPolicy(metaclass=OrderedClassDictMeta):
	python3 = Meta(Prefix("python3-"), Prefix("python-"))
	python2 = Prefix("python2-")
	vim = Prefix("vim-")
	
	libs = Prefix("lib")
	docs = Suffix("-doc")
	sources = Suffix("-src")
	data = Suffix("-data")
	locales = Meta(Suffix("-locales"), Suffix("-locale"), Suffix("-i18n"))
	tools = Rest
