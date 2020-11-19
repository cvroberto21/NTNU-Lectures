#!/usr/bin/env python

import argparse
import sys
from bs4 import BeautifulSoup
import pathlib

import logging
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def strip_file( fin, fout, selector ):
    with open(fin,'r') as f:
        text_in = f.read() 
    
        soup = BeautifulSoup( text_in, 'html.parser' )
        sols = soup.select( selector )
        for s in sols:
            logger.debug( f'{s}' )
            s.decompose()
        
        soup.smooth()

        with open(fout,'w') as fo:
            fo.write( soup.prettify() )
    
def main( argv = None ):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(prog='Strip divs marked as solutions from an exam html file')
    parser.add_argument( 'files', nargs = '*', default = [sys.stdin ] )
    parser.add_argument( '--selector', default='div.question_solution')
    args = parser.parse_args( argv )

    for f in args.files:
        if f == sys.stdin:
            fout = sys.stdout
        else:
            p = pathlib.Path( f )
            suffix = p.suffix 
            stem = p.stem
            logger.debug( f'stem {stem}' )
            if stem.endswith('-solutions') or stem.endswith('_solutions'):
                stem = stem[:-len('-solutions')]
            elif stem.endswith('-solution') or stem.endswith('_solution'):
                stem = stem[:-len('-solution')]
            fout = p.parent / ( str(stem) + "-no-solutions" + str(suffix) )
        strip_file( p, fout, args.selector )

        logger.debug( f'{f} -> {fout}')


if __name__ == '__main__':
    main( )


