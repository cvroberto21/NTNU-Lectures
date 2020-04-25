def QuestionProlog( ):
    qprolog='<div class="question_frame"><!-- Start of Question Frame -->\n'
    display(HTML(qprolog))

def QuestionBody( title, text ):
    if title:
        head = f"<h3>{title}</h3>"
    else:
        head = ""
    qtext = f"""
        {head}
        <div class="question_body">
            [<span class="question_number">1</span>]
            {text}
        </div>
    """

    display(HTML( qtext ))
    return qtext

def QuestionAnswer( marks, answer, height = None ):?PJ
    if marks == 1:
        marksStr = '<span class="mark_num">'+ str(marks) + '</span>' + " mark"
    else:
        marksStr = '<span class="mark_num">'+ str(marks) + '</span>' + " marks"
        
    qmarks = f"""
<div class="question_marks">
    {marksStr}
</div>
"""
    if height:
        hs = f'style="height:{height};"'
    else:
        hs = ""
        
    qhint = f"""
<div class="question_answer_box" {hs}>
""" + answer + "\n</div>\n"
    q = qmarks + qhint
    display(HTML(q))
    return q

def QuestionSolution( sol ):
    qsol = f"""
<div class="question_solution">
""" + sol + "\n</div>\n"
    display(HTML(qsol))
    return qsol
    
def QuestionEpilog( ):
    qepilog='</div><!-- End of Question Frame -->\n'
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