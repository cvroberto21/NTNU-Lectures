"""
A module that converts a reveal slideshow to a monogatari visual novel.
"""
from bs4 import BeautifulSoup
import sys
import re
import pathlib
import argparse
from distutils.dir_util import copy_tree
import os
import subprocess 

try:
    GIT_CMD
except NameError:
    GIT_CMD = 'git'
    
slideNum = 0

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = pathlib.Path(newPath).expanduser().resolve()

    def __enter__(self):
        self.savedPath = pathlib.Path.cwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class Slide:
    def __init__(self, id = "", html = "", dialog = "" ):
        global slideNum
        slideNum = slideNum + 1
        if id == "":
            id = "slide_{0:5d}".format(slideNum)
        self.id = id
        self.html = html
        self.dialog = dialog
        self.children = []

    def addChild( self, sl ):
        self.children.append( sl )

class MGDocParser():
    def __init__(self):
        self.slides = []
        self.soup = None
        self.root = None

    def parseFile0( self, root, soup ):
        for c in soup.find_all("section"):
            #print('Found slide', c['id'] )
            slide = c.find( "div", class_ = "jb-slide")
            if ( slide ):
                html = slide
                d = c.find( "aside", class_ = "notes" )
                if ( d ):
                    dialog = self.parseRenpy( d.get_text() )
                else:
                    dialog = ""
                root.addChild( self.parseFile0( Slide( c['id'], html, dialog ), slide ) )
        return root

    def parseFile( self, fname ):
        with open( fname, "r") as f:
            self.soup = BeautifulSoup( f )
            slides = self.soup.find( "div", class_ = 'slides' )
            self.root = self.parseFile0( Slide("ROOT", "", "" ), slides )

    def printTree( self, node = None, level = 0 ):
        if not node:
            node = self.root
        #print("type", type(node))
        print("   " * level, node.id )
        #print("   " * level, node.html )
        print("   " * level, node.dialog )
        for c in node.children:
            self.printTree( c, level + 1 )

    def parseRenpyLine( line ):
        pass

    def parseRenpy(self, dialog ):
        out = ""
        for d in dialog.splitlines():
            if not re.match(r'^\s*$', d):
                d = d.replace('"', '\\"').lstrip().rstrip()
                print('d=', d)
                line = ""
                if d:
                    line = line + '"'
                    line = line + d
                    line = line + '"'
                    line = line + ','
                if ( line ):
                    out = out + line + '\n'
        return [ f for f in filter(lambda x: not re.match(r'^\s*$', x), out.splitlines() ) ]
    
    def dialogToStr(self, dialog ):
        s = ""
        for l in dialog:
            s += l + "\n"
        return s

    def writeMGDirectory( self, dir ):
        slideDir = dir / "dialog"
        slideDir.mkdir( parents = True, exist_ok = True )
        dialogFiles = []

        with cd( slideDir ):
            stack = [ s for s in self.root.children ]
            first = True
            while len(stack) > 0:
                n = stack.pop()
                if not first:
                    id = n.id
                else:
                    id = 'Start'
                if n.dialog:
                    fname = id + ".js"
                    print('Writing file', fname )
                    with open( fname, "w" ) as f:
                        s = """
script["{id}"] = [
{dialog}
]
                        """.format( dialog=self.dialogToStr( n.dialog ), id=n.id )
                        f.write( s )
                        
                        dialogFiles.append( slideDir / fname )

                for c in n.children:
                    stack.append(c)       

def fetchMGData( mgHome, dir ):
    updateGit( "https://github.com/Monogatari/Monogatari.git", "Monogatari", "", mgHome  )
    dir.mkdir( parents = True, exist_ok = True )
    copy_tree( str( mgHome / "Monogatari" / "dist" ), str( dir ) ) 
    installNPMCanopy( dir )
    installNPM( dir )

def updateGit( url, dirname, branch,  root ):
        with cd( root ):
            p = pathlib.Path( dirname )
            if ( branch ):
                bs = " --branch " + branch
            else:
                bs = ""
            if not p.is_dir():
                print("cloning {0} from url {1} root {2}".format( dirname, url, root ), 'git command', GIT_CMD)
                    
                cmd = GIT_CMD + " clone " + bs + " " + url + " " + dirname 
                os.system( cmd )
            else:
                print("git directory exists")

            with cd( dirname ):
                print("Executing git pull")
                o = None
                try:
                    o = subprocess.check_output(GIT_CMD + " pull", stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError:
                    pass
                if ( o ):
                    print( 'git pull:' + o.decode('utf-8') )

def npmInstallCanopy( dirname ):
    with cd( dirname ):
        print("Executing npm install")
        o = None
        try:
            o = subprocess.check_output("npm install --save-dev canopy", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            pass
        if ( o ):
            print( 'npm install canopy:' + o.decode('utf-8') )

def npmInstall( dirname ):
    with cd( dirname ):
        print("Executing npm install")
        o = None
        try:
            o = subprocess.check_output("npm install", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            pass
        if ( o ):
            print( 'npm install' + o.decode('utf-8') )

def compileGrammar( dirname, grammar, lang ):
    with cd( dirname ):
        print("Executing canopy", grammar, 'language', lang )
        o = None
        try:
            o = subprocess.check_output(f"canopy {grammar} --lang {lang}", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            pass
        if ( o ):
            print( 'canopy output' + o.decode('utf-8') )

def main( args = None ):
    if args is None:
        args = sys.argv[1:]
    fetchMGData( pathlib.Path("..") / "Monogatarai", args[1] )    
    parser = MGDocParser()
    parser.parseFile( args[0] )
    parser.printTree( )
    parser.writeMGDirectory( args[1] )
    
if __name__ == "__main__":
    cwd = pathlib.Path(".").resolve()
    main( [ cwd / "reveal.js" / "index.html", cwd / "mg-test" ] )