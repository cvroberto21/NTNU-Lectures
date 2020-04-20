import pyparsing as pyp
import logging
import sys

logger = logging.getLogger( __name__ )
logger.setLevel( logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RenpyScript:
    class Commands:
        Comment, Speech, Show, Label, Jump = range(5)

    def __init__(self):
        self.dialog = []
        self.currSpeaker = "Unknown"
        self.speakers = []
        self.labels = []

    def rememberSpeaker(self, t):
        speaker = t
        self.currSpeaker = speaker
        logger.debug( f"setting current speaker {speaker}" )

    def addSpeech( self, tokens ):
        ind = 0
        if ( len(tokens) > 1 ):
            self.rememberSpeaker( tokens[0] )
            ind = 1
        logging.debug( f"addSpeech {self.currSpeaker} {tokens[ind]}" )
        self.dialog.append( [ RenpyScript.Commands.Speech, self.currSpeaker', tokens[ind] ] )
    
    def addComment( self, tokens ):
        self.dialog.append( [ RenpyScript.Commands.Comment, tokens[0].lstrip().rstrip() ] )
        logging.debug( f"addComment {tokens[0].lstrip().rstrip()}" )
        

class RenpyGrammar:
    def __init__(self, rscript):
        # punctuation
        (
            colon,
            lbracket,
            rbracket,
            dot,
            hash
        ) = map(pyp.Literal, r":().#")

        #keywords
        (
            label,
            jump,
            with_,
            at,
            show,
            pause,
            scene,
            window,
            hide,
            speak,
            blank,
            call,
            if_,
            image,
            init,
            menu,
            python,
            javascript,
            return_,
            set_,
            while_,
            lComm
        ) = map( pyp.CaselessKeyword, """
        label jump with at show pause scene window hide speak blank
        call if image init menu python javascript return set while //
        """.split() )

        #lComm = pyp.Keyword( '//' )

        lf = pyp.Suppress( pyp.lineEnd )
        ignoreWhitespaces = pyp.Suppress( pyp.ZeroOrMore( pyp.White( ' \t' ) ) )

        name = pyp.Word( pyp.alphas, pyp.alphanums + "_").setName("name")
        string_ = (  pyp.QuotedString('"""', endQuoteChar='"""', multiline = True ) 
                    | pyp.QuotedString("'''", endQuoteChar="'''", multiline = True) 
                    | pyp.QuotedString("`", endQuoteChar="`", multiline = True)  
                    | pyp.QuotedString('"') 
                    | pyp.QuotedString("'") 
                    )

        simpleExpression = ( name ^ string_ ^ ( lbracket + name + rbracket ) ) + pyp.Optional( ( dot +  name ) ^ ( lbracket + pyp.Optional(name ^ string_) + rbracket ) )

        speaker = simpleExpression
        speaker.setParseAction( rscript.rememberSpeaker )

        labelId = pyp.Word( pyp.alphas, pyp.alphanums + "_").setName("id")
        labelStmt = label + labelId + colon + lf

        jumpStmt = jump + labelId

        commentStmt = pyp.Suppress( ( lComm ^ hash ) + ignoreWhitespaces ) + pyp.restOfLine + lf
        commentStmt.setParseAction( rscript.addComment )

        sayStmt = ( string_ ^ ( pyp.Optional(speaker) + string_ ) ) + lf # + pyp.Optional( pyp.Suppress( with_ ) + simpleExpression ) + lf
        sayStmt.setParseAction( rscript.addSpeech ) 

        statement = sayStmt ^ commentStmt ^ labelStmt ^ jumpStmt
        self.grammar = pyp.OneOrMore( statement )
        #self.grammar.setDebug(True)

def test( rg, strng ):
    print("test", strng )
    x = rg.grammar.parseString( strng )
    print( x )
    print("done")

if __name__ == "__main__":
    
    rscript = RenpyScript()
    rg = RenpyGrammar( rscript )    
    test( rg, '"Another line of dialog"\n')
    test( rg, """
    jb `Hello 
    World`
    jb "Another line of dialog"
    "I have more to say"
    """)
    test( rg, """
#       Try this comment     
// A comment
# Another comment
    """)
    test( rg, """
// testing comments
(jb) "Talk to me later" 
"dialog continues"
# Another comment 
jb.lastName ''' Multine
   line speech'''
'Tell me what' with mad
    """)
    test( rg, """
 '''Multine
   line speech'''
    """)
    test( rg, '''
elsie() """ Multi 
line speech"""
`This string can also
span multiple lines`
# A python comment
    ''')
#     test( rg, '''
# jb "Hello" "World"
# jb Hello World
#     ''')
    print(rscript.state)