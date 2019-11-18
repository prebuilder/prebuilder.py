import typing
from abc import abstractmethod, ABC
from collections import defaultdict, OrderedDict
from os import linesep
from pathlib import Path
from hashlib import md5, sha256, sha512, blake2b, sha3_512
try:
	from hashlib import blake3
except ImportError:
	blake3 = None

from fsutilz import nestPath
from fetchers.utils.integrity import sumFile
from FHS import FHS


fsRoot = Path("/")


class FilesTracker:
	__slots__ = ("hashsums", "symlinks", "dirs")
	hashfuncs = (md5, sha256, sha512, blake2b, sha3_512)
	if blake3:
		hashfuncs += (blake3,)
	
	funcNames = tuple(hashFunc().name for hashFunc in hashfuncs)

	def __init__(self) -> None:
		self.hashsums = defaultdict(OrderedDict)
		self.symlinks = []
		#self.dirs = {}

	#def registerParents(self, p):
	#	dotPath = Path(".")
	#	if p.is_dir():
	#		self.dirs.add(p)
	#	while p:
	#		p = p.parent()
	#		self.dirs.add(p)
	#		if p == dotPath:
	#			break


	def registerPath(self, resPath: Path, rootPath: Path, hashes: typing.Optional[typing.Mapping[Path, typing.Mapping[str, str]]] = None) -> None:
		"""
		`hashes` is a dict of hashes (like `self.hashsums`) to update the dict of hashses without recomputing hashsums
		"""
		
		files = []
		symlinks = []
		fileIsDir = resPath.is_dir()
		if fileIsDir:
			for f in resPath.glob("**/*"):
				if f.is_symlink():
					symlinks.append(f)
				elif f.is_file():
					files.append(f)
		else:
			if resPath.is_symlink():
				symlinks.append(resPath)
			else:
				files = [resPath]

		#print(files)
		for s in symlinks:
			rS = s.relative_to(rootPath)
			self.symlinks.append(nestPath(fsRoot, rS))
			#self.registerParents(rS)

		if hashes is None:
			for f in files:
				rF = f.relative_to(rootPath)
				#self.registerParents(rF)
				hashes = sumFile(f, self.hashfuncs)
				absP = nestPath(fsRoot, rF)
				self.hashsums[absP] = hashes
				#print("self.hashsums["+repr(hashFuncName)+"]["+repr(str(f.relative_to(rootPath)))+"]", resPath)
		else:
			self.hashsums.update(hashes)
			#for p in hashses:
			#	self.registerParents(Path(p))

	@property
	def files(self) -> None:
		#print("self.hashsums.keys()", list(self.hashsums.keys()))
		yield from self.hashsums.keys()

	@property
	def filesAndSymlinks(self) -> None:
		yield from self.files
		yield from self.symlinks
	
	#def filesAndSymlinksAndDirs(self):
	#	yield from self.filesAndSymlinks

	def createHashDataPerHashFunc(self) -> typing.Iterator[typing.Tuple[str, typing.Iterator[typing.Any]]]:
		hashesSorted = sorted(self.hashsums.items(), key=lambda x: x[0])
		for i, hashName in enumerate(self.funcNames):

			def hashesGen():
				for filePath, fileHashes in hashesSorted:
					yield (filePath, fileHashes[i])

			hashesGen.__name__ = hashName + "_hashesGen"
			yield (hashName, hashesGen())


class HashesSerializer(ABC):
	@classmethod
	@abstractmethod
	def createSumsFileLines(cls, hashes):
		raise NotImplementedError()

	@classmethod
	@abstractmethod
	def createSumsFile(cls, sumsF: Path, hashes):
		raise NotImplementedError()

	@classmethod
	@abstractmethod
	def createSumsMetadata(cls, filesTracker: FilesTracker, outputDir: Path):
		raise NotImplementedError()


class TextLinesHashesSerializer(HashesSerializer):
	@classmethod
	def createSumsFile(cls, sumsF: Path, hashes: typing.Iterator[typing.Any]) -> None:
		with sumsF.open("wt") as f:
			f.writelines(cls.createSumsFileLines(hashes))
