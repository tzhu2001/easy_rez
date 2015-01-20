#!/usr/bin/python
#
# A tool for listing information about the difference between two sets of packages, including
# packages that have been added, packages that have been removed, and packages whos versions
# have changed, in this case listing all the changelogs associated with the version change.
# This information can optionally be displated in HTML format for easy viewing.
#

import os
import sys
import optparse
import rez_config as dc
import sigint


#########################################################################################
# command-line
#########################################################################################

p = optparse.OptionParser(usage="Usage: rez-diff [options] oldpkg1 oldpkgN [ -- newpkg1 newpkgN ]")

p.add_option("--html", dest="html", action="store_true", default=False, \
	help="output in html format [default = %default]")
p.add_option("--view-html", dest="viewhtml", action="store_true", default=False, \
	help="view the output directly in a browser [default = %default]")

if (len(sys.argv) == 1):
	p.parse_args(["-h"])
	sys.exit(0)

# turn all old pkgs into 'pkg=e' to force start from earliest
argv = []
newgroup = False

for pkg in sys.argv[1:]:
	if pkg == "--":
		newgroup = True
	if (not newgroup) and (pkg[0] != '-'):
		if (not pkg.endswith("=e")) and (not pkg.endswith("=l")):
			pkg += "=e"
	argv.append(pkg)

septok = "__SEP__"

# add new pkgs as latest of each if they weren't supplied
if "--" in argv:
	argv[argv.index("--")] = septok
else:
	newpkgs = []
	for pkg in argv:
		if pkg[0] != '-':
			newpkgs.append(pkg.split('-',1)[0])
	argv.append(septok)
	argv += newpkgs

(opts, args) = p.parse_args(argv)

opts.html = opts.html or opts.viewhtml

pos = args.index(septok)
old_pkgs_list = args[:pos]
new_pkgs_list = args[pos+1:]


#########################################################################################
# determine which pkgs have been added, which removed, and which altered
#########################################################################################

# (family, pkg)
old_pkgs = {}
new_pkgs = {}

for pkg in old_pkgs_list:
	fam = pkg.split('=',1)[0].split("-",1)[0]
	if fam in old_pkgs:
		sys.stderr.write("Error: package '" + fam + "' appears more than once in old package group.\n")
		sys.exit(1)
	old_pkgs[fam] = pkg

for pkg in new_pkgs_list:
	fam = pkg.split('=',1)[0].split("-",1)[0]
	if fam in new_pkgs:
		sys.stderr.write("Error: package '" + fam + "' appears more than once in new package group.\n")
		sys.exit(1)
	new_pkgs[fam] = pkg

# removed packages
removed_pkgs = []
fams = set(old_pkgs.keys()) - set(new_pkgs.keys())
for fam in fams:
	removed_pkgs.append(old_pkgs[fam])

# added packages
added_pkgs = []
fams = set(new_pkgs.keys()) - set(old_pkgs.keys())
for fam in fams:
	added_pkgs.append(new_pkgs[fam])

# altered packages
updated_pkgs = []
rolledback_pkgs = []
fams = set(new_pkgs.keys()) & set(old_pkgs.keys())
for fam in fams:
	old_path = dc.get_base_path(old_pkgs[fam])
	new_path = dc.get_base_path(new_pkgs[fam])
	if old_path != new_path:
		oldverstr = old_path.rsplit("/",1)[-1]
		newverstr = new_path.rsplit("/",1)[-1]
		oldver = dc.Version(oldverstr)
		newver = dc.Version(newverstr)
		if oldver < newver:
			updated_pkgs.append( (fam, old_path, new_path) )
		else:
			rolledback_pkgs.append( (fam, new_path, old_path) )


#########################################################################################
# generate output
#########################################################################################

rowcolindex3 = 0

if opts.html:
	big_line_sep = ""
	small_line_sep = ""
	br = "<br>"

	table_bgcolor2 = "DDDDDD"
	table_bgcolor = "888888"
	rowcols3 = [ "FFE920", "FFBE28" ]
	rowcols = [ "7CE098", "86BCFF" ]
	rowcols2 = [ [ "A4F0B7", "BDF4CB" ], [ "A8CFFF", "99C7FF" ] ]

else:
	big_line_sep   = "#########################################################################################"
	small_line_sep = "========================================================================================="
	br = ""


def print_added_packages(pkgs, are_added):

	global rowcolindex3

	if len(pkgs) > 0:
		print big_line_sep
		if are_added:
			tok = "added packages:  "
		else:
			tok = "removed packages:"

		pkgs_ = []
		for pkg in pkgs:
			pkg_ = pkg.rsplit("=",1)[0]
			pkgs_.append(pkg_)

		pkglist = str(", ").join(pkgs_)
		if opts.html:
			print "<tr>"
			print '  <td align="center"><font size="2">' + tok + '</font></td>'
			print '  <td bgcolor=#' + rowcols3[rowcolindex3] + '>'
			print '      <table border="0" cellpadding="5" bgcolor=#' + rowcols3[rowcolindex3] + '><tr><td>'
			print "         <font size='2'>" + pkglist + "</font>"
			print "      </td></tr></table>"
			print "  </td>"
			print "</tr>"
			rowcolindex3 = 1 - rowcolindex3
		else:
			print(tok + "\t" + pkglist)


def print_altered_packages(pkgs, are_updated):

	global rowcolindex3

	if len(pkgs) > 0:
		print big_line_sep
		if are_updated:
			tok = "updated packages:"
		else:
			tok = "rolled-back packages:"

		if opts.html:
			print '<tr><td align="center"><font size="2">' + tok + '</font></td><td>'
			print '<table border="0">'
			rowcolindex = 0
		else:
			print tok

		for pkg in pkgs:
			print small_line_sep
			if opts.html:
				print '<tr><td bgcolor=#' + rowcols3[rowcolindex3] + '>'
				print '<table cellspacing="5" border="0"><tr><td align="center"><font size=2>'
				rowcolindex3 = 1 - rowcolindex3

			path = pkg[1].rsplit("/",1)[0]
			fam = pkg[0]
			oldverstr = pkg[1].rsplit("/",1)[-1]
			newverstr = pkg[2].rsplit("/",1)[-1]
			oldver = dc.Version(oldverstr)
			newver = dc.Version(newverstr)

			if are_updated:
				print fam + br + " [" + str(oldver) + " -> " + str(newver) + "]"
			else:
				print fam + br + " [" + str(newver) + " -> " + str(oldver) + "]"

			if opts.html:
				print '</font></td></tr></table></td><td width="100%"><table border="0" bgcolor=#' + \
					table_bgcolor + ' cellpadding="0" cellspacing="1" width="100%">'

			# list all changelogs between versions
			pkgpath = dc.get_base_path(fam + "-" + str(newver))
			currver = dc.Version(pkgpath.rsplit("/",1)[-1])

			while currver > oldver:

				if opts.html:
					rowcolindex = 1 - rowcolindex
					print '<tr bgcolor=#' + rowcols[rowcolindex] + \
						'><td align="center" width="5%"><font size=2>&nbsp;' + str(currver) + "&nbsp;</font></td><td>"
				else:
					print "\n" + fam + "-" + str(currver) + ":"

				chlogpath = pkgpath + "/.metadata/changelog.txt"
				if os.path.isfile(chlogpath):
					f = open(chlogpath)
					chlog = '\t' + f.read().strip().replace('\n', '\n\t')
					if opts.html:
						lines = chlog.split('\n')
						lines2 = []
						prev_row = False
						rowcolindex2 = 0
						td_cols = rowcols2[rowcolindex]

						for l in lines:
							l2 = l.strip()
							if len(l2) > 0:
								if l2.find("-----------------") == -1:
									if l2.find("Changelog since rev") == 0:
										l2 = "<tr><td bgcolor=#" + td_cols[rowcolindex2] + \
											"><font size=1>" + l2 + "</font></td></tr>"
									else:
										is_rev_line = False
										if l2[0] == 'r':
											toks = l2.split(' ')
											if ((toks[-1] == "lines") or (toks[-1] == "line")) and ("|" in toks):
												l2 = "<tr><td bgcolor=#" + td_cols[rowcolindex2] + "><font size=2><i>" + l2 + "</i>"
												rowcolindex2 = 1 - rowcolindex2
												if prev_row:
													l2 = "</font></td></tr>" + l2
												prev_row = True
												is_rev_line = True
										if not is_rev_line:
											l2 = "<br>" + l2

									lines2.append(l2)

						chlog = str('\n').join(lines2)
						chlog = '<table border="0" cellpadding="5" cellspacing="1" width="100%">' + chlog + '</table>'

					f.close()
					print chlog
				else:
					if opts.html:
						print '<table cellspacing="1"><tr><td><font size=2>&nbsp;'
					print "\tno changelog available."
					if opts.html:
						print "</td></tr></table></font>"

				if opts.html:
					print "</td></tr>"

				pkgpath = dc.get_base_path(fam + "-0+<" + str(currver))
				currver = dc.Version(pkgpath.rsplit("/",1)[-1])

			if opts.html:
				print "</table></td></tr>"
				print "<tr><td></td><td></td></tr>"

		if opts.html:
			print "</table></td></tr>"


if opts.html:
	print '<font face="Arial">'
	print '<table border="0" cellpadding="0" bgcolor=#' + table_bgcolor2 + '>'

print_added_packages(removed_pkgs, False)
print_added_packages(added_pkgs, True)
print_altered_packages(updated_pkgs, True)
print_altered_packages(rolledback_pkgs, False)

print big_line_sep

if opts.html:
	print "</table></font>"

























#    Copyright 2008-2012 Dr D Studios Pty Limited (ACN 127 184 954) (Dr. D Studios)
#
#    This file is part of Rez.
#
#    Rez is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Rez is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with Rez.  If not, see <http://www.gnu.org/licenses/>.
