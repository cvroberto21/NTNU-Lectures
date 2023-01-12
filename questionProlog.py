import matplotlib.pyplot as plt
import numpy as np
import math
import random
import sys
from IPython.core.display import display, HTML
import html

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
        if index:
            rdata = rdata + f"<td>{index[i]}</td>" + "\n"
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

def createB64PNGImageFromFigure( fig, title, dl=True ):
    import io
    import base64

    figfile = io.BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="png" )
    figfile.seek(0)  # rewind to beginning of file
    image = base64.b64encode( figfile.getvalue() )
    img = ""
    if dl:
        img = img + "\n" + f"""
           <a download="{title}" href="data:image/png;base64,{image.decode('utf-8')}">\n
           """
    img = img + f"""
    <img src="data:image/png;base64,{image.decode('utf-8')}" alt="{title}"/>
    """
    
    if dl:
        img = img + "\n</a>\n"
    return img

def createB64PNGImageFromRGB( rgb, title, dl=True ):
    import io
    import base64

    from PIL import Image
    im = Image.fromarray(rgb)
    figfile = io.BytesIO()
    im.save(figfile, format="png")
    figfile.seek(0)
    image = base64.b64encode( figfile.getvalue() )
    if title is None or title == "":
        title = "image.png"
    img = ""
    if dl:
        img = img + "\n" + f"""
           <a download="{title}" href="data:image/png;base64,{image.decode('utf-8')}">\n
           """
    img = img + f"""
    <img src="data:image/png;base64,{image.decode('utf-8')}" alt="{title}"/>
    """
    
    if dl:
        img = img + "\n</a>\n"
    return img

