import subprocess
import pathlib
import os
import sys
import platform
from importlib import reload 

try:
    GIT_CMD
except NameError:
    GIT_CMD = 'git'
    
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = pathlib.Path(newPath).expanduser().resolve()

    def __enter__(self):
        self.savedPath = pathlib.Path.cwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def updateGit( url, dirname, branch,  root ):
        with cd( root ):
            p = pathlib.Path( dirname )
            if ( branch ):
                bs = " --branch " + branch
            else:
                bs = ""
            if not p.is_dir():
                print("cloning {0} from url {1} root {2}".format( dirname, url, root ), 'git command', GIT_CMD)
                    
                cmd = GIT_CMD + " clone " + bs + " " + url + " " + dirname 
                os.system( cmd )
            else:
                print("git directory exists")

            with cd( dirname ):
                print("Executing git pull")
                o = None
                try:
                    o = subprocess.check_output(GIT_CMD + " pull", stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError:
                    pass
                if ( o ):
                    print( 'git pull:' + o.decode('utf-8') )

updateGit('https://github.com/cvroberto21/NTNU-Lectures.git', 'NTNU-Lectures', 'mg', '.')

def gDriveLogin():
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials
    global GDrive

    # 1. Authenticate and create the PyDrive client.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    GDrive = drive
    return drive

def gDriveUpload( dir, file ):
    global GDrive

    if (not GDrive):
        gDriveLogin()
    # 2. Create & upload a file file.
    uploaded = drive.CreateFile( file )
    uploaded.SetContentFile( dir / file )
    uploaded.Upload()
    print('Uploaded file with ID {}'.format(uploaded.get('id')))


d = str( pathlib.Path( pathlib.Path('.') / 'NTNU-Lectures' ).resolve() )
if d not in sys.path:    
    sys.path.append(  d )
print('System Path', sys.path)

import jblecture

jblecture = reload(jblecture)
node = platform.node()

# %reload_ext jblecture
import jblecture
jblecture.load_ipython_extension( get_ipython() )

from jblecture import addJBImage, addJBVideo, addJBData
from jblecture import createTable
from jblecture import instTemplate
from jblecture import _a, createBase64ImageFromFigure, createSVGImageFromFigure
from jblecture import cfg
from jblecture import downloadDir, zipDirectory
from IPython.core.display import display, HTML, Math

doc = cfg['doc']
GDrive = None

import IPython
import uuid
from google.colab import output

class InvokeButton(object):
  def __init__(self, title, callback):
    self._title = title
    self._callback = callback

  def _repr_html_(self):
    callback_id = 'button-' + str(uuid.uuid4())
    output.register_callback(callback_id, self._callback)

    template = """<button id="{callback_id}" style="height:3cm;">{title}</button>
        <script>
          document.querySelector("#{callback_id}").onclick = (e) => {{
            //IPython.notebook.execute_cells_after()
            google.colab.kernel.invokeFunction('{callback_id}', [], {{}})
            e.preventDefault();
          }};
        </script>"""
    html = template.format(title=self._title, callback_id=callback_id)
    return html

def createRevealJSAndDownload():
    print('Create reveal.js and download it')
    doc.createRevealDownload( cfg['REVEAL_DIR'] )
    downloadDir( cfg['ROOT_DIR'] / "{title}_reveal.zip".format( title=title ), "reveal.js", cfg['ROOT_DIR'] )

def finalize():
    cfg['TITLE'] = title
    
    doc.createRevealDownload( cfg['REVEAL_DIR'] )
    if jblecture.jbgithub.createGitHub( cfg['TITLE'], cfg['ROOT_DIR']):
        print("Successful upload of presentation")
        print("You can access presentation at " + cfg['GITHUB_PAGES_URL'] )
    else:
        print("Upload of presentation failed")

# jblecture.jbgithub.login( jblecture.jbgithub.readGithubToken() )
# if ( cfg['GITHUB'] ):
#     print("Successful login to github")
# else:
#     print("Github integration disabled")

# This must come last
InvokeButton('Create and Download Reveal.js Slideshow', createRevealJSAndDownload )


