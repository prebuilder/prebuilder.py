import sh

dpkgSig = sh.Command("dpkg-sig").bake(s="builder", _fg=True)
