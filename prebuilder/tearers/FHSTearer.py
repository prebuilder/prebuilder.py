import typing
from FHS import FHS, Common
from ..core.Tearer import Splitter, Classifier, Tearer
from pathlib import Path, PurePath


# (matchers, component)
FHSSplitters = (
	Splitter((
		Classifier((FHS.bin, FHS.usr.bin, FHS.usr.bin, FHS.usr.libexec, Common.applications, Common.icons, Common.mime),),
		Classifier((FHS.lib, FHS.usr.lib), "\\.(sh)$")
	), "tools"),
	Splitter(Classifier((FHS.usr.lib,), ("^python(2(\\.\\d+)*)?$"), isDir = True), "python2",),
	Splitter(Classifier((FHS.usr.lib,), ("^python3(\\.\\d+)*$"), isDir = True), "python3",),
	Splitter((
		Classifier((FHS.usr.lib,), ("\\.pl", "\\.perl$")),
		Classifier((FHS.usr.share / "perl5",)),
	), "perl",),
	Splitter((
		Classifier((FHS.usr.lib / "lua",)),
	), "lua",),
	Splitter((
		Classifier((FHS.usr.include,), ("^lua(5(\\.\\d+)*)?$"), isDir = True),
		Classifier((FHS.usr.lib, ), "^liblua.+\\.(a|cmake|la)$"),
	), "lua_dev",),
	Splitter((
		Classifier((FHS.usr.share / "bash-completion",)),
	), "bash_completion",),
	Splitter((
		Classifier((FHS.usr.share / "vim" / "addons",)),
	), "vim",),
	Splitter((
		Classifier((FHS.usr.share / "zsh",)),
	), "zsh",),
	Splitter((
		Classifier((FHS.usr.lib / "emacsen-common" / "packages",)),
		Classifier((FHS.usr.share / "emacs" / "site-lisp",)),
	), "emacs",),
	Splitter((
		Classifier((FHS.usr.lib / "ocaml",), ("\\.so(\\.\\d+)*$")),
	), "ocaml",),
	Splitter((
		Classifier((FHS.usr.share / "gocode" / "src" / "gopkg.in",)),
	), "golang",),
	Splitter((
		Classifier((FHS.usr.lib / "ocaml",)),
	), "ocaml_dev",),
	Splitter((
		Classifier((FHS.usr.lib,), ("^clisp-(\\d+(\\.\\d+)+)$"), isDir = True),
	), "cLisp",),
	Splitter((
		Classifier((FHS.usr.share / "cargo",)),
	), "rust",),
	Splitter((
		Classifier(FHS.usr.include),
		Classifier((Common.pkgConfig, Common.aclocal)),
		Classifier((FHS.usr.lib, FHS.lib), "\\.(a|cmake|la|pc)$"),
	), "dev",),
	Splitter(Classifier((FHS.lib, FHS.usr.lib), ("\\.so(\\.\\d+)*$")), "libs",),
	Splitter(Classifier((FHS.usr.share.man, FHS.usr.share.info, FHS.usr.share.doc)), "docs",),
	Splitter(Classifier(FHS.usr.src, ), "sources",),
	Splitter(Classifier((FHS.usr.share.locale,), ("\\.mo$", "\\.qm$", )), "locales",),
	Splitter(Classifier((FHS.usr.share / "javascript")), "javascript",),
	Splitter(Classifier((FHS.usr.share, FHS.etc)), "data",),
	Splitter(Classifier((FHS.usr,)), "data",),
)

FHSTearer = Tearer(FHSSplitters)
