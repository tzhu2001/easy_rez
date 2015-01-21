Easy REZ is a branch of REZ with the following modifications
1) Cross platform enabled, tested in Linux and Windows 
2) no CMAKE required to release packages 
3) Integration with GIT
4) Updated rez-release with ability to save resolved environment into a shell file

How REZ is configured to work with GIT:

REZ packages are store in GIT, each package is a folder that contains codes and the package.yaml file.
ex: https://github.com/tzhu2001/easy_rez/tree/master/demotool

The package.yaml contain three type of information: 
1) general: name, description
2) release: version name, release note
3) runtime: environment variables and package dependencies required to run tool
ex: https://github.com/tzhu2001/easy_rez/tree/master/demotool/package.yaml

REZ release packages from GIT into a shared network location as specified by $REZ_RELEASE_PACKAGES_PATH environment.
Specifically:
1) it verifies any code changes in the packages been committed and pushed to GIT
2) it will make a copy of the package to the release directory, including the package.yaml file
	ex: $REZ_RELEASE_PACKAGES_PATH/demotool/1.0.0
3) it will tag the GIT state with the package version name.  
   This will enable code comparison between package versions.

   
The following instructions will demonstrate the REZ release process using GIT as repository.
It has been tested on Fedora Linux and Windows 8.
NOTE: for Windows 8 please see appendix to install GIT with Bash.

**************************
*   Installing REZ    
*
*   Requires a BASH session with GIT client installed.
*   If prompt for password, use user "wukong123", password "wukong1234"
*
**************************
# make the git repository directory to locally checkout code 
mkdir /tmp/repo

# make the test release directory, where REZ will install all the packages
# In actual production this would be a shared folder on the network
mkdir /tmp/release

# checkout the rez source from github to local folder /tmp/repo
cd /tmp/repo
git clone https://github.com/tzhu2001/easy_rez.git

# easy_rez contains two subfolders "archive" and "demotool"
cd /tmp/repo/easy_rez

# The subfolder easy_rez/archive contains the packages necessary for REZ to function
# The packages include yaml and pyparsing, they are pure python implementations
# Copy all of the pacakges to release.
cp -r /tmp/repo/easy_rez/archive/packages /tmp/release

**********************
*  Start REZ Session 
**********************
# source the init.sh to enter a new REZ shell session.
source /tmp/release/packages/rez/1.7.9/init.sh

# NOTE: the above will source all the Rez commands as well as setting these environment variables
#  REZ_RELEASE_PACKAGES_PATH : where packages will be installed
#  REZ_LOCAL_PACKAGES_PATH : where local development packages will be installed  
#  REZ_PATH : location of the REZ source

# test command rez-which: find yaml package, expect to return "/tmp/release/packages/yaml/3.10.0"
rez-which yaml 


******************************
*       Release demotool within REZ Session   
******************************
# You must be inside the package to release it.
cd /tmp/repo/easy_rez/demotool

# now release the package. 
# since REZ will attempt to tag the GIT state, it may prompt you for user/password (see above for user/pw)
rez-release

# NOTE:  As version 1.0.0 has already been tagged in Github, REZ will warn you that the tag operation has failed, 
#        and that the release has been interrupted.  This can be safely ignored as tool has been released.


******************************************
*   Resolve environment with demotool    
******************************************
# now that demotool has been released, you can ask REZ to build and enter an new shell demotool enabled.
rez-env demotool

# echo PYTHONPATH to see that the released demotool package has been appended.
# recall that this is the result of the configuration in package.yaml
echo $PYTHONPATH

# PATH has also been appended with demotool/1.0.0/bin so that you can launch test command
demotool

# you can specify in a more specific version, as well ask REZ to build more than one package. 
# ex: build and start shell with demotool and yaml
rez-env demotool-1.0 yaml

# you can append a new tool to the existing environment by using -t
rez-env -t pyparsing

# you can print shell environment as resolved by REZ without sourcing it.
rez-config demotool yaml --print-env

******************************************
* Toolchain   
*
* In production user usually wouldn't dynamically resolve environment.
* Rather, a master builder would resolve all the tools required and save the resulting environment in a shell script.
* This shell script can then be used by others to enter an environment for a SHOW.
* Such is the concept of a Toolchain, which is a empty package with only the package.yaml file.
* There may be a different toolchain for each show, with different tools and tool version requirements.
*
* The command "rez-release" handles packages specially prefixed with "toolchain_",
* which resolve an environment and save that to a SHOW.context file.
*
******************************************
(more tutorials to come on toolchain build and release)




******************************************
*
* APPENDIX REZ in Windows require GIT Bash
*
******************************************
1. Install Git Windows Client, which will also install Git Bash
   
    downloaded from http://msysgit.github.io/
  
2. Hookup Git Bash to python

In bash session, make a soft link to your python install.  
Test your link by starting python shell via "python".

       ln -s /c/Python27/python.exe /usr/bin/python
