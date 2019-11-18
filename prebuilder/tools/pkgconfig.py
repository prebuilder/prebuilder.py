import re
import sys
import pykg_config
from pathlib import Path

from pykg_config.result import PkgCfgResult, parse_package_spec_list
from pykg_config.pkgsearcher import Package, PkgSearcher, PackageNotFoundError
import os


class PyPKGResolver():
	globalz = {
		'pc_sysrootdir': None
	}
	def __init__(self, distroFile2PackageResolver):
		self.distroFile2PackageResolver = distroFile2PackageResolver
		self.r = PkgCfgResult(self.globalz)
	
	def __call__(self, pkg2Find):
		dep = parse_package_spec_list(pkg2Find)[0]
		try:
			pkg = self.r.searcher.search_for_package(dep, self.globalz)
		except PackageNotFoundError:
			return None
		
		#pkg.properties["version"]
		#pkg.properties["description"]
		print(pkg.properties)
		ress = []
		props = (("libpaths", "libs", lambda nm: "lib"+nm+".so"),)
		with self.distroFile2PackageResolver as r:
			for dN, lNN, mapper in props:
				if lNN:
					lns = pkg.properties[lNN]
				else:
					lns = None
				if lns or lNN is None:
					for d in pkg.properties[dN]:
						d = Path(d)
						if lns:
							for ln in lns:
								if mapper:
									ln = mapper(ln)
								lp = d / ln
								print(lp)
								if lp.exists():
									yield r[lp]
						else:
							yield r[d]
