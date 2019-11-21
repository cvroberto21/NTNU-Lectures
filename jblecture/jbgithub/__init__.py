from github import Github
import os
import getpass
import pathlib
from ..jbcd import JBcd
import subprocess
import distutils
import shutil

cfg = {}

def createEnvironment( mycfg ):
    global cfg
    cfg = mycfg
    cfg['GITHUB'] = None
    return cfg


def readGithubToken():
    passwd = getpass.getpass("Github Token:")    
    return passwd

def login( token ):
    g = Github( token )
    cfg['GITHUB'] = g
    return g

def getRepositories( ):
    repos = None
    if 'GITHUB' not in cfg or cfg['GITHUB'] is None:
        login( readGithubToken() )
    if 'GITHUB' in cfg and cfg['GITHUB']:
        repos = cfg['GITHUB'].get_user().get_repos()
    return repos

def createRepoTitle( title ):
    return tite.replace(" ", "-")

def findRepoByName( title ):
    repo = None
    if 'GITHUB' in cfg and cfg['GITHUB']:
        repos = getRepositories()
        if repos:
            for r in repos:
                if r.name == title:
                    repo = r
                    break
    return repo


def runCommand( cmd ):
    print( "Running command " + cmd )
    o = None
    try:
        o = subprocess.check_output( cmd, shell=True)
    except subprocess.CalledProcessError:
        pass
    if ( o ):
        print( "Output " + cmd + ":\n" + o.decode('utf-8') )

def createGitHub(title, root ):
    title = createRepoTitle( tite )
    
    p = pathlib.Path( root ) / pathlib.Path( title )
    cfg['GITHUB_DIR'] = p

    if ( ( 'GITHUB' not in cfg )  or ( not cfg['GITHUB'] ) ):
        tok = readGithubToken()
        if not tok:
            return None

        cfg['GITHUB'] = login(tok)

    repo = findRepoByName( title )
    if not repo:
        print('Repo', title, 'not found. Creating empty repo')
        user = cfg['GITHUB'].get_user()
        repo = user.create_repo(title)

    print('repo.name', repo.name )
    if p.is_dir():                
        with JBcd( p ):
            print("Executing git pull")
            runCommand( cfg['GIT_CMD'] + " pull gh-pages" )
    else:
        p.mkdir( parents=True, exist_ok= True )
        with JBcd( pathlib.Path( root ) ):
            runCommand( cfg['GIT_CMD'] + " clone " + '"' + repo.name + '"' + " ." )
        
        with JBcd( p ):
            runCommand( cfg['GIT_CMD'] + " checkout gh-pages" )
        
    with JBcd(p):
        shutil.copyfile( cfg['REVEAL_DIR'] / 'index.html', 'index.html' )
        for d in ["css", "js", "assets", "plugin" ]:
            distutils.dir_util.copy_tree( cfg['REVEAL_DIR'] / d, d)
        runCommand( cfg['GIT_CMD'] + " add ." )
        runCommand( cfg['GIT_CMD'] + " commit -m \"Commit\"" )
        runCommand( cfg['GIT_CMD'] + " push origin" )
    
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