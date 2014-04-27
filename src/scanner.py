#!/usr/bin/env python
#
# Copyright (C) 2014 by Samir Silbak
#
# Compiler Thoery - Scanner
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#

import os
import sys

from tokens import token_table as token_table
from printer import *

char_cnt  = 0

char_idx  = 0
line_num  = 1

curr_char = ""
next_char = ""

reserved_ids = ['string'    , 'integer' , 'bool'   , 'float'    ,
                'global'    , 'in'      , 'out'    , 'if'       ,
                'then'      , 'else'    , 'is'     , 'for'      ,
                'not'       , 'true'    , 'false'  , 'program'  ,
                'procedure' , 'begin'   , 'return' , 'end'      ]

data_types = reserved_ids[0:4]

def read_file(file_read):
    global f_read
    f_read = open(file_read).read()

    return f_read

def get_next_char():
    global curr_char
    global next_char
    global char_idx

    curr_char = f_read[char_idx]

    if (char_idx+1 == len(f_read)):
        next_char = None
    else:
        next_char = f_read[char_idx+1]

    char_idx += 1

    return next_char

def update_line_cnt():
    global line_num

    # some of test files provided were done in windows...
    if (next_char == "\r"): get_next_char()
    if (next_char == "\n"): line_num += 1

    return line_num

def _token((tok, lex), line_num):
    return (tok, lex, line_num)

def debug(message, line, tok):

    print message,"\t" + tok, "\t\t" + str(line)
    return

def get_tokens():
    global line_num
    global reserved_ids

    error          = 0
    debug          = 0

    curr_token     = ""

    relational_ops = ["<", ">", "!", ":"]

    while (next_char is not(None)):

        get_next_char()

        # check if char is part of the alphabet
        if (curr_char.isalpha()):
            curr_token = curr_char

            # keep fetching the next char until it's no longer
            # alphanumeric or "_" and we have not hit the end
            # of a newline
            while ((next_char.isalnum() or next_char == "_")):#(next_char != "\n" or next_char != "\r")):
                curr_token += next_char
                if (get_next_char() == None): break

            if (debug): debug("alhpa: ", line_num, curr_token)

            # force case insensitive
            curr_token = curr_token.lower()

            if (curr_token in reserved_ids):
                yield _token((curr_token, curr_token), line_num)
            else:
                yield _token(("id", curr_token), line_num)

        # check if char is a digit or a decmial point
        elif (curr_char.isdigit() or curr_char == "."):
            curr_token = curr_char
            error      = 0

            # keep fetching the next char as long as the next
            # char is a digit or we do not have an extra decimal
            # point in our input stream
            while ((next_char.isdigit() or next_char == ".")):# and (next_char != "\n")):

                # check for more than one decimal point in input stream
                if (((next_char == ".") and (next_char not in curr_token)) or next_char.isdigit()):
                    curr_token += next_char
                    get_next_char()

                else:
                    error = 1
                    break

            if (debug): debug("digit: ", line_num, curr_token)

            if (error):
                while (next_char != "\n"):
                    curr_token += next_char
                    get_next_char()

                if (debug): debug("err digit: ", line_num, curr_token)

                yield _token((curr_token, curr_token), line_num)
                print_error("unknown token: ", curr_token, line_num)

            else:

                # check for leading zero
                if (curr_token[0] == "."):
                    curr_token = '0' + curr_token
                    print_warning("leading zero is missing, it has been added", line_num)

                # check for trailing zero
                if (curr_token[-1] == "."):
                    curr_token += '0'
                    print_warning("trailing zero is missing, it has been added", line_num)

                # check for type int or float
                if ("." in curr_token):
                    yield _token(("float", curr_token), line_num)
                else:
                    yield _token(("integer", curr_token), line_num)

        # check for strings
        elif (curr_char == "\""):
            #global char_cnt
            curr_token = ""

            # keep fetching the next char as long as the next char
            # is not an end quote or an escape sequence
            while ((next_char not in ["\"", "\\"]) and next_char != "\n"):
                curr_token += next_char
                #char_cnt=char_cnt+1
                get_next_char()

            if (debug): debug("seq: ", line_num, curr_token)

            if ((next_char == "\"")):#) and (next_char != "\n")):
                #curr_token += next_char
                get_next_char()
                yield _token(("string", curr_token), line_num)

                if (debug): debug("string: ", line_num, curr_token)

            else:
                print_error("missing quote", "", line_num)
                yield _token((curr_token, curr_token), line_num)

        else:

            # ignore whitespace
            if (curr_char.isspace()): pass

            # check for equality symbol (==)
            elif (curr_char == "=" and next_char == "="):
                curr_token = curr_char + next_char
                get_next_char()
                yield _token((token_table[curr_token], curr_token), line_num)

            # check for relational operators: '<, >, !, :'
            elif (curr_char in relational_ops):
                curr_token = curr_char

                # check for something like !asdf
                #if (next_char.isalnum()):

                # check for: '<=, >=, !=, :='
                if (next_char == "="):
                    curr_token += next_char
                    get_next_char()
                    yield _token((token_table[curr_token], curr_token), line_num)

                # check for unsupported operators: '<<, >>, !!, ::'
                elif (next_char in relational_ops):
                    curr_token += next_char
                    get_next_char()

                    print_error("operator not supported: ", curr_token, line_num)
                    yield _token((curr_token, curr_token), line_num)

                else:
                    yield _token((token_table[curr_token], curr_token), line_num)

            # check for division or comment
            elif (curr_char == "/"):
                curr_token = curr_char

                if (debug): debug("div: ", line_num, curr_token)

                #while ((next_char != "/" and (next_char.isdigit() or next_char.isalnum()) and (next_char != "\n")):
                if (next_char != "/"):# and next_char != "\n"):
                    yield _token((token_table[curr_token], curr_token), line_num)

                elif (next_char == "/"):
                    while (next_char != "\n"):
                        curr_token += next_char
                        get_next_char()

                    if (debug):
                        debug("comment: ", line_num, curr_token)
                        # most likely token_table will be gone, much simplier to just
                        # pass in the strings directly
                        yield _token((token_table[curr_token[0:2]], curr_token), line_num)

            # check for escape sequences
            elif (curr_char == "\\"):
                curr_token = curr_char

                if (debug): debug("esq seq: ", line_num, curr_token)

                if (next_char in ["t", "n"]):# and next_char != "\n"):
                    curr_token += next_char
                    get_next_char()

                    yield _token((token_table[curr_token], curr_token), line_num)

                else:
                    curr_token += next_char
                    get_next_char()
                    print_error("escape sequence not supported: ", curr_token, line_num)

            elif (curr_char in token_table):
                yield _token((token_table[curr_char], curr_char), line_num)
                if (debug): debug("tok table: ", line_num, curr_char)

            else:
                curr_token = curr_char

                print_error("unknown token: ", "'" + curr_token + "'", line_num)
                yield _token((curr_token, curr_token), line_num)

        update_line_cnt()

    yield _token(("eof", next_char), line_num)

def check_src_file():

    program_file = sys.argv[1]
    if (program_file.endswith('.src')):
        read_file(program_file)
        return 1
    else:
        print "%s: file format not recognized" %(program_file)
    return

if (__name__ == "__main__"):
    if (check_src_file()):
        for token in get_tokens():
            print token
