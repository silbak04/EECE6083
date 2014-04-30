import parser
#import sys
#sys.path.append("../")

#import compiler
#from compiler import *
#print compiler.parse_err

#import os, sys
#lib_path = os.path.abspath('./')
#sys.path.append(lib_path)

#from .. compiler import *
#import compiler
#from compiler import parse_err as parse_err
#print parse_err

class ErrorToken(Exception):
    def __init__(self, exp_tok, rec_tok):
        self.exp_tok = exp_tok
        self.rec_tok = rec_tok

        return

    def print_error(self, err_msg):

        self.err_msg = err_msg

        red     = '\033[31m'
        default = '\033[0m'

        print red + "[syntax error]: " + default + "%s" %(self.err_msg)
        parser.parse_err = True

        return parser.parse_err

    def print_warning(self, err_msg):
        self.err_msg = err_msg

        yellow  = '\033[93m'
        default = '\033[0m'

        print yellow + "[warning]: " + default + "%s" %(self.err_msg)
