cfg = {}
defaults = {}

def createEnvironment( mycfg ):
    global cfg
    #print('jbdocument', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    for k in defaults:
        if k not in cfg:
            cfg[k] = defaults[k]
    #print('jbdocument', hex(id(cfg)))
    return cfg
