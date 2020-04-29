FROM continuumio/anaconda3

LABEL version="1.5" maintainer="Marcella Schutz <abthil023@protonmail.com>"

RUN mkdir /work
COPY start_lab.sh start_notebook.sh run-jupyter.py run-npm.py /work/
RUN chmod a+x /work/*;

ENV PATH="${PATH}:/work"

RUN  \
    adduser conda --system; \
    apt-get update; \
    apt-get --fix-missing --yes dist-upgrade; \
    apt-get install -y npm; \
    apt-get install -y ffmpeg; \
    apt-get install -y vim; \
    apt-get install -y graphviz; \
    apt-get install -y dos2unix; \
    apt-get install -y libopencv-dev python3-opencv;
 
RUN \ 
    /opt/conda/bin/conda upgrade --yes conda; \
    /opt/conda/bin/conda upgrade --yes anaconda; \ 
    /opt/conda/bin/conda install python-graphviz --quiet --yes; \
    /opt/conda/bin/conda install -c conda-forge opencv

RUN \
    python -m pip install pygments \
    youtube-dl \
    jinja2 \
#    google-colab \
    papermill \
    pytexturepacker \
    patch \
    requests_oauthlib \ 
    PyGithub \
    gitpython \
    PyDrive \
    portpicker \
    google-api-python-client \
    google-auth-oauthlib \
    google-auth-httplib2 \
    docutils \
    pyopenssl

RUN npm install -g \
    canopy \
    scenejs

RUN dos2unix /work/*.sh

RUN \
    apt-get --purge remove -y dos2unix; \
    rm -rf /var/lib/apt/lists/*





