
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
from ..jbdocument import JBDocument

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

defaults = {
}

class JBExam:
    class ComponentType:
        PROLOG, HTML, QUESTION_TEXT, QUESTION_BOX, ANSWERBOX = range(5)

    def __init__( self ):
        self.questions = []    
        self.components = []

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
        #print('jbexam CFG', hex(id(cfg)))
        #print('jbl: instTemplate: ', cfg)
        d = { ** cfg['user_ns'], **vars }
        return JBDocument.sInstTemplate( text, d )
        
    def addQuestion( self, question ):
        #html = wp.HTML( string = slideHTML )
        #doc = html.render( stylesheets = [ self.cssSlides ] )
        #png, width, height = doc.write_png( target=None )
        
        self.questions.append( question )
        return question

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

    def loadCSS( self, vars ):
        if 'EXAM_CSS' not in cfg:
            with open( cfg['MODULE_ROOT'] / 'html' / 'exam.css') as f:
                cfg['EXAM_CSS_TEMPLATE'] = f.read()
                cfg['EXAM_CSS'] = self.instTemplate( cfg['EXAM_CSS_TEMPLATE'], vars )

    def loadJS( self, vars ):
        if 'EXAM_JS' not in cfg:
            with open( cfg['MODULE_ROOT'] / 'html' / 'exam.js') as f:
                cfg['EXAM_JS_TEMPLATE'] = f.read()
                cfg['EXAM_JS'] = self.instTemplate( cfg['EXAM_JS_TEMPLATE'], vars )

    def loadConfig( self, vars ):
        self.loadCSS( vars )
        self.loadJS( vars )

        if 'EXAM_NOTES' not in cfg:
            cfg['EXAM_NOTES'] = """
            <ul>
                <li>Attempt all questions.</li>    
                <li>This is an <em>open</em> book and <em>open</em> Internet examination. 
                Use of books, notes, laptops, and computers <b>with Internet connectivity</b>
                is <em>permitted</em>.</li> 
                <li> This exam must be <b>your own</b> work. Communication with others via
                messenger apps, email, phone is strictly <b>forbidden</b>.</li>
                <li>Show your work to receive full marks. You must show your reasoning,
                intermediate steps/calculations to reach the answer.</li>
                <li>Some of the questions may not be solvable, that is it may be 
                impossible to calculate the requested information. In this case, 
                say so in your answer and explain why.</li>
            </ul>   
            """

        if 'EXAM_PROLOG' not in cfg:
            with open( cfg['MODULE_ROOT'] / 'html' / 'exam_header.html') as f:
                cfg['EXAM_PROLOG_TEMPLATE'] = f.read()
                cfg['EXAM_PROLOG'] = self.instTemplate( cfg['EXAM_PROLOG_TEMPLATE'], {} )

        if 'EXAM_MARKS_BOX' not in cfg:
            cfg['EXAM_MARKS_BOX'] = """
    <div>
        <div class="marks_box">
            <span id="marks">Marks</span><br>
            <span id="marks_holder">   _________   </span><br>
            <span>out of</span><br>
            <span id="total_marks_holder"> %# cfg['EXAM_TOTAL_MARKS'] #% </span>
        </div>
        <span ondblclick="showHideAnswers()" id="showhideanswersbox">
            solutions???
        </span>
        <div>
        <p>
        </p>
        </div>
    </div>
            """

        if 'EXAM_EPILOG' not in cfg:
            cfg['EXAM_EPILOG'] = """
  </body>
</html>
            """

        vars = {}
        repl = False

        html = ""
        html = html + self.instTemplate( cfg['EXAM_PROLOG'], vars ) + "\n"
        html = html + self.instTemplate( cfg['EXAM_MARKS_BOX'], vars ) + "\n"
        return html

    def removeEmbeddings( self, hhtml ):
        show = True
        out = ""
        for l in hhtml.splitlines():
            if l == "<!-- embeddings start -->":
                show = False
            if show:
                out = out + l + "\n"
            if l == "<!-- embeddings end -->":
                show = True
        return out
                
    def addHTML( self, html, type = None ):
        html = self.removeEmbeddings( html )
        self.components.append( (JBExam.ComponentType.HTML, html ) )
        return html

    def fixupQuestionNumbers( self, html ):
        qnum = 1
        pat = re.compile( r'\[\<span class="question_number"\>(1)\</span\>\]' )
        out = ""
        last = 0
        for m in re.finditer( pat, html ):
            print("Found qnum", m.start(), m.end() )
            out = out + html[last:m.start()]
            out = out + r'[<span class="question_number">' + str(qnum) + '</span>]'
            qnum = qnum + 1
            last = m.end()
            if qnum > 100:
                break
        if last < len(html):
            out = out + html[last:]
        return out

    def fixupTotalMarks( self, html ):
        patTotal = re.compile( r'\<span id="total_marks_holder"\>[^<]+\</span\>' )
        patMarks = re.compile( r'\<span class="mark_num"\>([^<]+)\</span\>' )
        out = ""
        marks = 0
        last = 0
        for m in re.finditer( patMarks, html ):
            print("Found marks", m.start(), m.end() )
            marks = marks + int( m.group(1) )
        print("Total marks", marks)
        out = re.sub( patTotal, r'<span id="total_marks_holder">'+str(marks)+'</span>', html )
        return out

    def render( self, includeSolutions = True ):
        prolog = cfg['EXAM_PROLOG']
        prolog = prolog.replace("%#", "{{" ).replace("#%", "}}")
        marksBox = cfg['EXAM_MARKS_BOX']

        html = ""
        html = html + prolog
        html = html + marksBox
        for c in self.components:
            typ = c[0]
            if typ == JBExam.ComponentType.PROLOG or typ == JBExam.ComponentType.HTML:
                html = html + f"<!-- Start of Component Type {typ}-->\n" + c[1] + f"\n<!-- End of Component Type {typ} -->\n"
        epilog = cfg['EXAM_EPILOG']
        html = html + epilog
        html = self.fixupQuestionNumbers( html )
        html = self.fixupTotalMarks(html)
        return html

cfg = {}

def createEnvironment( mycfg ):
    global cfg
    #print('jbexam', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    for k in defaults:
        if k not in cfg:
            cfg[k] = defaults[k]
    #print('jbexam', hex(id(cfg)))
    return cfg
