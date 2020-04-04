#!/bin/bash

/opt/conda/bin/jupyter lab --notebook-dir=/data --ip='*' --no-browser --port=8888 --NotebookApp.token='' --NotebookApp.password='' --allow-root
