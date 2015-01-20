"""
rez-release

A tool for releasing rez - compatible projects centrally
"""

import sys
import os
import time
import shutil
import subprocess
from rez_metafile import *
import versions
import config

SEND_RELEASE_MAIL = os.environ.get("SEND_RELEASE_MAIL", "true") # set to false to only email developer
FORCE_RELEASE     = os.environ.get("FORCE_RELEASE", "false") # no need to tag, overwrite the existing release packages.
RELEASE_TO_TEST   = os.environ.get("RELEASE_TO_TEST", "false")

LOG = config.get_logger()
# import doxygen_util

##############################################################################
# Exceptions
##############################################################################

class RezReleaseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)


##############################################################################
# Globals
##############################################################################

REZ_RELEASE_PATH_ENV_VAR =         "REZ_RELEASE_PACKAGES_PATH"
EDITOR_ENV_VAR             =         "REZ_RELEASE_EDITOR"
RELEASE_COMMIT_FILE     =         "rez-release-svn-commit.tmp"


##############################################################################
# Public Functions
##############################################################################
import subprocess
def git_get_status():
    pass

def check_git_under_master_branch(git_status_string):
    pass
    
# rez install path
LOCAL_PKG_ROOT = os.environ.get('REZ_LOCAL_PACKAGES_PATH', None)
RELEASE_PKG_ROOT = os.environ.get('REZ_RELEASE_PACKAGES_PATH', None)


import git_util
def release_from_path(path, commit_message, njobs, build_time, allow_not_latest):
    """
    release a package from the given path on disk, copying to the relevant tag,
    and performing a fresh build before installing it centrally. If 'commit_message'
    is None, then the user will be prompted for input using the editor specified
    by $REZ_RELEASE_EDITOR.
    path: filepath containing the project to be released
    commit_message: None, or message string to write to svn, along with changelog
    njobs: number of threads to build with; passed to make via -j flag
    build_time: epoch time to build at. If 0, use current time
    allow_not_latest: if True, allows for releasing a tag that is not > the latest tag version
    """
    # check for ./package.yaml
    if not os.access(path + "/package.yaml", os.F_OK):
        raise RezReleaseError(path + "/package.yaml not found")    
    
    # load the package metadata
    metadata = ConfigMetadata(path + "/package.yaml")
    
    global RELEASE_TO_TEST, FORCE_RELEASE, SEND_RELEASE_MAIL
    if RELEASE_TO_TEST=="true":
        FORCE_RELEASE = "true"        
        SEND_RELEASE_MAIL = "false"
    
    # check that this tag does not already exist
    release_path = os.environ.get('REZ_PACKAGES_PATH').strip(': ') + '/' + metadata.name + '/' + metadata.version
    current_link = os.environ.get('REZ_PACKAGES_PATH').strip(': ') + '/' + metadata.name + '/current'
    
    release_path = config.window_path(release_path)

    if not FORCE_RELEASE=="true" and os.path.exists( release_path ):
        print "The version %s has already been released, found at: %s" % ( metadata.version, release_path ) 
        print " * Hint: increment the version specified in package.yaml"
        return 
    
    ##### verify the package.yaml

    if (not metadata.version):
        raise RezReleaseError(path + "/package.yaml does not specify a version")
    try:
        this_version = versions.Version(metadata.version)
    except versions.VersionError:
        raise RezReleaseError(path + "/package.yaml contains illegal version number")

    # metadata must have name
    if not metadata.name:
        raise RezReleaseError(path + "/package.yaml is missing name")

    # metadata must have uuid
    if not metadata.uuid:
        raise RezReleaseError(path + "/package.yaml is missing uuid")

    # metadata must have description
    if not metadata.description:
        raise RezReleaseError(path + "/package.yaml is missing a description")

    # metadata must have description
    if not metadata.release_info:
        raise RezReleaseError(path + "/package.yaml is missing release_info that describe what has been updated")

    # metadata must have authors
    if not metadata.authors:
        raise RezReleaseError(path + "/package.yaml is missing authors")

    pkg_release_path = os.getenv(REZ_RELEASE_PATH_ENV_VAR)
    if not pkg_release_path:
        raise RezReleaseError("$" + REZ_RELEASE_PATH_ENV_VAR + " is not set.")

    # check uuid against central uuid for this package family, to ensure that
    # we are not releasing over the top of a totally different package due to naming clash
    existing_uuid = None
    package_uuid_dir = pkg_release_path + '/' + metadata.name
    package_uuid_file = package_uuid_dir + "/package.uuid"
    package_uuid_exists = True

    try:
        existing_uuid = open(package_uuid_file).read().strip()
    except Exception:
        package_uuid_exists = False
        existing_uuid = metadata.uuid

    if(existing_uuid != metadata.uuid):
        raise RezReleaseError("the uuid in '" + package_uuid_file + \
            "' does not match this package's uuid - you may have a package name clash. All package " + \
            "names must be unique.")



    # query for the state of the git for release
    git_ready, message = git_util.query_ready_for_release()
    
    if not FORCE_RELEASE=="true" and not git_ready:
        print '-' * 50;
        print "Warning: You git repository is not in release state:"
        print "\n".join(message)
        
        return 


    print
    print("---------------------------------------------------------")
    print("rez-release: installing...")
    print("---------------------------------------------------------")
    print
    
    if not RELEASE_PKG_ROOT:
        raise IOError, "Env REZ_RELEASE_PACKAGES_PATH not set."
    
    install_pkg(RELEASE_PKG_ROOT)

    print
    print("---------------------------------------------------------")
    print("rez-release: tagging...")
    print("---------------------------------------------------------")
    print
        
    # tag and release:
    if not FORCE_RELEASE=="true":
        print "\n* Package has been verified ready for release: "
        success = git_util.tag_and_push( metadata.name, metadata.version, metadata.description )
        if not success:
            print "Release process interrupted, incomplete publish."
            return
     
    print
    print("rez-release: your package was released successfully.")
    print


def link(target, link, force=False):

    import os, sys, subprocess, random, re
#     
#     try:
#         target, link = sys.argv[1], sys.argv[2] 
#     except:
#         raise IOError, "Expected command: rez-link <target> <link> <force use -f> \n Ex: rez-link c:\\target c:\\link \n or rez-link /c/target /c/link"
#     
#     if len(sys.argv) >= 4 and sys.argv[3] == '-f':
#         force = True
#     else:
#         force = False
    
    if link.startswith('/'):
        link = re.sub('/([a-z|A-Z])/', '\g<1>:/', link)
        
    if target.startswith('/'):
        target = re.sub('/([a-z|A-Z])/', '\g<1>:/', target)
        
    if not os.path.exists(target):
        raise IOError, 'Target does not exist: "%s"' % target
    
    if os.path.exists(link):
        if force:
            os.rmdir(link)
        else:
            raise IOError, 'Link already exist: "%s"' % link    
        
    
    cmd = r'cmd /c "mklink /J ^"%s^" ^"%s^""' % (link, target) 
    
    print 'executing: ', cmd
    os.system(cmd)

    
def install_pkg( pkg_root, local_install=True ): 
    # find the package.yaml
    pkg_path = os.getcwd() + '/package.yaml'
    
    if not os.path.isfile(pkg_path):
        raise IOError, "You need tobe inside a rez-package for installation.  Package.yaml not found: '%s'..." % pkg_path
    
    pkg_content = yaml.load(open(pkg_path))
    inst_ver = pkg_content['version']
    pkg_name = pkg_content['name']   
    
    pkg_root     = pkg_root + '/' + pkg_name 
    pkg_ver_root = pkg_root + '/' + inst_ver
    pkg_current  = pkg_root + '/current'
    
    # clean up if already exist, other wise create directory
    if os.path.exists(pkg_ver_root):
        if local_install:
            LOG.info("package already installed, removing it... '%s'" % pkg_ver_root)
            shutil.rmtree(pkg_ver_root)
        else:
            raise IOError, "package already exist '%s' " % pkg_ver_root     
        
    if os.path.exists(pkg_ver_root):
        LOG.error( "Failed to clean directory before install '%s'." % pkg_ver_root)
        
    if not os.path.exists( pkg_root):
        LOG.info( "Making directory for install '%s'." % pkg_root)
        os.makedirs( pkg_root )
    
    source_root = os.getcwd()
    LOG.info( "Copying source directory '%s' to dest '%s'..." % (source_root, pkg_ver_root) )
    shutil.copytree(source_root, pkg_ver_root)
    
    # if its a toolchain, make the context file
    toolchain_context_list = [ c for c in pkg_content if c.startswith('toolchain.') ]
    
    build_list = []
    for ctx in toolchain_context_list:
        pkg_list = [ p.strip() for p in pkg_content[ctx].split() if p.strip() and not p.strip().startswith('#')]
        context_filename = ctx[len('toolchain.'):]
        context_path = pkg_root + '/'+ context_filename
        
        rez_bin_root = config.get_bin_root()
        cmd = 'rez-config %s --no-local --print-env > "%s"' %  ( ' '.join(pkg_list), 
                                                        context_path)
        
        run_path = pkg_ver_root + '/build_%s_context.sh' % ctx
        backup_context_path = pkg_ver_root + '/' + context_filename # keep a copy in the folder.
        
        f = open( run_path, 'w' )
        f.write(cmd)
        f.write('\n')
        f.write('python ' + os.environ.get('PRODTOOLS') + '/bin/patch_toolchain_context.py "%s"' % context_path)
        f.write('\n')
        f.write('cp "%s" "%s"' % (context_path, backup_context_path))
        f.write('\n')   
        f.write('notepad "%s" &' % context_path)
        f.close()
        
        build_list.append( 'bash ' + run_path )
        
        
        #cmd = 'python "%s/rez-config_.py" %s --print-env > "%s"' %  (  rez_bin_root,
         #                                                                ' '.join(pkg_list), 
         #                                                                context_path)
#        LOG.info("\n\nBuilding toolchain '%s': \n command: %s" % (ctx[10:], cmd) )
#         
        #subprocess.Popen(cmd, shell=True).communicate()
         
        #if not os.path.isfile(context_path) or open(context_path).read().strip()=="":
        #    raise IOError, "Did not successfully build toolchain path: %s" % context_path 
    
    link( pkg_ver_root, pkg_current, force=True)
    LOG.info("Linking '%s' -> '%s'" % (pkg_current, pkg_ver_root) )
    
    if build_list:
        print "\n================ IMPORTANT =================="
        print " Please run the following to build the context "
        print " \n ".join(build_list)
            

RELEASE_EMAIL_TEMPLATE = '''
<html><head></head><body>
<b>Updates:</b> %(message)s 
<br>
<a href='http://docserver:8080/docs/%(api_doc_path)s'> <b> Docs: </b> %(local_doc_path)s</a> 
</body></html>
'''

def send_release_mail(title, message, api_doc_path):
    '''
    send release email to tools_release
    '''
    import getpass
    import smtplib
    from email.mime.text import MIMEText 
    from email.mime.multipart import MIMEMultipart 
    
    local_doc_path = doxygen_util.PACKAGE_DOC_ROOT + '/' + api_doc_path
    
    user_mail             = getpass.getuser() + '@mikrosimage.eu'
    tools_release_mail     = 'tools_releases@mikrosimage.eu'
    email_list          = [user_mail]
    if SEND_RELEASE_MAIL=="true":  email_list.append( tools_release_mail )
    
    msg = MIMEMultipart('alternative')
    msg['Subject']     = title
    msg['From']     = user_mail
    msg['To']         = ','.join( email_list )
    
    content = RELEASE_EMAIL_TEMPLATE % vars()
    msg.attach( MIMEText(content, 'html') )
    
    s = smtplib.SMTP('google.com')
    s.sendmail(user_mail, email_list, msg.as_string())    
    s.quit()

    # send_release_mail('testing title 2', 'testing message', 'demoTool/0.6.0/html/classes.html')

