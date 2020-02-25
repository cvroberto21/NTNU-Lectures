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
import logging

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
        self.renpyStyle = ""
        self.children = []
        self.next = None

    def addChild( self, sl ):
        self.children.append( sl )
    
    def __repr__(self):
        s = f'id:{self.id} next:{self.next}\nHTML:\n{self.html}\nDialog:\n{self.dialog}'
        return s

class MGDocParser():
    def __init__( self, revealRoot ):
        self.revealRoot = pathlib.Path( revealRoot )

        self.slides = []
        self.soup = None
        self.root = None

    def parseIndex0( self, root, soup ):
        prev = None
        for slide in soup.find_all("section"):
            logging.info('Found slide '+ str( slide['id'] ) )

            html = []
            dialog = []
            for c in slide.find_all( recursive = False ):
                logging.info("Soup c " + str( c.name ) )
                if c.name != "aside":
                    html.append( str(c) )
                else:
                    dialog.extend( self.parseRenpy( c.get_text() ) )
            logging.debug('HTML ' + str( html ) )
            logging.debug('dialog ' + str( dialog ) )
            sl = Slide( slide['id'], "\n".join( html ), "\n".join(dialog) )
            if prev:
                prev.next = sl.id
            root.addChild( self.parseIndex0( sl, slide ) )
            self.slides.append( sl )
            prev = sl
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
                logging.debug('d=' + str(d) )
                line = ""
                if d:
                    #line = line + '"'
                    line = line + d
                    #line = line + '"'
                    #line = line + ','
                if ( line ):
                    out = out + line + '\n'
            logging.debug('**out ' + str( out ) )
        return [ f for f in filter(lambda x: not re.match(r'^\s*$', x), out.splitlines() ) ]
    
    def dialogToStr(self, dialog ):
        pre = ""
        s = ""

        for l in dialog:
            m = re.match( r"^\s*//\s*args\s*=\s*(?P<args>.*)$", l)
            if m:
                pre = pre + m.group('args') + '\n'
            else:
                s = s + "'"
                s = s + l 
                s = s + "',\n"
        return pre, s

    def copyAssets(self, mgRoot ):
        copy_tree( str( self.revealRoot / "assets" ), str( mgRoot / "assets" ) )

    def patchMGIndex( self, fname ):
        with open( fname, "r" ) as f:
            index = f.readlines()

        for i,line in enumerate( index ):
            if re.match( '\s*<link rel="stylesheet" href="./style/main.css">\s*', line ):
                logging.debug( "Inserting stylesheets at index " +  str(i) )
                for s in self.styles:
                    index.insert( i+1, '        <link rel="stylesheet" href="{href}">\n'.format(href=s['href']))

        for i,line in enumerate( index ):
            if re.match( '\s*<script src="./js/main.js"></script>\s*', line ):
                logging.debug( "Inserting scenes at index "  +  str(i) )
                out = i + 1
                for j,s in enumerate( self.slides ):
                    index.insert( out + j, '        <script src="./scenes/{d}.js"></script>\n'.format(d=s.id))

        for i,line in enumerate( index ):
            if re.match( '\s*</head>\s*', line ):
                logging.debug("Inserting mathjax libraries at index" + str(i) )
                index.insert( i, """
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                    """)
                break

        with open( fname, "w" ) as f:
            f.writelines( index )

        return index

    def writeMGDirectory( self, mgRoot ):
        print("ROOT", self.revealRoot)
        for s in self.styles:
            rp = self.revealRoot / s['href']
            mp = mgRoot / s['href'] 
            mp.parent.mkdir(parents = True, exist_ok=True)
            print("s", s,  s.href, str( self.revealRoot / s['href'] ) )
            shutil.copyfile( str( rp ), str( mp ) )
        
        slideDir = mgRoot / "scenes"
        slideDir.mkdir( parents = True, exist_ok = True )
        sceneFiles = []

        with cd( slideDir ):
            stack = [ s for s in self.root.children ]
            stack.reverse()

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
                        args, dialog = self.dialogToStr( n.dialog.splitlines() )
                    else:
                        dialog = self.dialogToStr( [ "pause" ] )
                    print("DIA", type(n.dialog), n.dialog, dialog )

                    if n.next:
                        nxt = n.next
                    else:
                        nxt = "Start"

                    print('Writing file', fname )
                    with open( fname, "w" ) as f:
                        s = """
monogatari.asset('scenes', 'scene-{id}',
   [ "", `
   <div class="reveal">
   <div class="slides">
   {html}
   </div>
   </div>
   `]
);

monogatari.script()["{id}"] = [ 
    "show scene scene-{id} {args}",
    {dialog}
    "jump {next}"
];
                        """.format( dialog=dialog, html=html, id=n.id, next=nxt, args=args )
                        f.write( s )
                        
                        sceneFiles.append( slideDir / fname )

                for i in range( len(n.children) - 1, -1, -1 ):
                    stack.append( n.children[i] )
        self.copyAssets( mgRoot )       
        self.patchMGIndex( mgRoot / "index.html" )

    def parseStyleSheets( self ):
        styles = []
        for lnk in self.soup.find_all("link"):
            print('rel', lnk['rel'] )
            if lnk['rel'] == ["stylesheet"]:
                styles.append( lnk )
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
    parser = MGDocParser( revealRoot )
    parser.parseRevealDir( )
    
    parser.printTree( )
    parser.writeMGDirectory( mgRoot )
    
if __name__ == "__main__":
    cwd = pathlib.Path(".").resolve()
    main( [ cwd / "Test-Implementation", cwd / "mg-test" ] )