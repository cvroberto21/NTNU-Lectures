#!/usr/bin/env python

import subprocess
import sys
import argparse
import pathlib

def runningContainer( container ):
    cmd = [
        "docker",
        "container",
        "ls",
        "--filter",
        "status=running",
        "--format",
        "{{.Image }} {{.ID }}",
    ]

    running = None
    o = subprocess.check_output( cmd ).decode('utf-8')
    print("check", o, "container", container )
    for cl in o.splitlines():
        print("running", cl)
        img,id = cl.split()
        print("img", img, "id", id )
        if img == container:
            print("Found container")
            running = id
            break
    return running

def main( argv = None ):
    if not argv:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser( description="Start a docker image with the current directory mounted as /data")
    parser.add_argument("--data_dir", "-d", default=".")
    parser.add_argument("--container", default="abthil023/ntnu-lectures")
    parser.add_argument("--client_dir", "-c", default="/data")
    parser.add_argument("--port", "-p", default=8888)
    parser.add_argument("--client_port", default=8888)
    parser.add_argument("--command", default="lab")

    args = parser.parse_args( argv )
    
    data_dir = str( pathlib.Path( args.data_dir ).resolve() )
    client_dir = str( args.client_dir )

    print( "Command", args.command )

    if args.command == "lab":
        cmdExec = [ "/bin/bash", "--login", "-c",
            '' + f"/opt/conda/bin/conda install jupyterlab -y --quiet && /opt/conda/bin/jupyter lab --notebook-dir={args.client_dir} --ip='*' --port={args.client_port} --no-browser --NotebookApp.token='' --NotebookApp.password='' --allow-root" + ''
        ]
    elif args.command == "shell":
        cmdExec = [ "/bin/bash", "--login" ]
    else:
        cmdExec = args.command

    id = runningContainer( args.container )
    print("id", id)
    if not id:
        cmd = [
            "docker",
            "run",
            "--volume",
            '' + data_dir + '' + ":" + '' + client_dir + '',
            # "-i",
            # "-t",
            "-p",
            str(args.port) + ":" + str(args.client_port),
            '' + str( args.container ) +'',       
        ]   
    else:
        cmd = [
            "docker",
            "exec",
            "-i",
            "-t",
            '' + str( id ) +'',       
        ]   

    cmd.extend( cmdExec )

    print("Running cmd", " ".join(cmd) )

    subprocess.call( cmd )

if __name__ == "__main__":
    main()


