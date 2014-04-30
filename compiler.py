#! /usr/bin/env python

import sys
import argparse
import subprocess

from code.scanner import *
from code.parser import *
from code.exceps import *
from code import *

argparser = argparse.ArgumentParser(description='EECS 6083 Compiler')

argparser.add_argument('filename', help='input .src file')
args = argparser.parse_args()

src_filename = args.filename
gen_filename = args.filename.rsplit(".", 1)[0] + '.c'
out_filename = args.filename.rsplit(".", 1)[0]

subprocess.call(['./code/./parser.py', src_filename])

if scanner.scanner_error or parser.parser_error:
    print "-"*50
    print "BUILD FAILED"
    subprocess.call(['rm', gen_filename])
    sys.exit(1)

return_code = subprocess.call(['gcc', '-m32', '-Wno-int-to-pointer-cast', '-Wno-pointer-to-int-cast', '-o', out_filename, \
                               '-I', 'runtime', 'runtime/runtime.c', gen_filename])

if return_code == 1:
    print "GCC ERROR"
    sys.exit(return_code)

subprocess.call([out_filename])
