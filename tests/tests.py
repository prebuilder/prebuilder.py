#!/usr/bin/env python3
import sys
from pathlib import Path
import unittest
from collections import OrderedDict
from tempfile import TemporaryDirectory
from shutil import rmtree


thisFile = Path(__file__).absolute()
thisDir = thisFile.parent.absolute()
repoMainDir = thisDir.parent.absolute()
sys.path.append(str(repoMainDir))


dict = OrderedDict


from prebuilder.tearers.FHSTearer import FHSTearer
from prebuilder.core.Package import VersionedPackageRef
from prebuilder.webServices import detectService, _detectService
from prebuilder.webServices.services import *


@unittest.skip
class TestTearer(unittest.TestCase):
	def setUp(self):
		self.testPkgDirO = TemporaryDirectory(suffix=None, prefix=None, dir=None)
		self.testPkgDir = Path(self.testPkgDirO.__enter__())
	
	def tearDown(self):
		self.testPkgDirO.__exit__(None, None, None)
	
	def testTearer(self):
		testFileVirtualPath = Path("/usr/share/locale/cmn")
		testFilePath = nestPath(self.testPkgDir, testFileVirtualPath)
		testFilePath.parent.mkdir(parents=True, exist_ok=True)
		testFilePath.write_text("")
		
		#print(list(self.testPkgDir.glob("**/*")))
		res = FHSTearer(self.testPkgDir)
		self.assertEqual(res['data'], [testFileVirtualPath])


class TestWebServicesDetectors(unittest.TestCase):
	def testDetectors(self):
		table = (
			("https://github.com/rpm-software-management/rpm", (GitHubService, {"owner": "rpm-software-management", "repo": "rpm"})),
			("https://gitlab.com/dslackw/colored", (GitLabService, {"serviceBase": "gitlab.com", "repoPath": "dslackw/colored"})),
			("https://gitlab.gnome.org/GNOME/gimp", (GitLabService, {"serviceBase": "gitlab.gnome.org", "repoPath": "GNOME/gimp"})),
			("https://gitlab.freedesktop.org/mesa/mesa", (GitLabService, {"serviceBase": "gitlab.freedesktop.org", "repoPath": "mesa/mesa"})),
			("https://salsa.debian.org/pkg-rpm-team/rpm", (GitLabService, {"serviceBase": "salsa.debian.org", "repoPath": "pkg-rpm-team/rpm"})),
			("https://git.launchpad.net/~pythoneers/+git/distlib", (LaunchpadService, {"owner": "pythoneers", 'project': None, "repo": "distlib", "vcs": "git"})), # todo
			("https://bitbucket.org/ruamel/yaml", (BitBucketService, {"owner": "ruamel", "repo": "yaml"})),
		)
		for (uri, (correctService, correctArgs)) in table:
			with self.subTest(uri=uri, correctService=correctService, correctArgs=correctArgs):
				detectOther = False
				with self.subTest(func="_detectService"):
					serviceClass, ctorArgs = _detectService(uri)
					self.assertTrue(issubclass(serviceClass, correctService))
					self.assertEqual(ctorArgs, correctArgs)
					detectOther = True
				
				if detectOther:
					with self.subTest(func="detectService"):
						res = detectService(uri)
						self.assertIsInstance(res, correctService)



if __name__ == '__main__':
	unittest.main()
