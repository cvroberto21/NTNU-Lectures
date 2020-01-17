#!/usr/bin/env python

import subprocess
import sys
import argparse
import pathlib

def main( argv = None ):
    if not argv:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser( description="Start a docker image with the current directory mounted as /data")
    parser.add_argument("--data_dir", "-d", default=".")
    parser.add_argument("container", default="abthil023/ntnu-lectures")
    parser.add_argument("--client_dir", "-c", default="/data")
    parser.add_argument("--port", "-p", default=8888)
    parser.add_argument("--client_port", default=8888)

    args = parser.parse_args( argv )
    
    data_dir = str( pathlib.Path( args.data_dir ).resolve() )
    client_dir = str( pathlib.Path( args.client_dir ).resolve() )

    cmd = [
        "docker",
        "run",
        "--volume",
        '"' + data_dir + '"' + ":" + '"' + client_dir + '"',
        "-i",
        "-t",
        "-p",
        str(args.port) + ":" + str(args.client_port),
        "/bin/bash --login -c",
        f"/opt/conda/bin/conda install jupyterlab -y --quiet && /opt/conda/bin/jupyter lab --notebook-dir={args.client_dir} --ip='*' --port={args.client_port} --no-browser --NotebookApp.token='' --NotebookApp.password='111111' --allow-root"
    ]   

    subprocess.call( cmd )

if __name__ == "__main__":
    main()


