How REZ is configure to work with GIT:

A REZ package a folder that contains codes and the package.yaml file.
ex: https://github.com/tzhu2001/simple_rez/tree/master/demotool

The package.yaml specifies the release information, the version, release comment, and tool environment variables.
ex: https://github.com/tzhu2001/simple_rez/blob/master/demotool/package.yaml

REZ release a package from GIT into a shared network location stored in REZ_RELEASE_PACKAGES_PATH
1) it will deploy a new version as specifed in the package.yaml file.
	ex: $REZ_RELEASE_PACKAGES_PATH/demotool/1.0.0
2) it will tag the GIT state with the release version.  This will enable you do code comparison between tool versions later.

To be executed in Bash Shell session with git installed.

**********************
*     Install REZ    *
**********************
# make the git repository directory to locally checkout code 
mkdir /tmp/repo

# make the test release directory, where REZ will install all the packages
# In actual production this would be a shared folder on the network
mkdir /tmp/release

# clone the rez source from github, no password needed.
cd /tmp/repo
git clone https://github.com/tzhu2001/simple_rez.git

# simple_rez contains two subfolders "archive" and "demotool"
cd /tmp/repo/simple_rez

# The archive contains the packages necessary for REZ to function, including yaml and pyparsing.
# Copy all of the pacakges to release.
cp -r /tmp/repo/simple_rez/archive/packages /tmp/release/packages

**********************
*  Start REZ session *
**********************
source /tmp/release/packages/rez/1.7.9/init.sh

# NOTE: the above will establish these environment variables
#  1. REZ_RELEASE_PACKAGES_PATH : where packages will be installed
#  2. REZ_LOCAL_PACKAGES_PATH : where local development packages will be installed  
#  3. REZ_PATH : location of the REZ source

# test using rez to find yaml package, expect to return "/tmp/release/packages/yaml/3.10.0"
rez-which yaml 


******************************
*       Release demotool     *
******************************
# You must be inside the package to release it.
cd /tmp/repo/simple_rez/demotool

rez-release

# NOTE:  As version 1.0.0 has already been tagged in Github, REZ will warn you that tag operation failed, 
#        This can be safely ignored as this is only a test 


******************************************
*   Resolve environment with demotool    *
******************************************
