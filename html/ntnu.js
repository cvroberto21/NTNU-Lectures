var atype = {
    JBDATA : 0,
    JBIMAGE_PNG : 10,
    JBIMAGE_SVG : 11,
    JBIMAGE_JPG : 12,
    JBVIDEO: 30,    
};

class JBData {
    constructor( name, url=None, data=None, localFile=None, mytype = JBData.atype.JBDATA, suffix="dat" ) {
        this.mytype = mytype;
        this.name = name;
        this.url = url;
        this.data = data;
        this.localFile = localFile;
        this.suffix = suffix;

        console.log("JBData(" + name + "," + url + "," + localFile + ")" );
    }

    updateAsset( id, mode ) {
        newContent = "";
        if ( mode == "path" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + this.getLocalName() + "\">" + this.name + "</a>";
        } else if ( mode == "url" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + this.url + "\">" + this.name + "</a>";
        } else if ( mode == "localhost" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + "http://localhost:8000/" + this.getLocalName() + "\">" + this.name + "</a>";
        } else if ( mode == "file" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"file://" + this.getLocalName() + "\">" + this.name + "</a>";
        }

        console.log("JBData.updateAsset(" + id + "," + "," + mode + ") =>" + newContent );
        return newContent;
    }
    
    getLocalName() {
        return this.localFile + "." + this.suffix
    }
}

JBData.atype = atype;

class JBImage extends JBData {
    constructor( name, width, height, url=null, data=null, localFile=None, suffix = null ) {
        var lfLen = 0;
        if (suffix == null ) {
            if (localFile != null ) {
                lfLen = localFile.length;
                if ( ( lfLen - 4 >= 0 ) && ( localFile. substring( lfLen - 4, lfLen ) == ".png" ) ) {
                    suffix = "png";
                } else if ( ( lfLen - 4 >= 0 ) && ( localFile. substring( lfLen - 4, lfLen ) == ".svg" ) ) {
                    suffix = "svg";
                } else if ( ( lfLen - 4 >= 0 ) && ( localFile. substring( lfLen - 4, lfLen ) == ".jpg" ) ) {
                    suffix = "jpg";
                } else if ( (lfLen - 5 >= 0 ) && ( localFile. substring( lfLen -5, lfLen ) == ".jpeg" ) ) { 
                    suffix = "jpeg";
                }
            }
        }

        if ( ( localFile != null ) && ( lfLen - suffix.length - 1 >= 0 ) && ( localFile.substring( lfLen - suffix.length - 1, lfLen ) == "." + suffix  ) ) {
            localFile = localFile.substring( 0, lfLen - suffix.length - 1 );
        }

        var mytype = null;
        if ( suffix == "png" ) {
            mytype = JBData.atype.JBIMAGE_PNG; 
        } else if ( suffix == "svg") {
            mytype = JBData.atype.JBIMAGE_SVG; 
        } else if ( ( suffix == "jpg") || ( suffix == "jpeg" ) ) {
            mytype = JBData.atype.JBIMAGE_JPG;
        } 
        super( name, url, data, localFile, mytype, suffix );
        this.width = width;
        this.height = height;
        console.log("JBImage(" + name + "," + url + "," + localFile + "." + suffix + ")" );
    }

    // modes are null/"auto", "url", "localhost", "path", "inline", "file"
    updateAsset( id, mode ) {
        var newContent = "";
        if ( mode == "path" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"" + this.getLocalName() + "\"/>";
        } else if ( mode == "url" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"" + this.url + "\"/>";
        } else if ( mode == "localhost" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"" + "http://localhost:8000/" + this.getLocalName() + "\"/>";
        } else if ( mode == "file" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"file://" + this.getLocalName() + "\"/>";
        }

        console.log("JBImage.updateAsset(" + id + "," + "," + mode + ") =>" + newContent );
        return newContent;
    }    
}

class JBVideo extends JBData {
    constructor( name, width, height, url=None, data=None, localFile=None ) {
        super( name, url, data, localFile, JBData.atype.JBVIDEO, "mp4");
        this.width = width;
        this.height = height;
        console.log("JBVideo(" + name + "," + url + "," + localFile + ")" );
    }

    updateAsset( id, mode ) {
        var newContent = "";
        if ( mode == "path" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"" + this.getLocalName() + "\"/></video>";
        } else if ( mode == "url" ) {
            newContent = "<iframe id=\"vid-" + id + "\" src=\"" + this.url + "\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>/>";
        } else if ( mode == "localhost" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"" + "http://localhost:8000/" + this.getLocalName() + "\"/></video>";
        } else if ( mode == "file" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"file://" + this.getLocalName() + "\"/></video>";
        }
        
        console.log("JBVideo.updateAsset(" + id + "," + "," + mode + ") =>" + newContent );
        return newContent;
    }    
}

function convertURLs( assetInstances, mode ) {
    console.log("convertURLs " + mode );
    for( id in assetInstances ) {
        console.log("Updating id " + id);
        var el = document.getElementById( id );
        if ( el != null ) {
            console.log("el " + el );
            var asset = assetInstances[ id ];
            var newContent = asset.updateAsset( id, mode );
            el.innerHTML = newContent;
        }
    }
}

function clearNode( node ) {
    while( node.firstChild ) {
        node.removeChild( node.firstChild );
    }
}

function checkMode( tags, mode ) {
    var el = -1;
    for(var i = 0; i < tags.length && el == -1; i++ ) {
        if ( mode.includes( tags[i] ) ) {
            el = i;
        }
    }
    if ( ( el < 0 ) || ( el >= tags.length ) ) {
        for(var i = 0; i < tags.length && el == -1; i++ ) {
            if ( tags[i] == "default" ) {
                el = i;
            }
        }    
    }
    if ( ( el < 0 ) || ( el >= tags.length ) ) {
        el = 0;
    }
    return el;
}

function createCharacter( container, character, mode, anim ) {
    var id = character.id;
    var tags = character.tags;
    var children = character.children;

    clearNode( container );
    n = document.createElement( "div" );
    n.id = id;
    if ( checkMode( tags, mode ) >= 0 ) {
        for( var ci = 0; ci < children.length; ci++ ) {
            var cid = children[i].id;
            var ctags = children[i].ctags;
            
        }
    } 
}