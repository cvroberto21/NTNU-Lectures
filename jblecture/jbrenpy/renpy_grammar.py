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
        self.currSpeaker = "narrator"
        self.speakers = {}
        self.labels = []

    def setCurrSpeaker(self, speaker):
        if speaker in self.speakers:
            self.currSpeaker = self.speakers[speaker]
            logger.debug( f"Setting current speaker {speaker}" )
            ret = self.currSpeaker
        else:
            logger.warning( f"Unknown speaker {speaker}" )
            ret = None

    def addSpeech( self, speech ):
        self.dialog.append( speech )

    def addComment( self, tokens ):
        self.dialog.append( [ RenpyScript.Commands.Comment, tokens[0].lstrip().rstrip() ] )
        logging.debug( f"addComment {tokens[0].lstrip().rstrip()}" )
        
    def addSpeaker( self, name ):
        self.speakers[name] = { "name" : name }

class RenpyGrammar:
    def __init__(self, rscript):
        # punctuation
        (
            colon,
            lbracket,
            rbracket,
            dot,
            hash,
            comma
        ) = map(pyp.Literal, r":().#,")

        self.kwList = """
        label jump with at show pause scene window hide speak blank
        call if image init menu python javascript return set while onlayer 
        //
        """.lower().split()

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
            onlayer,
            lComm
        ) = map( pyp.CaselessKeyword, self.kwList )

        #lComm = pyp.Keyword( '//' )

        lf = pyp.Suppress( pyp.lineEnd )
        ignoreWhitespaces = pyp.Suppress( pyp.ZeroOrMore( pyp.White( ' \t' ) ) )

        name = pyp.Word( pyp.alphas, pyp.alphanums + "_", min=1).setName("name")
        name.setParseAction( grammarRejectKeywords )

        string_ = (  pyp.QuotedString('"""', endQuoteChar='"""', multiline = True ) 
                    | pyp.QuotedString("'''", endQuoteChar="'''", multiline = True) 
                    | pyp.QuotedString("`", endQuoteChar="`", multiline = True)  
                    | pyp.QuotedString('"', endQuoteChar='"', multiline=False) 
                    | pyp.QuotedString("'", endQuoteChar="'", multiline=False) 
                    ).setName('string')
        string_.setDebug(True)

        speakerFunc = pyp.Combine( lbracket + ignoreWhitespaces + name + ignoreWhitespaces + rbracket )
        simpleExpression = ( name ^ string_ ^ speakerFunc ) + pyp.Optional( pyp.Combine( dot +  name ) ^ pyp.Combine( lbracket + pyp.Optional(name ^ string_) + rbracket ) )

        speaker = simpleExpression
        speaker.setParseAction( grammarRejectKeywords )
        #speaker.setParseAction( grammarSetCurrentSpeaker )

        labelId = pyp.Word( pyp.alphas, pyp.alphanums + "_").setName("label")
        label.setParseAction( grammarRejectKeywords )
        labelStmt = label + labelId + colon + lf

        jumpStmt = jump + labelId

        commentStmt = pyp.Suppress( lComm ^ hash ) + pyp.restOfLine + lf
        commentStmt.setParseAction( rscript.addComment )

        sayStmt = pyp.Optional( speaker ) + string_ + lf # + pyp.Optional( pyp.Suppress( with_ ) + simpleExpression ) + lf
        sayStmt.setParseAction( grammarAddSpeech ) 

        tagList = pyp.OneOrMore( ~pyp.StringEnd() + name + pyp.Suppress( pyp.Optional( comma ) ) )
        atStmt = at + tagList

        withStmt = with_ + tagList

        imageSpec = name + tagList + pyp.Optional( atStmt ) + pyp.Optional( withStmt )

        showStmt = show + imageSpec + lf
        showStmt.setParseAction( grammarShowImage )

        statement = commentStmt ^ labelStmt ^ jumpStmt ^ showStmt ^ sayStmt
        self.grammar = pyp.OneOrMore( ( ~pyp.StringEnd() + statement ) ) + pyp.StringEnd()

        #self.grammar.setDebug(True)

def grammarAddSpeech( src, locn, tokens ):
    ind = 0
    if ( len(tokens) > 1 ):
        name = tokens[0]
        if name not in rscript.speakers:
            raise pyp.ParseException(src,locn,'undefined speaker')
        else:
            rscript.setCurrSpeaker( tokens[0] )
            ind = 1
    logging.debug( f"grammarAddSpeech {rscript.currSpeaker} {tokens[ind]}" )
    rscript.addSpeech( [ RenpyScript.Commands.Speech, rscript.currSpeaker, tokens[ind] ] )
    
def grammarSetCurrentSpeaker( src, locn, tokens ):
    rscript.setCurrSpeaker( tokens )

def grammarShowImage( src, locn, tokens ):
    print("Tokens", locn, tokens )
    #rscript.addSpeech( [ RenpyScript.Commands.Show ] + tokens )

def grammarRejectKeywords( src, locn, token ):
    if token[0].lower() in rg.kwList:
        pyp.ParseException( src, locn, f"keyword {token}" )
        
def test( rg, strng ):
    print("test", strng )
    # print('Start of scanliteral')
    # for tokens,start,end in rg.grammar.scanString( strng ):
    #     print( 'scanliteral:', start, end, tokens.asList() )
    # print('End of scanliteral')
    x = rg.grammar.parseString( strng )
    print( x )
    print("done")

if __name__ == "__main__":
    
    rscript = RenpyScript()
    rscript.addSpeaker('jb')
    rscript.addSpeaker('elsie')

    rg = RenpyGrammar( rscript )    


    test( rg, "show jb neutral at center with fade")
    test( rg, '"Another line of dialog"\n')
    test( rg, """
    show elsie
    show jb happy left_arm at left with fadeIn
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
show jb at center with dissolve
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


    print(rscript.dialog)