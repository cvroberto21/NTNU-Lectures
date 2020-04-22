
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
from .jbquestion import JBQuestion 

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

cfg = {}
defaults = {}

class JBExam:
    def __init__( self ):
        self.prolog = None
        self.questions = []

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
        
    def addQuestion( self, question ):
        #html = wp.HTML( string = slideHTML )
        #doc = html.render( stylesheets = [ self.cssSlides ] )
        #png, width, height = doc.write_png( target=None )
        
        self.questions.append( question )
        return question

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
