#
# System initialization script for rez. Source this file in order to use rez. 
#
export USER=$USERNAME

# Determine the REZ install paths
export REZ_PATH=$REZ_SOURCE_PATH
if [ "$REZ_PATH" == "" ]; then	
        REZ_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
	
	# note: only works if init.sh is not symlink
        echo "REZ_SOURCE_PATH not specified, auto resolve to: '$REZ_PATH'"
fi

# Determine the REZ package paths
if [ "$REZ_RELEASE_PACKAGES_PATH" == "" ]; then	
	echo "REZ_RELEASE_PACKAGES_PATH [installed packages root] not found in env."	

        PKG=`dirname $REZ_PATH`;
        PKG=`dirname $PKG`;
        PKG=`dirname $PKG`;
        PKG="$PKG/packages";
        
        if [ -d $PKG ]; then
		echo "REZ_RELEASE_PACKAGES_PATH auto resolve to '$PKG'.";
		REZ_RELEASE_PACKAGES_PATH=$PKG;
	fi
fi

# Determine the REZ dependent package paths, neccessary for parsing package yaml files.
REZ_YAML_PATH=$REZ_RELEASE_PACKAGES_PATH/yaml/3.10.0
REZ_PYPARSE_PATH=$REZ_RELEASE_PACKAGES_PATH/pyparsing/2.0.2

if [ ! -d $REZ_PATH ]; then
	echo "ERROR! Rez could not be found at $REZ_PATH" 1>&2
else

	# where rez searches for packages
	if [ "$REZ_PACKAGES_PATH" == "" ]; then
		export REZ_PACKAGES_PATH=$HOME/packages:$REZ_RELEASE_PACKAGES_PATH
	fi


	# where rez will publish packages to (ie those released with rez-release)
	#if [ "$REZ_RELEASE_PACKAGES_PATH" == "" ]; then
	#	export REZ_RELEASE_PACKAGES_PATH=
	#fi


	# where rez will publish local packages to (ie those installed with rez-build -- -- install)
	if [ "$REZ_LOCAL_PACKAGES_PATH" == "" ]; then
		export REZ_LOCAL_PACKAGES_PATH=$HOME/packages
	fi


	# where rez-egg-install will install python egg packages to
	if [ "$REZ_EGG_PACKAGES_PATH" == "" ]; then
		export REZ_EGG_PACKAGES_PATH=$REZ_RELEASE_PACKAGES_PATH
	fi

	# expose rez binaries, replacing existing rez paths if they have been set already
	PATH=`echo $PATH | /usr/bin/tr ':' '\n' | grep -v '^$' | grep -v '$REZ_PATH' | /usr/bin/tr '\n' ':'`
	export PATH=$PATH:$REZ_PATH/bin

	if [ "$REZ_RELEASE_EDITOR" == "" ]; then
		export REZ_RELEASE_EDITOR=/usr/bin/kwrite
	fi


	if [ "$REZ_DOT_IMAGE_VIEWER" == "" ]; then
		export REZ_DOT_IMAGE_VIEWER=/usr/bin/kde-open
	fi


	source $REZ_PATH/bin/_complete

fi


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
