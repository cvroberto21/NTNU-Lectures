FROM continuumio/anaconda3
LABEL version="1.1" maintainer="Marcella Schutz <abthil023@protonmail.com>"
COPY startlab.sh /usr/bin/
RUN apt update && apt --fix-missing --yes dist-upgrade; \ 
 adduser conda --system; \
 apt install -y npm; \
 apt install -y ffmpeg; \
 /opt/conda/bin/conda upgrade --yes conda; \ 
 /opt/conda/bin/conda upgrade --yes anaconda; \
 /opt/conda/bin/conda install jupyterlab --quiet --yes; 
