def QuestionProlog( ):
    qprolog='<!-- <div class="question_frame"> --><!-- start of question_frame -->\n'
    display(HTML(qprolog))

def QuestionBody( title, text ):
    if title:
        head = f'<h3>[<span class="question_number">1</span>] {title}</h3>'
    else:
        head = ""
    qtext = f"""
        {head}
        <div class="question_body">
            {text}
        </div><!-- end of question_body -->
    """

    display(HTML( qtext ))
    return qtext

def QuestionAnswer( marks, answer, height = None ):
    if marks == 1:
        marksStr = '<span class="mark_num">'+ str(marks) + '</span>' + " mark"
    else:
        marksStr = '<span class="mark_num">'+ str(marks) + '</span>' + " marks"
        
    qmarks = f"""
<div class="question_marks">
    {marksStr}
</div><!-- end of question_marks -->
"""
    if height:
        hs = f'style="height:{height};"'
    else:
        hs = ""
        
    qhint = f"""
<div class="question_answer_box" {hs}>
""" + answer + "\n</div><!-- end of question_answer_box -->\n"
    q = qmarks + qhint
    display(HTML(q))
    return q

def QuestionSolution( sol ):
    qsol = f"""
<div class="question_solution"><!-- start of question_solution -->
""" + sol + "\n</div><!-- end of question_solutiion -->\n"
    display(HTML(qsol))
    return qsol
    
def QuestionEpilog( ):
    qepilog='<!-- </div> --><!-- end of question_frame -->\n'
    display(HTML(qepilog))
    
def peval(s):
    o = s + ' => ' + str( eval(s) )
    return o

def generateHint( code ):
    show = True
    hint = ""
    for l in code.splitlines():
        if l == "#starthide":
            show = False
        if show:
            hint = hint + l + "\n"
        if l == "#endhide":
            show = True
    return hint

def fixupSVG( svg ):
    show = False
    out = []
    for l in svg.splitlines():
        if l[0:4] == "<svg":
            show = True
        if show:
            out.append(l)
        if l[0:6] == "</svg>":
            show = False
    return "\n".join( out )
        
def createSVGImageFromFigure( fig ):
    from io import BytesIO
    figfile = BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="svg" )
    figfile.seek(0)  # rewind to beginning of file
    image = figfile.getvalue().decode('utf-8')
    return fixupSVG( image )
