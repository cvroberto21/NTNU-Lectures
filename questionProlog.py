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
<p>Solution:</p>
""" + sol + "\n</div><!-- end of question_solution -->\n"
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

defTableT = """
<table {clsStmt}" {idStmt}> 
{cdata}
<tbody>
{bdata}
</tbody>
</table>
"""

defTrT = """
<tr>
{0}
</tr>
"""

defTdT = """
<td>
{0}
</td>
"""

defThT = """
<th>
{0}
</th>
"""

def createTable( data, index = None, columns = None, id=None, cls=None, tableT = defTableT, thT = defThT, 
                tdT = defTdT, trT = defTrT ):
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
    if cls:
        clsStmt = f' class="{cls}" '
    else:
        clsStmt = ""
        
    if id:
        idStmt = f' id="{id}" '
    else:
        idStmt= ""
    table = tableT.format( clsStmt=clsStmt, idStmt=idStmt, cdata=cdata, bdata=bdata )
    return table

def writeExam( fname = None, includeSolutions=False ):
    if not fname:
        fname = f"{cfg['COURSE_TITLE']}-{cfg['EXAM_TYPE']}-{cfg['UNI_SHORT']}-{cfg['YEAR']}-{cfg['SEED']}"
        if includeSolutions:
            fname = fname + "-solutions"
    fname = fname + ".html"

    html = cfg['doc'].render( includeSolutions )

    with open(fname, "w") as f:
        f.write(html)
    return html
