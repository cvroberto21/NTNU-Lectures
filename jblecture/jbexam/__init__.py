cfg = {}

def createEnvironment( mycfg ):
    global cfg
    #print('jbdocument', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    #print('jbdocument', hex(id(cfg)))
    return cfg
