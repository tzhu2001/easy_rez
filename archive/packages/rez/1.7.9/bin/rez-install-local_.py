#!/usr/bin/python
# append to the python path
import sys, os, shutil, logging  

rez_python = os.environ.get('REZ_SOURCE_PATH') + '/python'

if not os.path.exists(rez_python):
   raise IOError, "Rez python path not found in '%s'" %  rez_python 
sys.path.append( rez_python )

import yaml
from rez.rez_release import install_pkg

logging.getLogger().setLevel(10)

local_pkg_root = os.environ.get('REZ_LOCAL_PACKAGES_PATH', None)
if not local_pkg_root:
    raise IOError, "environ not exist: REZ_LOCAL_PACKAGES_PATH."

install_pkg(local_pkg_root)

    