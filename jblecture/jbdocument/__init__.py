
from jinja2 import Template
import re
import pathlib
import subprocess
import logging
import json
import logging

from ..jbslide import JBSlide
from ..jbdata import JBData, JBImage, JBVideo
from ..jbcd import JBcd

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

cfg = {}
defaults = {}

class JBDocument:
    def __init__( self ):
        self.slides = []
      
        self.current = ''
        self.parent = ''
        
        self.slideCount = 1
        self.slideFragmentCount = 1

        self.header = ""
        self.footer = ""
        self.background = ""
        
        # self.user_ns = {}
        
        # self.setTheme( theme )
        # self.setFooter( footer )
        # self.setHeader( header )
        # self.setBackground( background )

    # def setFooter(self, footer ):
    #     self.footer = footer

    # def setHeader(self, header):
    #     self.header = header

    # def setBackground( self, bg ):
    #     self.background = bg

    def createLocalTheme( self ):
        return self.makeRevealThemeLocal( cfg['REVEAL_THEME'] )
            
    def makeRevealThemeLocal(self, revealTheme):
        """removes .reveal, .reveal .slides, and .reveal .slides section from theme css"""
        tname = cfg['REVEAL_THEME'] + '.css' 
        themePath = pathlib.Path( cfg['REVEAL_THEME_DIR'] / tname ).resolve()
        with themePath.open() as f:
            css = f.read()
        # for x, r in [("\.reveal \.slides section ", ".jb-render "),
        #              ("\.reveal \.slides ", ".jb-render "),
        #              ("\.reveal ", ".jb-render "),
        #              ("section", ".jb-render ")]:
        #     css = re.sub(x, r, css)
        return css

    @staticmethod
    def sInstTemplate( text, vars ):
        prev = ""
        current = text
        while( prev != current ):
            t = Template( current )
            prev = current
            current = t.render( vars )
        return current 
      
    def instTemplate( self, text, vars ):
        #print('jbdocument CFG', hex(id(cfg)))
        #print('jbl: instTemplate: ', cfg)
        d = { ** cfg['user_ns'], **vars }
        return JBDocument.sInstTemplate( text, d )
        
    def findSlideIndex( self, id ):
        #logging.debug('Looking for', id)
        try:
            ind = next(i for i,v in enumerate( self.slides ) if v.id == id )
        except StopIteration:
            ind = -1
        #logging.debug('returning', ind )
        return ind

    def addSlide( self, id, slideHTML, background = None, header = None, footer = None ):
        #html = wp.HTML( string = slideHTML )
        #doc = html.render( stylesheets = [ self.cssSlides ] )
        #png, width, height = doc.write_png( target=None )
        
        if ( background ):
            background = self.instTemplate( self.background, {} )
        else:
            background = cfg['REVEAL_SLIDE_BACKGROUND']
        if ( header ):
            header = self.instTemplate( self.header, {} ) 
        else:
            header = cfg['REVEAL_SLIDE_HEADER']

        if ( footer ):
            footer = self.instTemplate( self.footer, {} )
        else:
            footer = cfg['REVEAL_SLIDE_FOOTER']

        self.slideCount = self.slideCount + 1
        self.slideFragmentCount = 1
        
        if ( id == "" ):
            id = "slide_{0:05d}_frag_{1:05d}".format( self.slideCount, self.slideFragmentCount )
        
        if ( id[0] == '"' ) or ( id[0] == "'" ):
            id = id[1:]
        if ( id[-1] == '"' ) or ( id[-1] == "'" ):
            id = id[:-1]
            
        oind = self.findSlideIndex( id )
        if (  oind >= 0 ) and ( oind < len(self.slides) ):
            del self.slides[oind]
        
        htmltxt = '\n<!-- Header -->\n' + header + '\n<!-- Background -->\n' + background + '\n<!-- Slide -->\n' + slideHTML + '\n<!-- Footer -->\n' + footer
        htmltxt = self.instTemplate( htmltxt, {} )
        #sl = JBSlide( id, header + '\n' + background + '\n' + slideHTML + '\n' + footer, renpy = '', left='', right='', up='', down='' )
        sl = JBSlide( id, htmltxt, renpyStyle='', renpy = '', left='', right='', up='', down='' )
        
        if ( self.current != '' ):
            c = self.findSlideIndex( self.current )
            if ( c >= 0 ) and ( c < len(self.slides) ):
                leftS = self.slides[ c ]
                leftS.right = sl.id
                sl.left = self.current
        
        self.current = id
        self.slides.append( sl )
        return sl
        
    def getCurrentSlide( self ):
        slide = None
        idx = self.findSlideIndex( self.current )
        if ( idx >= 0 ) and ( idx < len( self.slides ) ):
            slide = self.slides[idx]
        return slide
        
    def numberOfSlides( self ):
        return ( len( self.slides ) )
    
    def createSlides( self, start ):
        s = self.slides[ self.findSlideIndex( start ) ]
        slides = s.__repr_reveal_html__()
        
        while( s.right != '' ):
            s = self.slides[ self.findSlideIndex( s.right ) ]
            slides = slides + s.__repr_reveal_html__()
        return slides
      
    def createRevealSlideShow(self, startId = None ):
        if ( not startId ):
            startId = self.slides[0].id
        slides = self.createSlides( startId )
        assets = self.createAssets( cfg['ASSETS'], cfg['REVEAL_DIR'] )
        logging.debug("*** Assets ***")
        logging.debug(str(assets) )
        logging.debug("*** Assets ***")

        chars = self.createCharacters( cfg['CHARACTERS'] ) 
        
        presentation = self.instTemplate( cfg['REVEAL_PRESENTATION_TEMPLATE'], { 'slides': slides, 'assets': assets, 'characters' : chars  } )
        presentation = self.updateAssets( presentation, cfg['ASSETS'] ) 

        return presentation

    def updateAssets( self, presentation, assets ):
        for aName in assets:
            a = assets[ aName ]
            logging.debug( 'a' +str( a ) )
            for id in a.ids:
                re1 = re.compile(r'<span\s+id\s*=\s*"' + id + r'"\s*(?P<fmt>[^>]*?)\s*>(?P<data>.*?)</span>', re.DOTALL)
                m = re.match( re1, presentation ) 
                if m:
                    s = m.span[0]
                    e = m.span[1]
                    logger.debug( "updateAsset replacing presentation component ***%s***", presentation[s:e] )
                presentation = re.sub( 
                    re1, 
                    r'<span id="' + id + r'" \g<fmt>>' + a.__repr_html_path__(None, None, id=id) + r'</span>', 
                    presentation 
                )
        return presentation        

    def createAssets( self, assets, rdir ):
        s = "<!-- Assets -->\n"
        s = s + "var assets = {"
        inst = "var assetInstances = {"

        ia = 0
        iinst = 0
        for aname in assets:
            a = assets[ aname ]
            if ia > 0:
                s = s + ","
            s = s + "\n"
            s = s + f'"{a.name}" : '
            rpath = str( pathlib.Path(a.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )

            if a.url is not None:
                url = f'"{a.url}"'
            else:
                url = "null"

            if ( a.atype == JBData.JBIMAGE_PNG ) or ( a.atype == JBData.JBIMAGE_SVG ) or ( a.atype == JBData.JBIMAGE_JPG ):
                if a.atype == JBData.JBIMAGE_PNG:
                    suffix = "png"
                elif a.atype == JBData.JBIMAGE_SVG:
                    suffix = "svg"
                elif a.atype == JBData.JBIMAGE_JPG:
                    suffix = a.suffix
                else:
                    raise Exception("Unknown JBImage Type")

                s = s + f'new JBImage( "{a.name}", "{a.getSize()}", "{a.width}", "{a.height}", {url}, null, "{ rpath }", "{suffix}" )'
            elif ( a.atype == JBData.JBVIDEO ):
                s = s + f'new JBVideo( "{a.name}", "{a.getSize()}", "{a.width}", "{a.height}", {url}, null, "{ rpath }" )'

            for id in a.ids:
                if iinst > 0:
                    inst = inst + ","
                inst = inst + "\n"
                inst = inst + "    " + '"' + id + '"' + ":" + " " 
                inst = inst + f'assets["{a.name}"]'
                iinst = iinst + 1
            ia = ia + 1
        s = s + " \n};\n"
        inst = inst + "\n};\n"

        return s + inst + "<!-- End of Assets -->\n"

    def createCharacters( self, characters ):
        s = "<!-- Characters -->\n"
        s = s + 'var characters =\n'
        s = s + json.dumps( characters, sort_keys=True, indent=4)
        s = s  + ";\n"
        s = s + "<!-- End of Characters -->\n"
        return s

    def writeCharacters( self, chars, fname ):
        with open( fname, "w" ) as f:
            f.write( chars )

    def createRevealDownload( self, dir, fname = 'index.html' ):
        logging.info("Starting to create reveal slideshow")
        html = self.createRevealSlideShow()
        with open( pathlib.Path( dir ).joinpath( fname ), "w" ) as f:
            f.write( html )
        #self.npmInstall( dir )
        logging.info("Finished creating reveal slideshow")

    def npmInstall( self, dir ):
        with JBcd( dir ):
            logging.debug("Executing npm install")
            o = None
            try:
                o = subprocess.check_output("npm install", stderr=subprocess.STDOUT, shell = True)
            except subprocess.CalledProcessError:
                pass
            if ( o ):    
                logging.debug( 'npm install:' + o.decode('utf-8') )
    
    # def createSlideImages(self, rdir ):
    #     for s in self.slides:
    #         img = s.createJBImage( self.cssSlides )
    #         img.writeData( rdir )
    
    def createBackgroundsFile( self, rdir ):
        with open( pathlib.Path( rdir ).joinpath( "backgrounds.rpy" ), "w" ) as f:
            for s in self.slides:
                fname = s.getImageFileName()
                p = pathlib.Path( fname )
                rp = pathlib.Path(* p.parts[1:])
                f.write( f'image bg {s.id} = "{ str(rp) }"\n' )

    def createScriptFiles( self, rdir, startId = None ):
        if ( not startId ):
            startId = self.slides[0].id
        
        rpyScript = self.instTemplate( cfg['RenpyInitTemplate'], { 'title': cfg['TITLE'], 'startId': startId } )
        sp = pathlib.Path( rdir ) / "start.rpy"
        with sp.open( "w" ) as f:
            f.write( rpyScript )

        currentIdx = self.findSlideIndex( startId )

        while ( currentIdx >= 0 ) and ( currentIdx < len( self.slides) ):
            s = self.slides[ currentIdx ]
            if ( s.renpy ):
                logging.info('Slide ' + str(s.id) + ' has renpy ' + str( s.renpy ) )
            rpyScript = self.instTemplate( cfg['RenpyScriptTemplate'], { 'label': s.id, 'transition': cfg['RenpyTransition'], 'id': s.id, 'renpy': s.renpy, 'right': s.right } )
            sp = pathlib.Path( rdir ) / f"{s.id}.rpy"
            logging.debug("Writing renpy script %s", str(sp) )
            with sp.open( "w" ) as f:
                f.write( rpyScript )

            currentIdx = self.findSlideIndex( s.right )

    def setTitle( self, title ):
        cfg['TITLE'] = title

    # def createRenpySlideShow(self, startId = None ):
    #     rdir = cfg['RENPY_GAME_DIR']
    #     self.createSlideImages( rdir )
    #     self.createBackgroundsFile( rdir )
    #     self.createScriptFiles( rdir, startId )

def createEnvironment( mycfg ):
    global cfg
    #print('jbdocument', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    for k in defaults:
        if k not in cfg:
            cfg[k] = defaults[k]
    #print('jbdocument', hex(id(cfg)))
    return cfg
