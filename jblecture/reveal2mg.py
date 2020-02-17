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
import shutil 

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
    def __init__(self, id = "", html = "", dialog = "", next = None ):
        global slideNum
        slideNum = slideNum + 1
        if id == "":
            id = "slide_{0:5d}".format(slideNum)
        self.id = id
        self.html = str( html )
        self.dialog = str( dialog )
        self.children = []
        self.next = None

    def addChild( self, sl ):
        self.children.append( sl )
    
    def __repr__(self):
        s = f"Slide {self.id}\nnext:{self.next}\nHTML:\n{self.html}\nDialog:\n{self.dialog}"
        return s

class MGDocParser():
    def __init__( self, revealRoot, mgRoot ):
        self.revealRoot = pathlib.Path( revealRoot )
        self.mgRoot = pathlib.Path( mgRoot )

        self.slides = []
        self.soup = None
        self.root = None

    def parseIndex0( self, root, soup ):
        for c in soup.find_all("section"):
            print('Found slide', c['id'] )
            slide = c.find( "div", class_ = "jb-slide")
            if ( slide ):
                html = slide
                d = c.find( "aside", class_ = "notes" )
                if ( d ):
                    dialog = self.parseRenpy( d.get_text() )
                    # print("*** dialog", type(dialog), dialog )
                else:
                    dialog = ""
                root.addChild( self.parseIndex0( Slide( c['id'], html, "\n".join(dialog) ), slide ) )
        return root

    def parseIndex( self ):
        fname = self.revealRoot / "index.html"
        with open( fname, "r") as f:
            self.soup = BeautifulSoup( f )
            slides = self.soup.find( "div", class_ = 'slides' )
            self.root = self.parseIndex0( Slide("ROOT", "", "" ), slides )

    def parseRevealDir( self ):
        self.parseIndex( )
        self.parseStyleSheets( )
    
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
                #d = d.replace('"', '\\"').lstrip().rstrip()
                print('d=', d)
                line = ""
                if d:
                    #line = line + '"'
                    line = line + d
                    #line = line + '"'
                    #line = line + ','
                if ( line ):
                    out = out + line + '\n'
            print('**out', out )
        return [ f for f in filter(lambda x: not re.match(r'^\s*$', x), out.splitlines() ) ]
    
    def dialogToStr(self, dialog ):
        s = ""
        for l in dialog:
            s = s + "'"
            s = s + l 
            s = s + "'"
            s = s + ","
            s = s + "\n"
        return s

    def writeMGDirectory( self, mgRoot ):

        lstyles = []
        for s in self.styles:
            shutil.copyfile( s, mgRoot / "css" / s.name )
            lstyles.append( mgRoot / "css" / s.name )
        self.lstyles = lstyles
        
        slideDir = mgRoot / "dialog"
        slideDir.mkdir( parents = True, exist_ok = True )
        dialogFiles = []

        with cd( slideDir ):
            stack = [ s for s in self.root.children ]
            while len(stack) > 0:
                n = stack.pop()
                print('Slide', n)
                if n.dialog or n.html:
                    fname = n.id + ".js"
                    if n.html is not None:
                        html = n.html
                    else:
                        html = ""
                    if n.dialog:
                        dialog = self.dialogToStr( n.dialog.splitlines() )
                    else:
                        dialog = ""
                    print("DIA", type(n.dialog), n.dialog, dialog )

                    if not n.next:
                        nxt = n.next
                    else:
                        nxt = "Start"

                    print('Writing file', fname )
                    with open( fname, "w" ) as f:
                        s = """
monogatari.asset('scenes', 'scene-{id}',
   [ "", `
   {html}
   `]
);

monogatari.script()["{id}"] = [ 
    "show scene scene-{id}",
    {dialog}
    "jump {next}"
];
                        """.format( dialog=dialog, html=html, id=n.id, next=nxt )
                        f.write( s )
                        
                        dialogFiles.append( slideDir / fname )

                for c in n.children:
                    stack.append(c)       

    def parseStyleSheets( self ):
        styles = []
        for lnk in self.soup.find_all("link"):
            print('rel', lnk['rel'] )
            if lnk['rel'] == ["stylesheet"]:
                styles.append( self.mgRoot / lnk['href'] )
        self.styles = styles

        return styles

def fetchMGData( mgRoot, dir ):
    updateGit( "https://github.com/cvroberto21/Monogatari", "Monogatari", "develop", mgRoot  )
    dir.mkdir( parents = True, exist_ok = True )
    copy_tree( str( mgRoot / "Monogatari" / "dist" ), str( dir ) ) 

def setupNPM( dir ):
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

def installNPMCanopy( dirname ):
    with cd( dirname ):
        print("Executing npm install")
        o = None
        try:
            o = subprocess.check_output("npm install --save-dev canopy", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            pass
        if ( o ):
            print( 'npm install canopy:' + o.decode('utf-8') )

def installNPM( dirname ):
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
    revealRoot = pathlib.Path( args[0] )
    mgRoot = pathlib.Path( args[1] )
    fetchMGData( pathlib.Path(".."), args[1] )    
    parser = MGDocParser( revealRoot, mgRoot )
    parser.parseRevealDir( )
    
    parser.printTree( )
    parser.writeMGDirectory( mgRoot )
    print('Styles', styles )
    
if __name__ == "__main__":
    cwd = pathlib.Path(".").resolve()
    main( [ cwd / "Test-Implementation", cwd / "mg-test" ] )