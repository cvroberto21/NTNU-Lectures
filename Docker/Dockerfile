FROM continuumio/anaconda3

LABEL version="1.5" maintainer="Marcella Schutz <abthil023@protonmail.com>"

RUN mkdir /work
COPY startlab.sh run-jupyter.py run-npm.py /work/

ENV PATH="${PATH}:/work"

RUN chmod a+x /work/*; \
 apt update && apt --fix-missing --yes dist-upgrade; \ 
 adduser conda --system; \
 apt install -y npm; \
 apt install -y ffmpeg; \
 /opt/conda/bin/conda upgrade --yes conda; \ 
 /opt/conda/bin/conda upgrade --yes anaconda; \
 /opt/conda/bin/conda install jupyterlab --quiet --yes;

RUN python -m pip install pygments \
    youtube-dl \
    jinja2 \
    google-colab \
    papermill \
    pytexturepacker \
    patch \
    requests_oauthlib \ 
    PyGithub \
    gitpython \

    PyDrive \
    google-colab \
    portpicker \
    google-api-python-client \
    google-auth-oauthlib \
    google-auth-httplib2

RUN npm install -g canopy \
    scenejs



