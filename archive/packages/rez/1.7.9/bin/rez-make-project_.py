#!/usr/bin/python

from optparse import OptionParser
import subprocess as sp
import sys
import os
import os.path
import shutil
import uuid


def _mkdir(dir):
	if not os.path.exists(dir):
		print "making %s..." % dir
		os.mkdir(dir)


bin_cmake_code_template = \
"""
file(GLOB_RECURSE bin_files "bin/*")
rez_install_files(
	${bin_files}
    DESTINATION .
    EXECUTABLE
)
"""


_cmake_templates = {
	"BIN_CMAKE_CODE": \
"""
file(GLOB_RECURSE bin_files "bin/*")
rez_install_files(
    ${bin_files}
    DESTINATION .
    EXECUTABLE
)
""",

	"DOXYGEN_CMAKE_CODE": \
"""
include(RezInstallDoxygen)
file(GLOB_RECURSE doc_files "docs/*")

rez_install_doxygen(
    doc
    FILES %(FILES)s ${doc_files}
    DESTINATION doc
    %(DOXYPY)s

    # remove this once your docs have stabilised, then they will only be built and 
    # installed when you're performing a central install (ie a rez-release).
    FORCE 
)
""",

	"PYTHON_CMAKE_CODE": \
"""
file(GLOB_RECURSE py_files "python/*.py")
rez_install_python(
    py
    FILES ${py_files}
    DESTINATION .
)
"""
}


_project_types = [
	"empty",
	"doxygen",
	"python"
]

_project_template_deps = {
	"empty":	[],
	"doxygen":	["empty"],
	"python":	["empty"] # "doxygen"
}

_project_requires = {
	"empty":	[],
	"doxygen":	[],
	"python":	[]
}

_project_build_requires = {
	"empty":	[],
	"doxygen":	["doxygen"],
	"python":	[]
}



###########################################################################
# cmdlin
###########################################################################

usage = "usage: rez-make-project <name> <version>"
proj_types_str = str(',').join(_project_types)

p = OptionParser(usage=usage)
p.add_option("--type", dest="type", type="string", default="python", \
    help="Project type - one of [%s]. (default: python)" % proj_types_str)
p.add_option("--tools", dest="tools", type="string", default="", \
    help="Optional set of programs to create, comma-separated.")

(opts, args) = p.parse_args()

if opts.type not in _project_types:
	p.error("'%s' is not a recognised project type. Choose one of: [%s]" \
		% opts.type, proj_types_str)

if len(args) != 2:
	p.error("Wrong argument count.")

proj_name = args[0]
proj_version = args[1]

cwd = os.getcwd()
proj_dir_root = cwd + '/' + proj_name
proj_types = [opts.type]
proj_types += _project_template_deps[opts.type] or []
browser = os.getenv("BROWSER") or "firefox"

###########################################################################
# query system
###########################################################################

if "doxygen" in proj_types:
	doxygen_support = True
	doxypy_support = True
	doxygen_file_types = []
	string_repl_d = {"DOXYPY": ""}

	p = sp.Popen("rez-which doxygen", shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
	p.communicate()
	if p.returncode != 0:
		_project_build_requires["doxygen"].remove("doxygen")
		doxygen_support = False

	if doxygen_support and "python" in proj_types:
		p = sp.Popen("rez-which doxypy", shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
		p.communicate()
		if p.returncode == 0:
			_project_build_requires["doxygen"].append("doxypy")
			string_repl_d["DOXYPY"] = "DOXYPY"
			doxygen_file_types.append("py_files")
		else:
			print >> sys.stderr, "Skipped doxygen python support, 'doxypy' package not found!"
			doxypy_support = False

	doxy_files_str = str(' ').join([("${%s}" % x) for x in doxygen_file_types])
	string_repl_d["FILES"] = doxy_files_str
	code = _cmake_templates["DOXYGEN_CMAKE_CODE"] % string_repl_d
	_cmake_templates["DOXYGEN_CMAKE_CODE"] = code



###########################################################################
# create files and dirs
###########################################################################

print "creating files and directories for %s project %s-%s..." % \
	(opts.type, proj_name, proj_version)

str_repl = {
	"NAME":						proj_name,
	"VERSION":					proj_version,
	"USER":						os.getenv("USER"),
	"UUID":						str(uuid.uuid4()),
	"REZ_PATH":					os.getenv("REZ_PATH"),
	"BIN_CMAKE_CODE":			'',
	"PYTHON_CMAKE_CODE":		'',
	"DOXYGEN_CMAKE_CODE":		'',
	"COMMANDS":					'',
	"TOOLS":					'',
	"REQUIRES":					'',
	"BUILD_REQUIRES":			'',
	"HELP":						''
}

def _expand(s):
	return s % str_repl

def _expand_path(s):
	s = s.replace("_tokstart_", "%(")
	s = s.replace("_tokend_", ")s")
	return _expand(s)

def _gen_list(label, vals):
	s = ''
	if vals:
		s += label + ":\n"
		for val in vals:
			s += "- %s\n" % val
	return s


requires = []
build_requires = []
commands = []
tools = []

# insert tools
if opts.tools:
	tools = opts.tools.strip().split(',')
	str_repl["TOOLS"] = _gen_list("tools", tools)
	str_repl["BIN_CMAKE_CODE"] = bin_cmake_code_template
	commands.append("export PATH=$PATH:!ROOT!/bin")

# create the root path if not already exist
if os.path.exists(proj_dir_root):
	raise IOError, "Can not make project at '%s', folder already exist!" % proj_dir_root

else:
	print "Making project '%s' \n at '%s'..." % (proj_name, proj_dir_root)
	os.makedirs(proj_dir_root)
	

# copy and string-replace the templates
for proj_type in proj_types:
	utype = proj_type.upper()

	cmake_code_tok = "%s_CMAKE_CODE" % utype
	cmake_code = _cmake_templates.get(cmake_code_tok)
	if cmake_code:
		str_repl[cmake_code_tok] = cmake_code

	if proj_type == "doxygen":
		str_repl["HELP"] = "help: %s file://!ROOT!/doc/html/index.html" % browser
	elif proj_type == "python":
		commands.append("export PYTHONPATH=$PYTHONPATH:!ROOT!/python")

	requires += _project_requires[proj_type]
	build_requires += _project_build_requires[proj_type]

	str_repl["COMMANDS"] 		= _gen_list("commands", commands)
	str_repl["REQUIRES"] 		= _gen_list("requires", requires)
	str_repl["BUILD_REQUIRES"] 	= _gen_list("build_requires", build_requires)

	template_dir = "%s/template/project_types/%s" % (os.getenv("REZ_PATH"), proj_type)
	if not os.path.exists(template_dir):
		raise IOError
		print >> sys.stderr, "Internal error - path %s not found." % template_dir
		sys.exit(1)

	for root, dirs, files in os.walk(template_dir):
		dest_root = _expand_path(root.replace(template_dir, proj_dir_root))
		for dir in dirs:
			dest_dir = _expand_path(os.path.join(dest_root, dir))
			_mkdir(dest_dir)

		for file in files:
			fpath = os.path.join(root, file)
			f = open(fpath, 'r')
			s = f.read()
			f.close()
			
			# do string replacement, and remove extraneous blank lines
			s = _expand(s)
			while "\n\n\n" in s:
				s = s.replace("\n\n\n", "\n\n")

			dest_fpath = _expand(os.path.join(dest_root, file))
			print "making %s..." % dest_fpath
			f = open(dest_fpath, 'w')
			f.write(s)
			f.close()


# add programs, if applicable
if tools:
	shebang = '#!/bin/bash'
	if opts.type == "python":
		shebang = "#!/usr/bin/env python"
	_mkdir("./bin")

	for tool in tools:
		path = os.path.join("./bin", tool)
		print "creating %s..." % path
		f = open(path, 'w')
		f.write(shebang + '\n')
		f.close()
