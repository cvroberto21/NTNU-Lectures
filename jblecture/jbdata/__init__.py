from urllib import request
import pathlib
import base64
import youtube_dl
import uuid
import functools
import logging

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

cfg = {}

def genId( func ):
    @functools.wraps( func )
    def wrapperGenId( *args, **kwargs ):
        self = args[0]
        #logger.debug('args %s kwargs %s', args, kwargs )
        id = None
        if 'id' in kwargs:
            id = kwargs['id']
        else:
            kwargs['id'] = None
        if not id:
            id = self.generateId()
        kwargs['id'] = id
        ret = func( * args, **kwargs )
        if id not in self.ids:
            self.ids.append( id )
        return ret
    return wrapperGenId

class JBData:
    """
    Class that encapsulates an image and its various representations.
    """

    JBDATA, JBIMAGE_PNG, JBIMAGE_SVG, JBIMAGE_JPG, JBVIDEO = 0, 10, 11, 12, 30

    @staticmethod
    def sReadDataFromURL(url):
        data = request.urlopen(url).read()
        return data

    @staticmethod
    def sReadData( fname ):
        #logger.debug('JBData.sReadData', 'Reading file', fname)
        with open( fname, "rb") as f:
            data = f.read()
        return data

    @staticmethod
    def sWriteData(fname, data):
        with open(fname, "wb") as f:
            f.write(data)

    def getDefaultFileName(self):
        p = cfg['ROOT_DIR'] / 'reveal.js' / 'assets' / "{name}.{suffix}".format(name=self.name, suffix=self.suffix)
        return str(  p.expanduser().resolve() )

    def __init__(self, name, url=None, data=None, lfname=None, atype = JBDATA, suffix="dat"):
        self.url = url
        self.name = name
        self.data = None
        self.ids = []
        self.atype = atype

        if suffix and suffix[0] == ".":
            suffix = suffix[1:]

        self.suffix = suffix

        if data:
            if not lfname:
                lfname = self.getDefaultFileName()
            with open(lfname, "wb") as f:
                f.write(data)
                self.localFileStem = lfname[0:-len(suffix) - 1 ]
        elif url:
            if not lfname:
                lfname = self.getDefaultFileName()
            self.data = self.readDataFromURL(url, lfname)
            if (self.data):
                JBData.sWriteData(lfname, self.data)
            self.localFileStem = lfname[0:-len(suffix) - 1]
        elif lfname:
            if lfname[-len(suffix)-1:] != "." + suffix:
                lfname = lfname + "." + suffix
            data = JBData.sReadData(  lfname )
            #logger.debug('localFileStem',  lfname )
            self.localFileStem = lfname[0:-len(suffix)-1]
        else:
            uploaded = files.upload()
            for fn in uploaded.keys():
                print('User uploaded file "{name}" with length {length} bytes'.format(
                    name=fn, length=len(uploaded[fn])))
                self.localFileStem = fn
        self.clearCache()

    def readDataFromURL(self, url, tmpFile):
        # logger.debug('JBData.readDataFromURL', url )
        return JBData.sReadDataFromURL(url)

    def writeData(self, rdir):
        if (self.localFileStem):
            fname = self.localFileStem
        else:
            fname = self.getDefaultFileName()
        if (not self.data):
            self.data = JBData.sReadData(fname)
        ret = JBData.sWriteData(pathlib.Path(rdir).joinpath(fname), self.data)
        self.clearCache()
        return ret

    def readData( self ):
        if ( self.localFileStem ):
            fname = self.localFileStem
            self.data = sReadData( fname )
            
    @staticmethod
    def getBase64Data(fname):
        data = JBData.sReadData(fname)
        enc = base64.b64encode(data).decode('utf-8')
        return enc

    def clearCache(self):
        if (self.data) and (len(self.data) > 1024 * 1024):
            self.data = None

    @staticmethod
    def sCreateStyleString(typ, st):
        if st:
            s = typ + '="{}"'.format(st)
        else:
            s = ""
        return s

    def createStyleString( self, typ, st ):
        return JBData.sCreateStyleString( typ, st )

    @genId
    def __repr_html_localhost__(self, cls = None, style=None, *, id=None ):
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '<span id="{id}" {style}><object id="dat-{id}" src="http://localhost:{port}/{src}"/></span>\n'.format( id=id, style=cs, port=cfg['HTTP_PORT'], src=rpath + "." + self.suffix )

    @genId
    def __repr_html_path__(self, cls = None, style=None, *, id=None ):
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '<span id="{id}" {style}><object id="dat-{id}" src="{src}"/></span>\n'.format( id=id, style=cs, src=rpath + "." + self.suffix )

    @genId
    def __repr_html_file__(self, cls = None, style=None, *, id=None ):
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '<span id="{id}" {style}><object id="dat-{id}" src="file://{src}"/></span>\n'.format( id=id, style=cs, src=rpath + "." + self.suffix )

    @genId
    def __repr_html_url__(self, cls=None, style=None, *, id=None ):
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        return '<span id="{id}" {style}><img id="dat-{id}" src="{url}"/></span>\n'.format(id=id, url=self.url, style=cs )        

    def __repr_html__(self, cls = None, style=None, mode = None, *, id = None ):
        s = ""
        if ( mode is None ) or ( mode == "auto" ) or ( mode == "" ):
            if ( ('HTTPD' in cfg) and ( cfg['HTTPD'] ) and self.localFileStem ):
                mode = "localhost"
            elif self.url:
                mode = "url"
            else:
                mode = "path"

        if mode == "url":
            s = self.__repr_html_url__( cls, style, id=id )
        elif mode == "localhost":
            s = self.__repr_html_localhost__( cls, style, id=id )
        elif mode == "path":
            s = self.__repr_html_path__( cls, style, id=id )
        elif mode == "file":
            s = self.__repr_html_file__( cls, style, id=id )
        elif mode == "smart-path":
            if self.getSize() <= MAX_PATH_SIZE:
                s = self.__repr_html_path__( cls, style, id=id )
            else:
                s = self.__repr_html_url__( cls, style, id=id )
        else:
            raise Exception( f"JBData - unknown mode {mode}" )

        return s

    def __call__(self, cls=None, style = None, mode = None ):
        return self.__repr_html__(cls, style, mode, id=None )

    @staticmethod
    def sGenerateId():
        return "id-" + str( uuid.uuid4() )

    def generateId( self ):
        return JBData.sGenerateId()

    def getLocalName( self ):
        return self.localFileStem + "." + self.suffix
    
    def encodeMIME( self, tag ):
        s = ""
        s = s + tag + "base64, " + JBData.getBase64Data( str(self.localFileStem) + "." + self.suffix )
        return s
    
    @staticmethod
    def sGetSize( fname ):
        p = pathlib.Path( fname )
        return p.stat().st_size

    def getSize( self ):
        return JBData.sGetSize( self.getLocalName() )

class JBImage(JBData): 
    def __init__(self, name, width, height, url=None, data=None, localFileStem=None, suffix=None):
        if ( not suffix ):
            if ( localFileStem ):
                if str(localFileStem)[-4:] == ".png":
                    suffix = "png"
                elif str(localFileStem)[-4:] == ".svg":
                    suffix = "svg"
                elif str(localFileStem)[-4:] == ".jpg":
                    suffix = "jpg"
                elif str(localFileStem)[-5:] == ".jpeg":
                    suffix = "jpeg"
            elif ( url ):
                if str(url)[-4:] == ".png":
                    suffix = "png"
                elif str(url)[-4:] == ".svg":
                    suffix = "svg"
                elif str(url)[-4:] == ".jpg":
                    suffix = "jpg"
                elif str(url)[-5:] == ".jpeg":
                    suffix = "jpeg"

        if ( localFileStem and str(localFileStem)[-len(suffix) + 1:] == "." + suffix ):
            localFileStem = str(localFileStem)[0:-len(suffix)]

        if suffix == 'png':
            atype = JBData.JBIMAGE_PNG
        elif suffix == "svg":
            atype = JBData.JBIMAGE_SVG
        elif suffix == "jpg" or suffix == "jpeg":
            atype = JBData.JBIMAGE_JPG
        else:
            #logger.debug('name', name, 'localFileStem', localFileStem, 'suffix', suffix)
            raise Exception("Unknown JBImage data type: " + suffix )
        super(JBImage, self).__init__(name, url, data, localFileStem, atype=atype, suffix=suffix)
        self.width = width
        self.height = height

    @genId
    def __repr_html_localhost__(self, cls = None, style=None, *, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="http://localhost:{port}/{src}"/></span>\n'.format( id=id, width=w, height=h, style=cs, port=cfg['HTTP_PORT'], src=rpath + "." + self.suffix )

    @genId
    def __repr_html_path__(self, cls = None, style=None, *, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        if self.atype == JBData.JBIMAGE_SVG:
            s = '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="{src}"/></span>\n'.format( id=id, width=w, height=h, style=cs, src=rpath + "." + self.suffix )
        else:
            s = '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="{src}"/></span>\n'.format( id=id, width=w, height=h, style=cs, src=rpath + "." + self.suffix )
        return s

    @genId
    def __repr_html_file__(self, cls = None, style=None, *, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="file://{src}"/></span>\n'.format( id=id, width=w, height=h, style=cs, src=rpath + "." + self.suffix )

    @genId
    def __repr_html_url__(self, cls=None, style=None, *, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        return '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="{url}"/></span>\n'.format(id=id, width=w, height=h, url=self.url, style=cs )        

    @genId
    def __repr_html_base64__(self, cls=None, style=None, *, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        mime = self.encodeMIME()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        return '<span id="{id}"><img id="img-{id}" {width} {height} {style} src="{mime}"/></span>\n'.format(id=id, width=w, height=h, style=cs, mime=mime )

    def encodeMIME( self ):
        if self.suffix == "png":
            tag = "data:image/png;"
        elif self.suffix == "jpeg" or self.suffix == "jpg":
            tag = "data:image/jpeg;"

        s = ""
        s = s + tag + "base64, " + JBData.getBase64Data( str(self.localFileStem) + "." + self.suffix )
        return s

    @genId
    def __repr_html_svg__(self, cls=None, style=None, *, id=None):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        data = JBData.sReadData( str(self.localFileStem) + "." + self.suffix ).decode('utf-8')
        return '<span id="{id}" {style}>{data}</span>\n'.format(id=id, width=w, height=h, style=cs, data=data )

    def __repr_html_inline__( self, cls = None, style = None, *, id = None ):
        s = ""
        if ( self.atype == JBData.JBIMAGE_SVG ):
            s = self.__repr_html_svg__( cls, style, id=id )
        else:
            s = self.__repr_html_base64__( cls, style, id=id )
        return s

    def getDefaultFileName(self):
        p = cfg['REVEAL_IMAGES_DIR'] /  "{name}.{suffix}".format(name=self.name, suffix=self.suffix)        
        return str(  p.expanduser().resolve() )

    @staticmethod
    def sCreateWidthString( width ):
        if width > 0:
            w = 'width="{0}"'.format(width)
        else:
            w = ""
        return w

    def createWidthString( self ):
        return JBImage.sCreateWidthString( self. width )        

    @staticmethod
    def sCreateHeightString( height ):
        if height > 0:
            h = 'height="{0}"'.format(height)
        else:
            h = ""
        return h
    
    def createHeightString( self ):
        return JBImage.sCreateHeightString( self.height )

    # Modes are None/"auto", "url", "localhost", "path", "inline", "file"
    
    def __repr_html__(self, cls = None, style=None, mode = None, *, id = None ):
        #logger.debug("JBImage.__repr_html__", 'mode', mode )
        if ( mode is None ) or ( mode == "auto" ) or ( mode == "" ):
            if ( ('HTTPD' in cfg) and ( cfg['HTTPD'] ) and self.localFileStem ):
                mode = "localhost"
            elif self.url:
                mode = "url"
            # elif self.localFileStem:
            #     mode = "path"
            else:
                mode = "inline"

        s = ""
        if mode == "url":
            s = self.__repr_html_url__( cls, style, id=id )
        elif mode == "localhost":
            s = self.__repr_html_localhost__( cls, style, id=id )
        elif mode == "path":
            s = self.__repr_html_path__( cls, style, id=id )
        elif mode == "inline":
            s = self.__repr_html_inline__( cls, style, id=id )
        elif mode == "file":
            s = self.__repr_html_file__(cls, style, id=id )
        elif mode == "smart-path":
            if self.getSize() <= MAX_PATH_SIZE:
                s = self.__repr_html_path__( cls, style, id=id )
            else:
                s = self.__repr_html_url__( cls, style, id=id )
        else:
            raise Exception( f"JBImage - unknown mode {mode}" )
        return s

    # def updateAsset( self, id, mode ):
    #     newContent = ""
    #     if ( mode == "local" ):
    #         newContent = "<a id=\"img-" + id + "\" href=\"file://" + self.getLocalName() + "\">" + self.name + "</a>"
    #     elif ( mode == "url" ):
    #         newContent = self.__repr_html_url__()
    #     elif ( mode == "localhost" ):
    #         newContent = self.__repr_html_file__()
    #     elif ( mode == "path" ):
    #         newContent = "<a id=\"dat-" + id + "\" href=\"" + self.getLocalName() + "\">" + self.name + "</a>"
    #     return newContent

class JBVideo(JBData):
    def __init__(self, name, width, height, url=None, data=None, localFileStem=None, suffix="mp4"):
        super(JBVideo, self).__init__(name, url, data, localFileStem, atype=JBData.JBVIDEO, suffix=suffix)
        self.width = width
        self.height = height

    def readDataFromURL( self, url, localFileStem ):
        logger.debug('Reading video from %s localFileStem %s', str(url), str(localFileStem) )
        ydl_opts = {'outtmpl': localFileStem }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        self.localFileStem = localFileStem

    def getDefaultFileName(self):
        p = cfg['REVEAL_VIDEOS_DIR'] /  "{name}.{suffix}".format(name=self.name, suffix=self.suffix)
        return str(  p.expanduser().resolve() )

    @genId
    def __repr_html_url__(self, cls = None, style=None, id=None ):
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", style )
        return '''<span id="{id}">
            <iframe id="vid-{id}" {width} {height} {style} src="{src}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </span>\n'''.format(id=id, width=w, height=h, src=self.url, style=cs )

    @genId
    def __repr_html_path__(self, cls = None, style=None, id=None ):
        if style is not None:
            st = str( style )
        else:
            st = ""
        
        if len(st) > 0 and st[-1] != ";":
            st = st + ";"

        st = st + "pointer-events:all;"
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", st )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '''<span id="{id}">
           <video id="vid-{id}"  {style} controls>
           <source src="{src}"/>
           </span>\n'''.format(id=id, width=w, height=h, src=rpath + "." + self.suffix, style=cs )

    @genId
    def __repr_html_localhost__(self, style=None):
        if style:
            style=""

        return """<video controls>
                    <source src="{src}" {style}">'
                    </video>
                 """.format(src=self.localFileStem, port=cfg['HTTP_PORT'], name=self.name, style=style)

    @genId
    def __repr_html_base64__(self, cls = None, style=None, id=None ):
        #style['pointer-select'] = 'all'
        if style is not None:
            st = str( style )
        else:
            st = ""
        
        if len(st) > 0 and st[-1] != ";":
            st = st + ";"

        st = st + "pointer-events:all;"
        w = self.createWidthString()
        h = self.createHeightString()
        cs = self.createStyleString( "class", cls ) + " " + self.createStyleString( "style", st  )
        mime = self.encodeMIME( )
        rpath = str( pathlib.Path(self.localFileStem).relative_to(cfg['REVEAL_DIR'] ) )
        return '''<span id="{id}">
           <video id="vid-{id}"  {style} controls>
           <source src="{src}"/>
           </span>\n'''.format(id=id, width=w, height=h, src=mime, style=cs )

    def createHeightString( self ):
        return JBImage.sCreateHeightString( self.height )
    
    def createWidthString( self ):
        return JBImage.sCreateWidthString( self.width )

    # Modes are None/"auto", "url", "localhost", "path", "file", "inline?" "smart-path"
    def __repr_html__(self, cls = None, style=None, mode = None, *, id = None ):
        if (mode is None) or (mode == "auto") or ( mode == ""):
            if ( ('HTTPD' in cfg) and ( cfg['HTTPD'] ) and self.localFileStem ):
                mode = "localhost"
            elif self.url:
                mode = "url"
            # elif self.localFileStem:
            #     mode = "path"
            else:
                mode = "inline"

        s = ""
        if mode == "url":
            s = self.__repr_html_url__( cls, style, id = id )
        elif mode == "localhost":
            s = self.__repr_html_localhost__( cls, style, id = id )
        elif mode == "path":
            s = self.__repr_html_path__( cls, style, id = id )
        elif mode == "inline":
            s = self.__repr_html_base64__(cls, style, id = id )
        elif mode == "file":
            s = self.__repr_html_file__(cls, style, id = id )
        elif mode == "smart-path":
            if self.getSize() <= MAX_PATH_SIZE:
                s = self.__repr_html_path__( cls, style, id=id )
            else:
                s = self.__repr_html_url__( cls, style, id=id )
        else:
            raise Exception("JBVideo unknown mode", mode )

        return s

    def encodeMIME( self ):
        if ( self.suffix == "mp4" ) or ( self.suffix == "m4a" ) or ( self.suffix == "m4p" ) or ( self.suffix == "m4b" ) or ( self.suffix == "m4a" ) or ( self.suffix == "m4v" ):
            tag = "data:video/mp4;"
        elif self.suffix == "ogg":
            tag = "data:video/ogg;"
        elif self.suffix == "webm":
            tag = "data:video/webm;"
        elif self.suffix == "mkv":
            tag = "data:video/mkv;"

        s = ""
        s = s + tag + "base64, " + JBData.getBase64Data( str(self.localFileStem) + "." + self.suffix )
        return s

def createEnvironment( mycfg ):
    global cfg
    #print('jbdata', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    #print('jbdata', hex(id(cfg)))
    return cfg
