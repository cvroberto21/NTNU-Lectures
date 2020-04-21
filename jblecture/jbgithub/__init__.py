from github import Github, GitAuthor, GithubException
import getpass
import pathlib
from ..jbcd import JBcd
import subprocess
import distutils
import shutil
import git
import re

cfg = {}

def createEnvironment( mycfg ):
    global cfg
    #print('jbgithub', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    cfg['GITHUB'] = None
    #print('jbgithub', hex(id(cfg)))
    return cfg


def readGithubToken():
    passwd = getpass.getpass("Github Token:")    
    return passwd

def login( token ):
    g = Github( token )
    cfg['GITHUB'] = g
    cfg['GITHUB_TOKEN'] = token
    return g

def getRepositories( ):
    repos = None
    if 'GITHUB' not in cfg or cfg['GITHUB'] is None:
        tok = readGithubToken()
        login( tok )
    if 'GITHUB' in cfg and cfg['GITHUB']:
        repos = cfg['GITHUB'].get_user().get_repos()
    return repos

def createRepoTitle( title ):
    return title.replace(" ", "-")

def findRepoByName( title ):
    repo = None
    if 'GITHUB' in cfg and cfg['GITHUB']:
        repos = getRepositories()
        if repos:
            for r in repos:
                # print("Github repo", r.name )
                if r.name == title:
                    repo = r
                    break
    return repo

def findBranchByName( repo, bName ):
    branch = None
    if 'GITHUB' in cfg and cfg['GITHUB']:
        branches = repo.get_branches()
        if branches:
            for b in branches:
                if b.name == bName:
                    branch = repo.get_branch( branch = bName )
                    break
    return branch

def runCommand( cmd, secure = False ):
    if not secure:
        print( "Running command " + cmd )
    o = None
    
    if not secure:
        myStdOut = None
        myStdErr = None
    else:
        myStdOut = subprocess.DEVNULL
        myStdErr = subprocess.DEVNULL
        
    try:
        o = subprocess.call( cmd, stdout=myStdOut, stderr=myStdErr, shell=True)
    except subprocess.CalledProcessError as error:
        print("Command returned error CalledProcessError", error, error.stderr )
    if o and not secure:
        print( "Output " + cmd + ":\n" + o.decode('utf-8') )

# https://github.com/cvroberto21/Test-Implementation.git

def modUrl( url, tok ):
    n = None
    m = re.match( r"(?P<scheme>https?)://(?P<host>[^/]*)/(?P<user>[^/]*)/(?P<repo>.*)", url )
    
    if m:
        n = m.group('scheme') + "://" + m.group('user') + ':' + tok + '@' + m.group('host') + '/' + m.group('user') + '/' + m.group('repo')
        cfg['GITHUB_USER'] = m.group('user')
        cfg['GITHUB_PAGES_URL' ] =  'https://{user}.github.io/{repo}/'.format( user=m.group('user'), repo=m.group('repo')[:-4] )
    else:
        raise(Exception("Invalid URL Format"))
    return n

def installLFS( tdir=pathlib.Path("/tmp") ):
    with JBcd( tdir ):
        runCommand( "wget -O /tmp/lfs.tgz https://github.com/git-lfs/git-lfs/releases/download/v2.10.0/git-lfs-linux-amd64-v2.10.0.tar.gz", True )
        runCommand( "tar -xzpvf /tmp/lfs.tgz", True )
        runCommand( "sudo ./install.sh", True )


MAX_GITHUB_FILE_SIZE=(25 * 2**20)

def createGitHub( title, root = None):
    title = createRepoTitle( title )
    if not root:
        root = cfg['ROOT_DIR']

    p = pathlib.Path( root ) / pathlib.Path( title )
    cfg['GITHUB_DIR'] = p
    cfg['GITHUB_AUTHOR'] = None
    if ( ( 'GITHUB' not in cfg )  or ( not cfg['GITHUB'] ) ):
        tok = readGithubToken()
        if not tok:
            return None
        login(tok)
        
    repo = findRepoByName( title )
    if not repo:
        print('Repo', title, 'not found. Creating empty repo')
        user = cfg['GITHUB'].get_user()
        repo = user.create_repo(title)
        if not repo:
            return None

    try:
        contents = repo.get_contents("")
    except GithubException:
        repo.create_file("README.md", "Initial commit", "Update readme file here.", "master")
        contents = repo.get_contents("")
    
    print('repo.name', repo.name, repo.clone_url )
    print( "Contents", contents )

    if p.is_dir():                
        with JBcd( p ):
            print("Executing git pull")
            if ( findBranchByName(repo, "gh-pages") ):
                runCommand( cfg['GIT_CMD'] + " pull origin gh-pages", True )
            
            if ( findBranchByName(repo, "master") ):
                runCommand( cfg['GIT_CMD'] + " pull origin master", True )
            
    else:
        with JBcd( pathlib.Path( root ) ):
            runCommand( cfg['GIT_CMD'] + " clone " + '"' + repo.clone_url + '"' + " " + str(p), True )

        with JBcd( p ):
            
            if ( not findBranchByName(repo, "gh-pages") ):
                print("Creating branch gh-pages")
                runCommand( cfg['GIT_CMD'] + " branch gh-pages", True )
            print("Checking out branch gh-pages")
            runCommand( cfg['GIT_CMD'] + " checkout gh-pages", True )

    with JBcd(p):
        runCommand( cfg['GIT_CMD'] + " remote set-url origin " + modUrl( repo.clone_url, cfg['GITHUB_TOKEN'] ), True )
        runCommand( cfg['GIT_CMD'] + " config user.email jacky.baltes@ntnu.edu.tw", True )
        runCommand( cfg['GIT_CMD'] + " config user.name \"Jacky Baltes\"", True )
        
    with JBcd(p):
        shutil.copyfile( cfg['REVEAL_DIR'] / 'index.html', 'index.html' )
        runCommand( cfg['GIT_CMD'] + " add index.html", True )
        shutil.copyfile( cfg['REVEAL_DIR'] / 'package.json', 'packages.json' )
        runCommand( cfg['GIT_CMD'] + " add packages.json", True )
        for d in ["css", "js", "plugin", "lib" ]:
            pathlib.Path(d).mkdir( parents = True, exist_ok = True )
            distutils.dir_util.copy_tree( cfg['REVEAL_DIR'] / d, d)
            runCommand( cfg['GIT_CMD'] + " add " + str(d), True )
        for d in [ "assets/images", "assets/videos", "assets/sounds" ]:
            pathlib.Path(d).mkdir( parents = True, exist_ok = True )

        for aName in cfg['ASSETS']:
            a = cfg['ASSETS'][aName]
            print('Asset', aName, 'Size', a.getSize(), 'Name', a.getLocalName() )
            if a.getSize() <= MAX_GITHUB_FILE_SIZE:
                print("Copying asset", aName, a.getLocalName() )
                rpath = pathlib.Path(a.getLocalName() ).relative_to(cfg['REVEAL_DIR'])
                shutil.copyfile( a.getLocalName(), str( rpath ) )
                runCommand( cfg['GIT_CMD'] + " add " + str(rpath), False )
                          
        runCommand( cfg['GIT_CMD'] + " commit -a -m \"Commit\"", True )

    with JBcd(p):
        runCommand( cfg['GIT_CMD'] + " push", True )
        runCommand( cfg['GIT_CMD'] + " push --set-upstream origin gh-pages", True )
    
        runCommand( cfg['GIT_CMD'] + " push origin gh-pages", True )
    
    return True
            # if not p.is_dir():
            #     print("cloning {0} from url {1} root {2}".format( dirname, url, root ), 'git command', cfg['GIT_CMD'])
            #     if ( branch ):
            #         bs = " --branch " + branch
            #     else:
            #         bs = ""
                    
            #     cmd = cfg['GIT_CMD'] + " clone " + bs + " " + url + " " + dirname 
            #     os.system( cmd )
            # else:
            #     print("git directory exists")

            # with JBcd( dirname ):
            #     print("Executing git pull")
            #     o = None
            #     try:
            #         o = subprocess.check_output(cfg['GIT_CMD'] + " pull", shell=True)
            #     except subprocess.CalledProcessError:
            #         pass
            #     if ( o ):
            #         print( 'git pull:' + o.decode('utf-8') )
