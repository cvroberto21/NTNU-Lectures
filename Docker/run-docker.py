#!/usr/bin/env python3

import subprocess
import sys
import argparse
import pathlib
import os
import configparser
import logging
import os

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger( __name__ )
logger.setLevel(logging.DEBUG )

defaults = {
    'docker' : {
        "verbose": "1",
        "data_dir" : "./",
        "work_dir" : "/work",
        "user" : "none", 
        "commands" : [ "shell" ],
        "local" : False,
        "kill" : False,
        "ports" : []
    },
    'commands' : {
        "shell" : [ "/bin/bash", "--login" ]
    }
}

def run_container( container ):
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
    logger.debug( f"check {o} container {container}" )
    for cl in o.splitlines():
        print("running", cl)
        img,id = cl.split()
        print("img", img, "id", id )
        if img == container:
            print("Found container")
            running.append(  id )
    return running

def container_exists( container ):
    cmd = [
        "docker",
        "container",
        "ls",
        "--filter",
        "status=exited",
        "--format",
        "{{.Image }} {{.ID }}",
    ]

    running = []
    o = subprocess.check_output( cmd ).decode('utf-8')
    logger.debug( f"check {o} container {container}" )
    for cl in o.splitlines():
        logger.debug( f"exited {cl}")
        img,id = cl.split()
        logger.debug( f"img {img} id {id}")
        
        if img == container:
            logger.info(f"found container")
            running.append(  id )
    return running

def kill_all( container ):
    ids = run_container( container )
    for id in ids:
        cmd = [
            "docker",
            "container",
            "stop",
            id,
        ]
        o = subprocess.check_output( cmd ).decode('utf-8')
        logger.debug( f"kill {o} container {container}" )
        cmd = [
            "docker",
            "container",
            "rm",
            id,
        ]
        o = subprocess.check_output( cmd ).decode('utf-8')
        logger.debug( f"kill {o} container {container}" )
        
def remove_duplicates( lst ):
    out = []
    for i in range(len(lst)-1, -1, -1 ):
        l = lst[i]
        if l not in out:
            out.append(l)
    return out 

def update_config( c_parser, args ):
    config = { **defaults }
    print('d', defaults )

    for s in c_parser.sections():
        print('s', s, config[s], c_parser[s] )
        for it in c_parser[s]:
            config[s][it] = eval( c_parser[s][it] )
        
    print('c', config)
    
    if args.container is not None:
        config['docker']['container'] = args.container
    # if args.image is not None:
    #     config['docker']['image'] = args.image
    if args.data_dir is not None:
        config['docker']['data_dir'] = args.data_dir
    if args.work_dir is not None:
        config['docker']['work_dir'] = args.work_dir
    if args.user is not None:
        config['docker']['user'] = args.user
    if args.verbose is not None:
        config['docker']['verbose'] = args.verbose
    if args.commands is not None and len(args.commands)>0:
        config['docker']['commands'] = args.commands
    
    print('cw', config)
    return config

def substitute_command( cmd, commands ):
    replaced = True
    while( replaced ):
        if ( len(cmd) == 1 ) and ( cmd[0] in commands):
            cmd = commands[ cmd[0] ].split()
        else:
            replaced = False
    return cmd

config = { 'docker' : {} }

def main( argv = None ):
    global config

    if not argv:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser( description="Start a docker image with the current directory mounted as /data")
    parser.add_argument("--config", "-c", default="run-docker.conf")
    parser.add_argument("--data_dir", "-d", default=None)
    parser.add_argument("--container", default=None)
#    parser.add_argument("--image", default=None)
    parser.add_argument("--work_dir", "-w", default=None)
    parser.add_argument("--port", "-p", action='append', default=[ ] )
    parser.add_argument("commands", nargs="*", default=None)
    parser.add_argument("--local", action="store_true", default=False)
    parser.add_argument("--kill", action="store_true", default=False)
    parser.add_argument("--user", default=None  )
    parser.add_argument("--verbose", "-v", action="count", default=None )

    args = parser.parse_args( argv )
    
    c_parser = configparser.ConfigParser()
    c_parser['docker'] = {}

    for it in defaults:
        if it not in c_parser:
            config['docker'][it] = defaults[it]
    
    logger.debug( "Reading c_parser file %s", args.config )
    c_parser.read( args.config )
    logger.debug( f"Loaded c_parser {c_parser}" )

    config = update_config(c_parser, args )
    
    logger.debug( f'container data_dir {config["docker"]["data_dir"]}  work_dir {config["docker"]["work_dir"]} ')
    
    data_dir = pathlib.Path( config["docker"]["data_dir"] ).resolve()
    client_dir = str( config["docker"]["work_dir"] )

    logger.debug( f"commands {config['docker']['commands']}")
    
    if int( config['docker']['verbose'] ) > 0:
        print( "Executing command", config['docker']['commands'] )

    if config['docker']['commands'] == "" or config['docker']['commands'] == [ "default" ]:
        config['docker']['commands'] = "shell"

    cmdExec = substitute_command( config['docker']['commands'], config['commands'] )

    if (config['docker']['local']):
        config['docker']['container'] = config['docker']['container'] + ":local"
    
    if ( config['docker']['kill'] ):
        kill_all( config['docker']['container'] )

    config['docker']['ports'] = remove_duplicates( config['docker']['ports'] )
    
    ids = run_container( config['docker']['container'] )
    logger.debug( f"id {ids}" )
    if len( ids ) == 0:
        existingIds = container_exists( args.container )
        if len(existingIds) == 0:
            
            if ( config['docker']['user'] == "" ) or ( config['docker']['user'] == "none" ):
                user_s = ""
            elif config['docker']['user'] == "default":
                user_s = str(os.getuid()) + ":" + str(os.getgid() )
            else:
                user_s = config['docker']['user']
            
            cmd = [
                "docker",
                "run",
                "--rm",
                "--volume", '"' + str(data_dir) + '' + ":" + '' + client_dir + '"',
                "--interactive",
                "--tty",
                user_s,
            ] + [
                '--publish=' + p for p in config['docker']['ports']
            ] + [
                '' + str( config['docker']['container'] ) +'',       
            ]
            cmd.extend( cmdExec ) 
        else:
            cmd = [
                "docker",
                "start",
                '--attach',
                '--user', args.user,
                '--interactive',
                '' + str( existingIds[0] ) +'',       
            ]         
    else:
        cmd = [
            "docker",
            "exec",
            '--user', args.user,
            "--interactive",
            "--tty",
            '' + str( ids[0] ) +'',       
        ]   
        cmd.extend( cmdExec )
    print(cmd)

    logger.debug( f'Running cmd {" ".join(cmd)}' )

    subprocess.call( " ".join( cmd ) )

if __name__ == "__main__":
    main( )

