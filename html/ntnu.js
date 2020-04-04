var atype = {
    JBDATA : 0,
    JBIMAGE_PNG : 10,
    JBIMAGE_SVG : 11,
    JBIMAGE_JPG : 12,
    JBVIDEO_MP4 : 30,    
};

const MAX_LOCAL_FILE_SIZE = (25*1024*1024);

class JBData {
    constructor( name, size=-1, url=None, data=None, localFileStem=None, mytype = JBData.atype.JBDATA, suffix="dat" ) {
        this.mytype = mytype;
        this.name = name;
        this.size = size;
        this.url = url;
        this.data = data;
        this.localFileStem = localFileStem;
        this.suffix = suffix;

        console.log("JBData(" + name + "," + url + "," + localFileStem + ")" );
    }

    updateAsset( id, mode ) {
        newContent = "";
        if ( mode === "path" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + this.getLocalName() + "\">" + this.name + "</a>";
        } else if ( mode === "url" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + this.url + "\">" + this.name + "</a>";
        } else if ( mode === "localhost" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"" + "http://localhost:8000/" + this.getLocalName() + "\">" + this.name + "</a>";
        } else if ( mode === "file" ) {
            newContent = "<a id=\"dat-" + id + "\" href=\"file://" + this.getLocalName() + "\">" + this.name + "</a>";
        } else if ( mode === "smart-path" ) {
            if ( this.size <= MAX_LOCAL_FILE_SIZE ) {
                newContent = this.updateAsset( id, "path" );
            } else {
                newContent = this.updateAsset( id, "url" )
            }
        }

        console.log("JBData.updateAsset(" + id + "," + "," + mode + ") =>" + newContent );
        return newContent;
    }
    
    getLocalName() {
        return this.localFileStem + "." + this.suffix
    }
}

JBData.atype = atype;

class JBImage extends JBData {
    constructor( name, size, width, height, url=null, data=null, localFileStem=None, suffix = null ) {
        var lfLen = 0;
        if (suffix == null ) {
            if (localFileStem != null ) {
                lfLen = localFileStem.length;
                if ( ( lfLen - 4 >= 0 ) && ( localFileStem. substring( lfLen - 4, lfLen ) == ".png" ) ) {
                    suffix = "png";
                } else if ( ( lfLen - 4 >= 0 ) && ( localFileStem. substring( lfLen - 4, lfLen ) == ".svg" ) ) {
                    suffix = "svg";
                } else if ( ( lfLen - 4 >= 0 ) && ( localFileStem. substring( lfLen - 4, lfLen ) == ".jpg" ) ) {
                    suffix = "jpg";
                } else if ( (lfLen - 5 >= 0 ) && ( localFileStem. substring( lfLen -5, lfLen ) == ".jpeg" ) ) { 
                    suffix = "jpeg";
                }
            }
        }

        if ( ( localFileStem != null ) && ( lfLen - suffix.length - 1 >= 0 ) && ( localFileStem.substring( lfLen - suffix.length - 1, lfLen ) == "." + suffix  ) ) {
            localFileStem = localFileStem.substring( 0, lfLen - suffix.length - 1 );
        }

        var mytype = null;
        if ( suffix == "png" ) {
            mytype = JBData.atype.JBIMAGE_PNG; 
        } else if ( suffix == "svg") {
            mytype = JBData.atype.JBIMAGE_SVG; 
        } else if ( ( suffix == "jpg") || ( suffix == "jpeg" ) ) {
            mytype = JBData.atype.JBIMAGE_JPG;
        } 
        super( name, size, url, data, localFileStem, mytype, suffix );
        this.width = width;
        this.height = height;
        console.log("JBImage(" + name + "," + size + "," + url + "," + localFileStem + "." + suffix + ")" );
    }

    // modes are null/"auto", "url", "localhost", "path", "inline", "file", "smart-path"
    updateAsset( id, mode ) {
        var newContent = "";
        if ( mode == "path" ) {
            if ( this.atype == "svg" ) {
//                newContent = "<object id=\"img-" + id + "\"" + " type=\"image/svg+xml\"" + " data=\"" + this.getLocalName() + "\"></object>";
                newContent = "<img id=\"img-" + id + "\" src=\"" + this.getLocalName() + "\"/>";
            } else {
                newContent = "<img id=\"img-" + id + "\" src=\"" + this.getLocalName() + "\"/>";
            }
        } else if ( mode == "url" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"" + this.url + "\"/>";
        } else if ( mode == "localhost" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"" + "http://localhost:8000/" + this.getLocalName() + "\"/>";
        } else if ( mode == "file" ) {
            newContent = "<img id=\"img-" + id + "\" src=\"file://" + this.getLocalName() + "\"/>";
        } else if ( mode === "smart-path" ) {
            if ( this.size <= MAX_LOCAL_FILE_SIZE ) {
                console.log( "JBImage.updateAsset(" + id + "," + mode + ") chooses path " + this.size );
                newContent = this.updateAsset( id, "path" );
            } else {
                console.log( "JBImage.updateAsset(" + id + "," + mode + ") chooses path " + this.size );
                newContent = this.updateAsset( id, "url" )
            }
        }

        console.log("JBImage.updateAsset(" + id + "," + mode + ") =>" + newContent );
        return newContent;
    }    
}

class JBVideo extends JBData {
    constructor( name, size, width, height, url=None, data=None, localFileStem=None ) {
        super( name, size, url, data, localFileStem, JBData.atype.JBVIDEO, "mp4");
        this.width = width;
        this.height = height;
        console.log("JBVideo(" + name + "," + size  + "," + url + "," + localFileStem + ")" );
    }

    updateAsset( id, mode ) {
        var newContent = "";
        if ( mode == "path" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"" + this.getLocalName() + "\"/></video>";
        } else if ( mode == "url" ) {
            newContent = "<iframe id=\"vid-" + id + "\" src=\"" + this.url + "\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>";
        } else if ( mode == "localhost" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"" + "http://localhost:8000/" + this.getLocalName() + "\"/></video>";
        } else if ( mode == "file" ) {
            newContent = "<video id=\"vid-" + id + "\" controls> <source src=\"file://" + this.getLocalName() + "\"/></video>";
        } else if ( mode === "smart-path" ) {
            if ( this.size <= MAX_LOCAL_FILE_SIZE ) {
                newContent = this.updateAsset( id, "path" );
            } else {
                newContent = this.updateAsset( id, "url" )
            }
        }
        
        console.log("JBVideo.updateAsset(" + id + "," + "," + mode + ") size (" + this.size + ") =>" + newContent );
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