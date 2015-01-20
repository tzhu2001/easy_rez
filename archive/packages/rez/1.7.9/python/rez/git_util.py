import subprocess

def has_git():
    result = subprocess.Popen(['git'], stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()[0]
    
    if "usage: git" in result:
        return True
    
    else:
        return False

def list_modified():
    result = subprocess.Popen(['git','ls-files','--modified'], stdout=subprocess.PIPE ).communicate()[0]
    
    return result.split()


def query_current_branch():
    result = subprocess.Popen(['git','rev-parse','--abbrev-ref','HEAD'], stdout=subprocess.PIPE ).communicate()[0]
    
    return result.strip()

def list_untracked():
    result = subprocess.Popen(['git','ls-files','--others','--exclude-standard'], stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()[0]
    
    return result.split()


def list_added_removed():
    result = subprocess.Popen('git diff --name-only --diff-filter=A --cached', stdout=subprocess.PIPE, shell=True).communicate()[0]
    return result.split()
    
    
def query_has_pushed():    
    result = subprocess.Popen('git log origin/master..master', stdout=subprocess.PIPE, shell=True).communicate()[0]
    return result


def password_prompt():
    result = subprocess.Popen('ssh-add', stdout=subprocess.PIPE, shell=True).communicate()[0]
    return result    
    
    
def tag_and_push(toolname, version, comments):
    tag_name = toolname + '-' + version
    
    print '\n > Tagging version %s into the git repository: \n' % tag_name
    
    # create tag
    msg, error = subprocess.Popen([ 'git', 'tag', '-a', tag_name, '-m', comments ],  
                                                                stdin  = subprocess.PIPE, 
                                                                stdout = subprocess.PIPE, 
                                                                stderr = subprocess.PIPE,
                                                                ).communicate()
#     if error:
#         print "Warning: create tag may have failed: ", error
#     else:
#         print msg

    # push tag                                                            
    msg, error = subprocess.Popen([ 'git', 'push', 'origin', tag_name],  
                                                                stdin  = subprocess.PIPE, 
                                                                stdout = subprocess.PIPE, 
                                                                stderr = subprocess.PIPE,
                                                                ).communicate()                                                                
    
    
    
    if tag_name not in error: # std error is just a message, so only error if tag not found in message.
        print "Tag push to git failed: \n '%s'" % error
        
        
        # tag push 
        msg, error = subprocess.Popen([ 'git', 'tag', '-d', tag_name ],  
                                                                stdin  = subprocess.PIPE, 
                                                                stdout = subprocess.PIPE, 
                                                                stderr = subprocess.PIPE,
                                                                ).communicate()        
        return False        
    else: 
        return True
        
    
    
    
def query_ready_for_release():
    '''
    Query if the current location is ready for release.
    
    Have to be in master branch    
    Have no uncommitted changes
    Have to have latest commit push to master
    
    @return list of errors
    '''
    current_branch      = query_current_branch()
    modified_list       = list_modified()
    untracked_list      = list_untracked()    
    added_removed_list  = list_added_removed()
    
    pushed_log          = query_has_pushed()  
    
    # ignore the .rez-build files
    untracked_list = [ f for f in untracked_list if not f.startswith('.rez_build') ]  
    
    error_msg = []
    
    if current_branch!='master':
        error_msg.append( '-' * 50);
        error_msg.append( "> You must be in the master branch to make a release. You are in %s. \n" %  current_branch)
    
    if modified_list:
        error_msg.append( '-' * 50);
        error_msg.append( "> There are %s uncommitted modified files: \n   %s" % ( len(modified_list), 
                                                                                  '\n   '.join(modified_list) 
                                                                                ) ) 
        error_msg.append( ' * Hint: Commit file changes ex: git commit %s -m "update version for release..." \n' 
                                            % ' '.join(modified_list))
        
    if untracked_list:
        error_msg.append( '-' * 50);
        error_msg.append( "> There are %s untracked files:  \n   %s" % (len(untracked_list),
                                                                      '\n   '.join(untracked_list))
                         )

        error_msg.append( ' * Hint: Add file to git ex: git add %s  \n' 
                                            % ' '.join(untracked_list))
        
    if added_removed_list:
        error_msg.append( '-' * 50);
        error_msg.append( "> There are %s uncommitted added/removed files: \n   %s" % ( 
                                                                                      len(added_removed_list),
                                                                                      '\n   '.join(added_removed_list)                                                                                       
                                                                                     ))
        
    if pushed_log:
        error_msg.append( '-' * 50);
        error_msg.append( "> There are commit(s) not pushed to master: \n\n%s" % pushed_log)
        error_msg.append( ' * Hint: Push commit to master ex: git push \n')
    
    if error_msg:        
        return False, error_msg
    
    else:
        return True, ["success"]
        
        
if __name__ == '__main__':
    
    import os
    
    #os.chdir('/norman/work/tzhu/git_norman/sandbox/rez_deploy/int/demoLogger')
    os.chdir('/norman/work/tzhu/git_norman/sandbox/rez_deploy/int/common/demoTool')
    
    print '...has git',  tag_and_push('demoTool', '0.5.5', 'some comments')