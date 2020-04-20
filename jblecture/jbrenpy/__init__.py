import pathlib
import logging
import subprocess
import os
import sys
import shutil
import math
from PIL import Image

logger = logging.getLogger( __name__ )
logger.setLevel( logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def createEnvironment( mycfg ):
    global cfg
    defaults = {}
    defaults['ROOT_DIR'] = pathlib.Path( "/data/test" )
    defaults['CHARACTER_DIR']  = pathlib.Path( defaults['ROOT_DIR'] ) / "Characters"
    defaults['GIT_CMD'] = "git"

    mycfg = { **defaults, **mycfg }
    cfg = mycfg
    return cfg

class JBcd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = pathlib.Path(newPath).expanduser().resolve()

    def __enter__(self):
        self.savedPath = pathlib.Path.cwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def updateGit( cfg, url, dirname, branch,  root ):
    with JBcd( root ):
        logger.debug( f"Switching to directory {root}")
        p = pathlib.Path( dirname )
        if not p.is_dir():
            logger.debug("cloning {0} from url {1} root {2}".format( dirname, url, root ) )
            logger.debug( 'git command ' + cfg['GIT_CMD'] )
            if ( branch ):
                bs = [" --branch", branch ]
            else:
                bs = []
            subprocess.run( [ cfg['GIT_CMD'],"clone" ] + bs + [ url, dirname ] )
        else:
            logger.info( f"git directory {p} exists" )

        with JBcd( dirname ):
            logger.info("Executing git pull")
            o = None
            try:
                o = subprocess.check_output(cfg['GIT_CMD'] + " pull", stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError:
                pass
            if ( o ):
                logger.debug( 'git pull:' + o.decode('utf-8') )

class Character:
    def __init__(self, name, width, height, url, color = '#808020' ):
        cdir = pathlib.Path( cfg['CHARACTER_DIR'] )
        cdir.mkdir( parents=True, exist_ok=True )

        updateGit( cfg, url, name, None, cfg['CHARACTER_DIR']  )
        self.characterDir = cdir
        self.name = name
        self.width = width
        self.height = height

    def autocrop( self, img ):
        cropped = None
        bbox = img.getbbox()
        if bbox:
            cropped = img.crop( bbox )
        return cropped

    def resize( self, img, width, height, keepAspect = True ):
        iw,ih = img.size
        aspect = iw/ih
        if width == 0:
            width = height * aspect
        if height == 0:
            height = width / aspect
        if width > 0 and height > 0:
            if width / iw < height / ih * aspect:
                nw = width
                nh = ih * width / iw 
            else:
                nh = height
                nw = iw * height / ih

            logger.debug( f"resize {self.name}: {iw}x{ih} {aspect} -> {nw}x{nh}" )
            img = img.resize( (int(round(nw)), int(round(nh)) ), Image.LANCZOS  )

        return img

    def prepareImages( self, cdir, gPat="./**/*.png" ):
        logger.debug( f"Looking for images in {self.characterDir}" )
        trg = pathlib.Path( cdir ) / self.name / "images" 
        trg.mkdir( parents=True, exist_ok=True )

        for img in pathlib.Path( self.characterDir ).glob( gPat ):
            name = img.with_suffix('').name
            suffix = img.suffix
            comp = name.split( '_' )

            comp.sort()

            logger.debug( f"Found image {img} name {name} suffix {suffix} comp {comp}" )
            src = Image.open( img )
            cropped = self.autocrop( src )
            cropped = self.resize( cropped, self.width, self.height )
            if cropped:
                dst = trg / ("_".join(comp) + ".png")
                cropped.save(  dst, "PNG" )    
            else:
                logger.warning( f"Skipping empty image {img}")

if __name__ == "__main__":
    defaults = {}
    defaults['ROOT_DIR'] = pathlib.Path( "/data/test" )
    defaults['CHARACTER_DIR']  = pathlib.Path( defaults['ROOT_DIR'] ) / "Characters"
    defaults['GIT_CMD'] = "git"
    createEnvironment( defaults )
    jb = Character( "profjb", 320, 240, url="https://github.com/cvroberto21/profjb.git" )
    jb.prepareImages( "/tmp/profJB")