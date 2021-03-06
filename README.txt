REZ Easy is a branch of REZ with the following modifications
1) Cross platform enabled, tested in Linux and Windows 
2) Integration with GIT
3) no CMAKE required to release packages 
4) Release command with ability to save resolved environment into a shell file (toolchain)

The following content have 2 aims.
1) Quick startup guide on REZ, with focus on getting it up and running
2) Provide base packages for you to start assembling your own pipeline with REZ.

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

   
The following tutorial will demonstrate the EASY REZ release process using GIT as repository.
It's production ready, just check this into your own GIT repository and you're set to go.

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
# since REZ will attempt to tag the GIT state with the tool release version.
# it will prompt you for user/password (see above for user/pw)
rez-release

# NOTE:  In this test, 1.0.0 has already been tagged in Github, REZ will warn you that the tag operation has failed
# This can be safely ignored.


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
* In production, users don't dynamically resolve environment.
* Rather, a master builder would resolve all the tools required and save the resolved environment in a shell script.
* This shell script can then be sourced by all users to enter a SHOW environment
* Each show can have it's own environment with unique set of tools and tool versions.
* Such is the concept of a Toolchain, which is a package with only the package.yaml file.
* The package file list the tool names and can restrict tool version.
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
       
3. Remember the GIT credentials, execute command below before doing next git pull/push command.
   more info: https://help.github.com/articles/caching-your-github-password-in-git/

       git config --global credential.helper wincred
       
4. To develope REZ, you can set the rez environment to use local.

       export REZ_PATH="/path/to/rez" # where /bin/rez-env  is at /path/to/rez/bin/rez-env
