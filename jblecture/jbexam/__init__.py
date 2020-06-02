from .jbexam import JBExam

cfg = {}
defaults = {

}

def createEnvironment( mycfg ):
    global cfg
    #print('jbexam', hex(id(cfg)), hex(id(mycfg)))
    cfg = mycfg
    for k in defaults:
        if k not in cfg:
            cfg[k] = defaults[k]
    #print('jbexam', hex(id(cfg)))
    jbexam.createEnvironment( cfg )
    return cfg
