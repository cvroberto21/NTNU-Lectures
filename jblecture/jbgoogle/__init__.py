import importlib
import logging

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )

defaults = {'GDRIVE' : None }
cfg = {}

def gDriveLogin( ):
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials
    global cfg

    # 1. Authenticate and create the PyDrive client.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)
    cfg['GDRIVE'] = drive
    return drive

def gDriveUpload( dir, file ):
    global cfg
    if ( not cfg['GDRIVE'] ):
        gDriveLogin()
    # 2. Create & upload a file "file".
    uploaded = cfg['GDRIVE'].CreateFile( file )
    uploaded.SetContentFile( dir / file )
    uploaded.Upload()
    logger.debug('Uploaded file with ID %s', uploaded.get('id'))
    return uploaded.get('id')

def installModules( ):
    from ..jbgithub import runCommand
    for p in [ "PyDrive", "google-colab", "portpicker", "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2" ]:
        try:
            importlib.import_module( p )
        except ModuleNotFoundError:
            logger.debug('Using pip to install missing dependency ' +  p )
            runCommand("python -m pip" + " install " + p, False )

def loadModules():
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials

def createEnvironment( params = {} ):
    global cfg
    cfg = { **defaults, **params }
    cfg['GDRIVE'] = None

    installModules()
    loadModules()
    return cfg
