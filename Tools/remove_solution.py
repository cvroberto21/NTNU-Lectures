#!/usr/bin/env python

import argparse
import sys
import pathlib

def remove_solution( fin, fout ):
    if args.verbose > 0:
        print('remove_solution', 'fin', fin, 'fout', fout )
    skip = False

    for i,line in enumerate( fin.readlines() ):
        f = line == '<div class="question_solution"><!-- start of question_solution -->'

        print('f', f, 'l', line)
        if ( line == '<div class="question_solution"><!-- start of question_solution -->\n' ):
            if args.verbose > 0:
                print( f"Found start of solution at line {i+1}")
            skip = True
        elif line == '</div><!-- end of question_solution -->\n':
            if args.verbose > 0:
                print( f"Found end of solution at line {i+1}")
            skip = False
        else:
            if ( not skip ):
                fout.write( line + '\n' )

args = None

def main( argv = None ):
    global args

    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument( 'file_or_dir', default = '-' )
    parser.add_argument( '-v', '--verbose', action='count', default = 0 )
    parser.add_argument( '-r', '--recursive', action='store_true', default = False )
    parser.add_argument( 'out_file_or_dir', default = '-' )
    args = parser.parse_args()

    print('args', args)
    files = []
    if args.file_or_dir == '-':
        files = [ sys.stdin ]
    else:
        fd = pathlib.Path( args.file_or_dir )
        if fd.is_file():
            files.append( fd.open('r') )

    ofiles = [ ]
    if args.out_file_or_dir == '-':
        ofiles = [ sys.stdout ]
    else:
        fd = pathlib.Path( args.out_file_or_dir )
        ofiles.append( fd.open('w') )
        

    map = zip( files, ofiles )

    for m in map:
        if args.verbose > 0:
            print(m)
        remove_solution( m[0], m[1] )


if __name__ == '__main__':
    main()