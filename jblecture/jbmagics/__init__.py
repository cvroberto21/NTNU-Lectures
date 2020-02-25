import base64

from IPython.core import magic_arguments
from IPython.core.magic import line_magic, cell_magic, line_cell_magic, Magics, magics_class
from IPython.core.display import HTML, Image, Pretty, Javascript, display
from IPython.utils.capture import capture_output

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from docutils import core, io
import re

from ..jbdocument import JBDocument

import logging

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

@magics_class
class JBMagics(Magics):
    def __init__(self, shell, doc):
        super(JBMagics, self).__init__(shell)
        self.doc = doc

    def instTemplate(self, text, vars):
        d = { **self.shell.user_ns, **vars }
        d[ 'cfg' ] = cfg
        return JBDocument.sInstTemplate(text, d)

    def html_parts(self, input_string, source_path=None, destination_path=None,
                   input_encoding='unicode', doctitle=True,
                   initial_header_level=1):
        """
    Given an input string, returns a dictionary of HTML document parts.

    Dictionary keys are the names of parts, and values are Unicode strings;
    encoding is up to the client.

    Parameters:

    - `input_string`: A multi-line text string; required.
    - `source_path`: Path to the source file or object.  Optional, but useful
      for diagnostic output (system messages).
    - `destination_path`: Path to the file or object which will receive the
      output; optional.  Used for determining relative paths (stylesheets,
      source links, etc.).
    - `input_encoding`: The encoding of `input_string`.  If it is an encoded
      8-bit string, provide the correct encoding.  If it is a Unicode string,
      use "unicode", the default.
    - `doctitle`: Disable the promotion of a lone top-level section title to
      document title (and subsequent section title to document subtitle
      promotion); enabled by default.
    - `initial_header_level`: The initial level for header elements (e.g. 1
      for "<h1>").
        """
        overrides = {'input_encoding': input_encoding,
                     'doctitle_xform': doctitle,
                     'initial_header_level': initial_header_level}
        parts = core.publish_parts(
            source=input_string, source_path=source_path,
            destination_path=destination_path,
            writer_name='html', settings_overrides=overrides)
        return parts

    def html_body(self, input_string, source_path=None, destination_path=None,
                  input_encoding='unicode', output_encoding='unicode',
                  doctitle=True, initial_header_level=1):
        """
    Given an input string, returns an HTML fragment as a string.

    The return value is the contents of the <body> element.

    Parameters (see `html_parts()` for the remainder):

    - `output_encoding`: The desired encoding of the output.  If a Unicode
      string is desired, use the default value of "unicode" .
        """
        parts = self.html_parts(
            input_string=input_string, source_path=source_path,
            destination_path=destination_path,
            input_encoding=input_encoding, doctitle=doctitle,
            initial_header_level=initial_header_level)
        fragment = parts['html_body']
        if output_encoding != 'unicode':
            fragment = fragment.encode(output_encoding)
        return fragment

    def embedCellHTML(self, html, line, cls, css):
        it = ""

        if css:
            it = it + "<style>\n" + css + "\n" + "</style>" + "\n"

        # it = it + '<div class="section">'
        it = it + '<div class="{cls} jb-render">\n'.format(cls=cls)

        if line:
            # print("Adding style", line)
            it = it + "<div {0}>\n".format(line)

        it = it + html + "\n"

        it = it + '</div>\n'


        # it = it + """
        #          <script src="reveal.js/js/reveal.js"></script>
        #          <script>
        #             Reveal.initialize();
        #          </script>
        # """
        if line:
            it = it + "</div>\n"

        #it = it + '</div>'

        # print(self.shell.user_ns['test'])
        # print(s
        return it

    def createHTMLRepr(self, output):
        rh = getattr(output, "_repr_html_", None)
        if (callable(rh)):
            html = output._repr_html_()
            if (html is not None):
                return html
            else:
                rp = getattr(output, "_repr_png_", None)
                if (callable(rp)):
                    png = output._repr_png_()

                    if (png is not None):
                        enc = base64.b64encode(png).decode('utf-8')

                        return '<img src="data:image/png;base64,{0}"/>'.format(enc)
        return None

    @cell_magic
    def html_templ(self, line, cell):
        it = ""
        if line:
            it = it + "<div {0}>\n".format(line)
        it = it + cell + "\n"
        if line:
            it = it + "</div>\n"
        # print(self.shell.user_ns['test'])
        # print(s)
        display(HTML("<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.3/"
             "latest.js?config=default'></script>"))
        display(HTML(self.instTemplate(it, {})))

    @cell_magic
    def reveal_html(self, line, cell):
        #print("cell_magic reveal_html called")

        it = ""
        it = it + self.embedCellHTML(cell, line, 'jb-output', self.doc.createLocalTheme())

      #display(HTML("<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.3/latest.js?config=default'></script>"))

        display(HTML(self.instTemplate(it, {})))

    @cell_magic
    def reveal_rst(self, line, cell):
        #print("cell_magic reveal_rst called")

        md = self.html_body(input_string=cell)
        it = ""
        it = it + self.embedCellHTML(md, line, 'jb-output', self.doc.createLocalTheme())
        display(HTML(self.instTemplate(it, {})))

    @cell_magic
    def css(self, line, cell):
        s = ""
        s = s + "<style>" + "\n"
        s = s + self.instTemplate(cell, {})
        s = s + "</style>" + "\n"
        display(HTML(s))

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--no-stderr', action="store_true",
                              help="""Don't capture stderr."""
                              )
    @magic_arguments.argument('--no-stdout', action="store_true",
                              help="""Don't capture stdout."""
                              )
    @magic_arguments.argument('--no-display', action="store_true",
                              help="""Don't capture IPython's rich display."""
                              )
    @magic_arguments.argument('--echo', action="store_true",
                              help="""Prepend cell content."""
                              )
    @magic_arguments.argument('--parent', type=str, default='',
                              help="""Select parent slide. Slide will be appended to list of children of this slide"""
                              )
    @magic_arguments.argument('--id', type=str, default='',
                              help="""Select slide id"""
                              )
    @magic_arguments.argument('--footer', type=str, default='', nargs=1,
                              help="""Define the slide footer"""
                              )
    @magic_arguments.argument('--header', type=str, default='', nargs=1,
                              help="""Define the slide header"""
                              )
    @magic_arguments.argument('--background', type=str, default='', nargs=1,
                              help="""Define the slide background"""
                              )
    @magic_arguments.argument('--output', type=str, default='output', nargs=1,
                              help="""A variable that will be pushed into the user namespace with the 
        utils.io.CapturedIO object.
        """
                              )
    @magic_arguments.argument('--style', type=str, default='',
                              help="""
        HTML inline style to be applied to the cell.
        """
                              )

    @magic_arguments.argument('--math', action="store_true", default="False",
                              help="""
        Add MathJax to render math in output cell.
        """
                              )

    @cell_magic
    def slide(self, line, cell):
        args = magic_arguments.parse_argstring(self.slide, line)
        out = not args.no_stdout
        err = not args.no_stderr
        disp = not args.no_display
        math = args.math
        
        #print("cell_magic slide called")
        # print('args', args )

        if args.id:
            if args.id[0] == '"' or args.id[0] == "'":
                args.id = args.id[1:]
            if args.id[-1] == '"' or args.id[-1] == "'":
                args.id = args.id[0:-1]

        if (args.style):
            if args.style[0] == '"' or args.style[0] == "'":
                args.style = args.style[1:]
            if args.style[-1] == '"' or args.style[-1] == "'":
                args.style = args.style[0:-1]

            mystyle = 'style="{s}"'.format(s=args.style)
        else:
            mystyle = ""

        # print("MYSTYLE", mystyle)

        s = self.instTemplate(cell, {})
        with capture_output(out, err, disp) as io:
            self.shell.run_cell(s)

        html = '<div class="{cls}">\n'.format(cls="jb-slide")

        # print(args.echo)
        if (args.echo):
            html = html + '<div class="jb-input jb-render jb-code" style="text-align:center">' + '\n'
            html = html + self.embedCellHTML( highlight(cell, PythonLexer(),
                                                        HtmlFormatter(cssstyles="color:#101010;display=inline-block;",
                                                                      noclasses=True)), mystyle, 'jb-input-code',
                                              self.doc.createLocalTheme()) + '\n'
            html = html + "</div>" + "\n"
        # print("html", html)

        if (out):
            if io.stdout != "":
                display( Pretty( io.stdout ) )
                # # print("Adding output", io.stdout)
                # h = '<div class="jb-output jb-render code" style="text-align:center">' + '\n'
                # h = h + '<div class="jb-stdout code" style="display:inline-block; width:90%">' + '\n'
                # h = h + '<pre {s}>\n'.format(s=mystyle)
                # h = h + io.stdout
                # h = h + '</pre>\n'
                # h = h + '</div>\n'
                # h = h + '</div>\n'
                # html = html + self.embedCellHTML(h, mystyle, 'jb-print', '')

        for o in io.outputs:
            # print('Output', o)
            h = self.createHTMLRepr(o)
            # print('SLIDE: h', h)
            if (h is not None):
                html = html + "\n" + self.embedCellHTML(h, mystyle, 'jb-output-code', '') + "\n"

        html = html + "\n" + "</div>"

        # html = re.sub("<style>.*", "", html, flags=re.MULTILINE )
        htmlNoStyle=html
        if ( html.find("<style>") >= 0 ) and  ( html.find("</style>") >= 0 ):
            htmlNoStyle = html[:html.find("<style>")] + html[html.find("</style>") + len("</style>"):]
        #print('*** HTML ***', htmlNoStyle)

        if args.output:
            self.shell.user_ns[args.output] = html

        slide = self.doc.addSlide(args.id, htmlNoStyle, args.background, args.header, args.footer)
        #print('**HTML***', slide.html )

        html = ""

        html = html + """
            <script src="https://www.gstatic.com/external_hosted/mathjax/latest/MathJax.js?config=TeX-AMS_HTML-full,Safe&delayStartupUntil=configured"></script>
            <script>
                (() => {
                const mathjax = window.MathJax;
                mathjax.Hub.Config({
                'tex2jax': {
                    'inlineMath': [['$', '$'], ['\\(', '\\)']],
                    'displayMath': [['$$', '$$'], ['\\[', '\\]']],
                    'processEscapes': true,
                    'processEnvironments': true,
                    'skipTags': ['script', 'noscript', 'style', 'textarea', 'code'],
                    'displayAlign': 'center',
                },
                'HTML-CSS': {
                    'styles': {'.MathJax_Display': {'margin': 0}},
                    'linebreaks': {'automatic': true},
                    // Disable to prevent OTF font loading, which aren't part of our
                    // distribution.
                    'imageFont': null,
                },
                'messageStyle': 'none'
                });
                mathjax.Hub.Configured();
            })();
            </script>
            """

        html = html + '<style>\n' + self.doc.createLocalTheme() + '\n' + '</style>'
        html = html + """
            <div class="reveal">
                <div class="slides">
        """

        html = html + slide.html
        
        html = html + """
                </div>
            </div>
        """

        display ( HTML( html ) )

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--id', type=str, default='',
                              help="Select slide id. Use current slide if unspecified."
                              )
    @magic_arguments.argument('--style', type=str, default='',
                              help="Additional style applied to the slide"
                              )
    @cell_magic
    def renpy(self, line, cell):
        args = magic_arguments.parse_argstring(self.renpy, line)
        
        if (args.style):
            if args.style[0] == '"' or args.style[0] == "'":
                args.style = args.style[1:]
            if args.style[-1] == '"' or args.style[-1] == "'":
                args.style = args.style[0:-1]

            myStyle = 'style="{s}"'.format(s=args.style)
        else:
            myStyle = ""

        it = ""

        cellText = "\n".join([" " * 4 + c if (len(c) > 0) else "\n" for c in cell.splitlines()])
        it = it + cellText + "\n"

        # print(self.shell.user_ns['test'])
        # print(s)
        rp = self.instTemplate(it, {})
        display(Pretty(rp))
        cs = self.doc.getCurrentSlide()
        if (cs):
            logger.debug( f"*** Adding renpy to slide {cs.id}" )
            # print(rp)

            cs.addRenpy( rp, myStyle )

def createEnvironment( mycfg ):
    global cfg
    cfg = mycfg
    return cfg
