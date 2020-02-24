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

    running = []
    o = subprocess.check_output( cmd ).decode('utf-8')
    print("check", o, "container", container )
    for cl in o.splitlines():
        print("running", cl)
        img,id = cl.split()
        print("img", img, "id", id )
        if img == container:
            print("Found container")
            running.append(  id )
    return running

def killAll( container ):
    ids = runningContainer( container )
    for id in ids:
        cmd = [
            "docker",
            "container",
            "stop",
            id,
        ]
        o = subprocess.check_output( cmd ).decode('utf-8')
        print("killAll", o, "container", container )
        cmd = [
            "docker",
            "container",
            "rm",
            id,
        ]
        o = subprocess.check_output( cmd ).decode('utf-8')
        print("killAll", o, "container", container )

def main( argv = None ):
    if not argv:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser( description="Start a docker image with the current directory mounted as /data")
    parser.add_argument("--data_dir", "-d", default=".")
    parser.add_argument("--container", default="abthil023/ntnu-lectures")
    parser.add_argument("--client_dir", "-c", default="/data")
    parser.add_argument("--port", "-p", default=8888)
    parser.add_argument("--client_port", default=8888)
    parser.add_argument("commands", nargs="+", default="lab")
    parser.add_argument("--local", action="store_true", default=False)
    parser.add_argument("--kill", action="store_true", default=False)

    args = parser.parse_args( argv )
    
    data_dir = str( pathlib.Path( args.data_dir ).resolve() )
    client_dir = str( args.client_dir )

    print( "Command", args.commands )

    if args.commands == []:
        cmdExec = [ "/usr/bin/startlab.sh" ]
    elif args.commands == [ "lab" ]:
        # cmdExec = [ "/bin/bash", "--login", "-c",
        #     '' + f"/opt/conda/bin/conda install jupyterlab -y --quiet && /opt/conda/bin/jupyter lab --notebook-dir={args.client_dir} --ip='*' --port={args.client_port} --no-browser --NotebookApp.token='' --NotebookApp.password='' --allow-root" + ''
        # ]
        cmdExec = [ "/usr/bin/startlab.sh" ]
        
    elif args.commands == [ "shell" ]:
        cmdExec = [ "/bin/bash", "--login" ]
    else:
        cmdExec = args.commands 

    if (args.local):
        args.container = args.container + ":local"
    
    if ( args.kill ):
        killAll( args.container )

    ids = runningContainer( args.container )
    print("id", ids)
    if len( ids ) == 0:
        cmd = [
            "docker",
            "run",
            "--volume",
            '' + data_dir + '' + ":" + '' + client_dir + '',
             "--interactive",
             "--tty",
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
            '' + str( ids[0] ) +'',       
        ]   

    cmd.extend( cmdExec )

    print("Running cmd", " ".join(cmd) )

    subprocess.call( cmd )

if __name__ == "__main__":
    main()


