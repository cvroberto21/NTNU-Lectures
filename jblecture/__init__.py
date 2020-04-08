# -*- coding: utf-8 -*-
"""
"""

import pathlib
import os
import platform
import subprocess
import glob
import shutil
import importlib
import sys
import zipfile
from distutils.dir_util import copy_tree
import textwrap
import logging
import tempfile
import base64 

from .jbcd import JBcd

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

defaults = {}
defaults['TITLE'] = '{title}'
defaults['HOME_DIR'] = pathlib.Path.home().resolve()
defaults['ORIG_ROOT'] = pathlib.Path('.').resolve()
defaults['ROOT_DIR'] = defaults['ORIG_ROOT'] / 'BuildDir'
defaults['GDRIVE_ROOT'] = '/gDrive/My Drive'
defaults['MODULE_ROOT'] = defaults['ORIG_ROOT'] / 'NTNU-Lectures'

defaults['REVEAL_DIR'] = defaults['ROOT_DIR'] / "reveal.js" 

defaults['REVEAL_CSS_DIR'] = defaults['REVEAL_DIR'] / "css"
defaults['REVEAL_JS_DIR'] = defaults['REVEAL_DIR'] / "js"
defaults['REVEAL_THEME_DIR'] = defaults['REVEAL_CSS_DIR'] / "theme"
defaults['REVEAL_ASSETS_DIR'] = defaults['REVEAL_DIR'] / "assets"
defaults['REVEAL_IMAGES_DIR'] = defaults['REVEAL_ASSETS_DIR'] / "images"
defaults['REVEAL_VIDEOS_DIR'] = defaults['REVEAL_ASSETS_DIR'] / "videos"
defaults['REVEAL_SOUNDS_DIR'] = defaults['REVEAL_ASSETS_DIR'] / "sounds"

defaults['RENPY_GAME_DIR'] = defaults['ROOT_DIR'] / "renpy" / "game"
defaults['RENPY_ASSETS_DIR'] = defaults['RENPY_GAME_DIR'] / "assets"
defaults['RENPY_IMAGES_DIR'] = defaults['RENPY_ASSETS_DIR'] / "images"
defaults['RENPY_SOUNDS_DIR'] = defaults['RENPY_ASSETS_DIR'] / "sounds"
defaults['RENPY_VIDEOS_DIR'] = defaults['RENPY_ASSETS_DIR'] / "videos"

defaults['MG_GAME_DIR'] = defaults['ROOT_DIR'] / "Monogatari"
defaults['MG_ASSETS_DIR'] = defaults['MG_GAME_DIR'] / "assets"
defaults['MG_IMAGES_DIR'] = defaults['MG_ASSETS_DIR'] / "images"
defaults['MG_SOUNDS_DIR'] = defaults['MG_ASSETS_DIR'] / "sounds"
defaults['MG_VIDEOS_DIR'] = defaults['MG_ASSETS_DIR'] / "videos"

defaults['GIT_CMD'] = 'git'

defaults['GOOGLE_COLAB'] = False

defaults['HTTP_PORT'] = None

defaults['CHARACTERS'] = dict()

cfg = {}

try:
    from google.colab import files
    defaults['GOOGLE_COLAB'] = True
except ImportError:
    defaults['GOOGLE_COLAB'] = False

# Reveal.js Parameters
defaults['REVEAL_THEME'] = 'ntnuerc'

with open( defaults['MODULE_ROOT'] / 'html' / 'index_template.html') as f:
    defaults['REVEAL_PRESENTATION_TEMPLATE'] = f.read()

defaults['REVEAL_SLIDE_TEMPLATE'] = """
<section id="{{id}}" data-state="{{id}}">

{{slideHTML}}

<aside class="notes">
{{slideNote}}
</aside>

{{slideChildren}}

</section>
"""

defaults['REVEAL_SLIDE_FOOTER'] = """
<div class="jb-footer-left plain">
    {{ cfg['ASSETS']['logo']( cls="jb-footer-left-img plain" ) }}
</div>
<div class="jb-footer-right plain">
    {{ cfg['ASSETS']['robbi']( cls="jb-footer-right-img plain" ) }}
</div>
"""

defaults['REVEAL_SLIDE_HEADER'] = """  
"""

defaults['REVEAL_SLIDE_BACKGROUND'] = """
"""

# RENPY Parameters
defaults['RenpyInitTemplate'] = """
define jb = Character("Prof. Jacky Baltes", color="#06799f", callback=speaker("jb"))
define gc = Character("Student G.C.", color="#069f67", callback=speaker("gc"))
define msG = Character("Student G.", color="#069f67", callback=speaker("msG"))

label start:
    show jb neutral at center with dissolve
    
    # Prof. Jacky's Introduction
    jb "Hello! I am Prof. Jacky Baltes."
    
    show jb neutral at center:
        linear 2.0 left
        
    jb "This project describes {{title}}."

    
    jump {{startId}}
"""

defaults['RenpyScriptTemplate'] = """
# Slide {{id}}
label {{label}}:
    scene bg {{id}} with {{transition}}
{{renpy}}
    jump {{right}}
"""

defaults['RenpyTransition'] = "fade"
defaults['RenpyInitLabel'] =  ".init"
defaults['PAGE_SIZE'] = [ int(1280), int (720) ]

def updateGit( cfg, url, dirname, branch,  root ):
    from .jbcd import JBcd
    with JBcd( root ):
        p = pathlib.Path( dirname )
        if not p.is_dir():
            logger.debug("cloning {0} from url {1} root {2}".format( dirname, url, root ) )
            logger.debug( 'git command ' + cfg['GIT_CMD'] )
            if ( branch ):
                bs = " --branch " + branch
            else:
                bs = ""
                
            cmd = cfg['GIT_CMD'] + " clone " + bs + " " + url + " " + dirname 
            os.system( cmd )
        else:
            logger.info("git directory exists")

        with JBcd( dirname ):
            logger.info("Executing git pull")
            o = None
            try:
                o = subprocess.check_output(cfg['GIT_CMD'] + " pull", stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError:
                pass
            if ( o ):
                logger.debug( 'git pull:' + o.decode('utf-8') )

def loadModules( cfg ):
    logger.info('Loading Modules' + str( cfg['MODULE_ROOT'] ) )
    if cfg['MODULE_ROOT'] not in sys.path:
        sys.path.append( str( cfg['MODULE_ROOT']  ) )
    logger.debug('sys.path %s', sys.path )    

    from .jbcd import JBcd

    from .jbdata import createEnvironment, JBImage, JBVideo
    cfg = jbdata.createEnvironment( cfg )

    from .jbslide import createEnvironment, JBSlide
    cfg = jbslide.createEnvironment( cfg )

    from .jbmagics import createEnvironment, JBMagics
    cfg = jbmagics.createEnvironment( cfg )

    from .jbdocument import createEnvironment, JBDocument
    cfg = jbdocument.createEnvironment( cfg )

    from .jbgithub import createEnvironment, login, getRepositories
    cfg = jbgithub.createEnvironment( cfg )

    from .jbgoogle import createEnvironment
    cfg = jbgoogle.createEnvironment( cfg )
    
    logger.info('Loading of modules finished')
    return cfg

def createEnvironment( params = {} ):
    cfg = { **defaults, **params }
    logger.debug('Title ' + cfg['TITLE'] )
    cfg['ROOT_DIR'].mkdir(parents = True, exist_ok = True )

    node = platform.node()

    for p in [ "pygments", "youtube-dl", "jinja2", "papermill", "pytexturepacker", "patch", "requests_oauthlib", "PyGithub", "gitpython" ]:
        try:
            importlib.import_module( p )
        except ModuleNotFoundError:
            logger.debug('Using pip to install missing dependency ' +  p )
            os.system("python -m pip" + " install " + p )

    cfg = loadModules( cfg )

    updateGit( cfg, "https://github.com/hakimel/reveal.js.git", "reveal.js", "", cfg['ROOT_DIR'] )

    # 'decktape',
    for pkg in []: #[  'scenejs' ]:            
        with JBcd( cfg['REVEAL_DIR']  ):
            logger.info( f"Executing npm install {pkg}" )
            o = None
            try:
                o = subprocess.check_output( f"npm install {pkg}", stderr=subprocess.STDOUT, shell = True)
            except subprocess.CalledProcessError:
                pass
            if ( o ):    
                logger.info( f'npm install {pkg}:' + o.decode('utf-8') )

    for d in [ cfg['REVEAL_IMAGES_DIR'], cfg['REVEAL_VIDEOS_DIR'], cfg['REVEAL_SOUNDS_DIR'] ]:
        d.mkdir( parents = True, exist_ok=True )
    
    fetchRenpyData( cfg )

    shutil.copy2( cfg['ORIG_ROOT'] / 'NTNU-Lectures' / 'html' / 'ntnuerc.css' , 
        cfg['REVEAL_THEME_DIR'] / 'ntnuerc.css'  )
    shutil.copy2( cfg['ORIG_ROOT'] / 'NTNU-Lectures' / 'html' / 'fira.css' , 
        cfg['REVEAL_THEME_DIR'] / 'fira.css'  )
    shutil.copy2(  cfg['ORIG_ROOT'] / 'NTNU-Lectures' / "images" / "ntnuerc-logo-1.png", 
        cfg['REVEAL_IMAGES_DIR'] / 'robbi.png' )
    shutil.copy2(  cfg['ORIG_ROOT'] / 'NTNU-Lectures' / "images" / "ntnu-ee-logo.png", 
        cfg['REVEAL_IMAGES_DIR']  / 'logo.png')
    shutil.copy2(  cfg['ORIG_ROOT'] / 'NTNU-Lectures' / "images" / "FIRA-logo-1.png", 
        cfg['REVEAL_IMAGES_DIR']  / 'FIRA-logo-1.png')
    shutil.copy2(  cfg['ORIG_ROOT'] / 'NTNU-Lectures' / "images" / "pairLogo.png", 
        cfg['REVEAL_IMAGES_DIR']  / 'pairLogo.png')
    
    # Copy html, js, and css artefacts
    shutil.copy2(  cfg['ORIG_ROOT'] / 'NTNU-Lectures' / "html" / "ntnu.js", 
        cfg['REVEAL_JS_DIR']  / 'ntnu.js')
    
    fetchMGData( cfg )

    cfg['ASSETS'] = {}

    cfg['ASSETS']['robbi'] = jbdata.JBImage( name = 'robbi', width=162, height=138, localFileStem= str( cfg['REVEAL_IMAGES_DIR']  / "robbi" ), suffix="png" )
    cfg['ASSETS']['logo'] = jbdata.JBImage( name = 'logo', width=0, height=0, localFileStem= str( cfg['REVEAL_IMAGES_DIR'] / "logo" ), suffix="png" )
    cfg['ASSETS']['fira-logo-1'] = jbdata.JBImage( name = 'fira-logo-1', width=0, height=0, localFileStem= str( cfg['REVEAL_IMAGES_DIR'] / "FIRA-logo-1"), suffix="png" )
    cfg['ASSETS']['pairLogo'] = jbdata.JBImage( name = 'pairLogo', width=0, height=0, localFileStem= str( cfg['REVEAL_IMAGES_DIR'] / "pairLogo" ), suffix="png" )

    ratio = 1.0
    cssStr = """
        @page {{
            size: {width}px {height}px;
            margin: 0px;
        }}""".format(width=cfg['PAGE_SIZE'][0], height=cfg['PAGE_SIZE'][1])
    doc = createDocument( cfg )
    cfg['doc'] = doc
    return cfg

def createDocument( cfg ):
    doc = jbdocument.JBDocument()
    return doc

def zipDirectory( archive, dir, root = '.' ):
    with JBcd(root):
        xroot = dir

        with zipfile.ZipFile( archive, 'w', zipfile.ZIP_DEFLATED, True ) as zf:
            zf.Debug = 3
            for root, dirs, files in os.walk( xroot ):
                #print(root, dirs, files )

                for f in files:
                    zf.write( pathlib.Path( root ).joinpath( f ) )

                for rdir in [ '.git', 'node_modules' ]:
                    if ( rdir in dirs ):
                        dirs.remove( rdir )

        #print('Zipping Files', filesList)

        with zipfile.ZipFile( archive, 'r' ) as zf:
            zf.namelist()

def downloadDir( zFile, dir, root = None  ):        
    zipDirectory(  zFile, dir, root )
    if cfg['GOOGLE_COLAB']:
        print("Downloading file", zFile )
        files.download( zFile )

def fetchRenpyData( cfg ):
#    os.system("sudo apt install renpy") 
    updateGit( cfg, "https://github.com/guichristmann/Lecture-VN.git", "Lecture-VN", "", cfg['ORIG_ROOT'] )
    src = cfg['ORIG_ROOT'] / 'Lecture-VN' / 'Resources' / 'templateProject' / 'game'
    cfg['RENPY_GAME_DIR'].mkdir(parents = True, exist_ok = True )
    with JBcd( cfg['RENPY_GAME_DIR'] ):
        logger.info("Creating renpy directory in " + str( cfg['RENPY_GAME_DIR'] ) )
        for d in [ cfg['RENPY_IMAGES_DIR'], cfg['RENPY_IMAGES_DIR'] / "slides", cfg['RENPY_SOUNDS_DIR'], cfg['RENPY_VIDEOS_DIR'], "renpy/game/tl" ]:
            pathlib.Path(d).mkdir( parents = True, exist_ok = True )
    
    for f in [ 'characters.rpy', 'gui.rpy', 'options.rpy', 'screens.rpy', 'script.rpy', 'transforms.rpy' ]:
        shutil.copy2( src / f, cfg['RENPY_GAME_DIR'] / f )
    #shutil.copytree(  src / "images" / "Characters", cfg['RENPY_IMAGES_DIR'] / "characters" )
    copy_tree( str( src / "gui" ), str( cfg['RENPY_GAME_DIR'] / "gui" ) )
    copy_tree( str( src / "images" / "Characters" ), str( cfg['RENPY_IMAGES_DIR'] / "characters" ) )

def fetchMGData( cfg ):
    updateGit( cfg, "https://github.com/cvroberto21/Monogatari", "Monogatari", "develop", cfg['ORIG_ROOT'] )
    copy_tree( str( cfg['ORIG_ROOT'] / "Monogatari" / "dist" ), str( cfg['MG_GAME_DIR'] ) ) 
            
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # This class must then be registered with a manually created instance,
    # since its constructor has different arguments from the default:

    global cfg
    cfg = createEnvironment( {} )
    magics = jbmagics.JBMagics( ipython, cfg['doc'] )
    cfg['user_ns'] = magics.shell.user_ns
    ipython.register_magics(magics)

# Functions that should be exported
def addJBImage( name, width, height, url=None, data=None, localFileStem=None, suffix=None ):
    img = jbdata.JBImage( name, width, height, url, data, localFileStem, suffix )
    cfg['ASSETS'][img.name] = img
    return img

def addJBVideo( name, width, height, url=None, data=None, localFileStem=None, suffix=None ):
    vid = jbdata.JBVideo( name, width, height, url, data, localFileStem, suffix )
    cfg['ASSETS'][vid.name] = vid
    return vid

def addJBData( name, url=None, data=None, localFileStem=None, suffix="dat" ):
    dat = jbdata.JBData( name, url, data, localFileStem, suffix )
    cfg['ASSETS'][dat.name] = dat
    return dat

def addJBCharacter( name, data = None ):
    if data:
        cfg['CHARACTERS'][name] = data
        ret = data
    else:
        ret = cfg['CHARACTERS'][name]
        del cfg['CHARACTERS'][name]
    return ret
    
def addJBFigure( name, width, height, fig, suffix = "svg" ):
    if suffix == "svg":
        img = createSVGImageFromFigure( fig )
        f = addJBImage( name, width, height, data = img.encode('utf-8'), suffix = "svg" )
    elif suffix == "png":
        img = createBase64ImageFromFigure( fig )
        f = addJBImage( name, width, height, data = img, suffix = "png" )
    else:
        raise Exception( "addJBFigure unknown suffix " + suffix )
    return f

def addJBGraph( name, width, height, g, suffix = "svg" ):
    if suffix == "svg":
        g.format = "svg"
        img = g.pipe().decode('utf-8')
        g.format = saveFormat
        f = addJBImage( name, width, height, data = img.encode('utf-8'), suffix = "svg" )
    elif suffix == "png":
        saveFormat = g.format
        g.format('png')
        img = g.pipe()
        g.format = saveFormat
        f = addJBImage( name, width, height, data = img, suffix = "png" )
    else:
        raise Exception( "addJBFigure unknown suffix " + suffix )

    return f

def addJBAnimation( name, width, height, anim, suffix="mp4"):
    aName = cfg['REVEAL_VIDEOS_DIR'] / name + "." + suffix
    anim.save( aName )
    v = addJBVideo( name, width, height, localFileStem=aName, suffix=suffix )
    return v

tableT = """
<table style="text-align: left; width: 100%; font-size:0.4em" border="1" cellpadding="2"
cellspacing="2"; border-color: #aaaaaa>
{0}
<tbody>
{1}
</tbody>
</table>
"""

trT = """
<tr>
{0}
</tr>
"""

tdT = """
<td style="vertical-align: top;">
{0}
</td>
"""

thT = """
<th>
{0}
</th>
"""

def createTable( data, index = None, columns = None, tableT = tableT, thT = thT, tdT = tdT, trT = trT ):
    if columns:
        cdata = """
        <thead>
          <tr>
        """
        for c in columns:
            cdata = cdata + thT.format(c)
        cdata = cdata + """
          </tr>
        </thead>
        """
    else:
        cdata = ""

    bdata = ""
    for i,r in enumerate( data ):
        rdata = ""
        for j,d in enumerate( r ):
            rdata = rdata + tdT.format( d )
        row = trT.format( rdata )
        #print(row)
        bdata = bdata + row
    #/print(bdata)
    table = tableT.format( cdata, bdata )
    return table

def instTemplate( text, vars ):
    prev = ""
    current = text
    while( prev != current ):
        t = Template( current )
        prev = current
        current = t.render( vars )
    return current

#print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
def aprint( *objects, sep=' ', end='\n', file=sys.stdout, flush=False, width=None):
    s = _a( objects, sep, end, width )
    print(s, end="", file=file, flush=flush )
    
def _a( *objects, sep=' ', end='\n', width=None):
    s = ""
    for o in objects:
        if len(s) >  0:
            s += sep
        if isinstance(o, str):
            s += o
        else:    
            s += repr(o)
    s += end
    if width:
        s = textwrap.fill(s, width )
    return s

def createBase64ImageFromFigure( fig ):
    from io import BytesIO
    figfile = BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="png")
    figfile.seek(0)  # rewind to beginning of file
    # figdata_png = base64.b64encode(figfile.read())
    image = base64.b64encode(figfile.getvalue()).decode('utf-8')
    return image


def createSVGImageFromFigure( fig ):
    from io import BytesIO
    figfile = BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="svg" )
    figfile.seek(0)  # rewind to beginning of file
    image = figfile.getvalue().decode('utf-8')
    return image

def createBase64VideoFromAnimation( anim ):
    fp, fname = tempfile.mkstemp( suffix=".mp4", prefix="animation" ) 
    anim.save( fname )
    with fp:
        data = f.read()
    return base64.b64encode( data )

def extract(source=None):
    """Copies the variables of the caller up to iPython. Useful for debugging.

    .. code-block:: python

        def f():
            x = 'hello world'
            extract()

        f() # raises an error

        print(x) # prints 'hello world'

    """
    import inspect
    import ctypes 

    if source is None:
        frames = inspect.stack()
        caller = frames[1].frame
        name, ls, gs = caller.f_code.co_name, caller.f_locals, caller.f_globals
    elif hasattr(source, '__func__'):
        func = source.__func__
        name, ls, gs = func.__qualname__, (func.__closure__ or {}), func.__globals__
    elif hasattr(source, '__init__'):
        func = source.__init__.__func__
        name, ls, gs = func.__qualname__, (func.__closure__ or {}), func.__globals__
    else:
        raise ValueError(f'Don\'t support source {source}')

    ipython = [f for f in inspect.stack() if f.filename.startswith('<ipython-input')][-1].frame

    ipython.f_locals.update({k: v for k, v in gs.items() if k[:2] != '__'})
    ipython.f_locals.update({k: v for k, v in ls.items() if k[:2] != '__'})

    # Magic call to make the updates to f_locals 'stick'.
    # More info: http://pydev.blogspot.co.uk/2014/02/changing-locals-of-frame-frameflocals.html
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(ipython), ctypes.c_int(0))

    message = 'Copied {}\'s variables to {}'.format(name, ipython.f_code.co_name)
    raise RuntimeError(message)