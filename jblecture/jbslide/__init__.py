import logging

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

class JBSlide:
    def __init__(self, id, html, renpyStyle, renpy, left = '', right = '', up = '', down = '', parent = '' ):
        self.id = id
        self.parent = parent
        self.html = html
        
        self.renpyStyle = renpyStyle
        self.renpy = renpy
        
        self.up = up
        self.left = left
        self.right = right
        self.down = down
        
        self.note = ""

    def __repr_reveal_html__( self ):
        from ..jbdocument import JBDocument 
        reveal = JBDocument.sInstTemplate( cfg['REVEAL_SLIDE_TEMPLATE'], { 'id': self.id, 'slideHTML': self.html, 'slideNote': self.renpy, 'slideChildren':"" } )
        return reveal
        
    def createJBImage( self, css ):
        html = wp.HTML( string = self.html )
        doc = html.render( stylesheets = [ css ] )
        png, width, height = doc.write_png( target=None )
        from ..jbdata import JBImage
        img = JBImage( self.id, width, height, data = png, localFileStem= cfg['ROOT_DIR'] / self.getImageFileName() )
        return img

    def getImageFileName( self ):
        return cfg['RENPY_IMAGES_DIR'] / "slides" / f"{self.id}.png"
      
    def addRenpy( self, txt, style = ''):
        logging.debug( f'addRenpy {txt} {style}' )
        if len(self.renpy) == 0:
            logging.debug( f'adding initial preamble {style}' )
            self.renpy = """
                show scene-{id} {style}
            """.format(id=self.id, style=style)
        self.renpy = self.renpy + '\n' + txt
        self.renpyStyle = style

cfg = {}

def createEnvironment( mycfg ):
    global cfg
    cfg = mycfg
    return cfg
