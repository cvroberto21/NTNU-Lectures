#!/bin/bash

/opt/conda/bin/jupyter notebook --notebook-dir=/data --ip='*' --no-browser --port=8888 --NotebookApp.token='' --NotebookApp.password='' --allow-root
