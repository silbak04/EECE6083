#
# Copyright (C) 2014 by Samir Silbak
#
# Compiler Thoery - Parser
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

# http://www.cs.engr.uky.edu/~lewis/essays/compilers/rec-des.html

# http://stackoverflow.com/questions/9814528/recursive-descent-parser-implementation
# http://stackoverflow.com/questions/1960888/register-allocation-and-spilling-the-easy-way

#import scanner
#from scanner import update_line_cnt
#from scanner import get_tokens
from scanner import *

curr_tok_idx = 0
next_tok_idx = 0

curr_tok = ""
next_tok = ""
data_types = ["integer","float","bool","string"]

count    = 1

var_dec  = 0
proc_dec = 0

class parser:
    def __init__(self, tokens):
        self.curr_tok     = next(tokens)
        self.next_tok     = next(tokens)

        print self.curr_tok
        print self.next_tok

        self.curr_tok_typ = self.curr_tok[0]
        self.curr_tok_lex = self.curr_tok[1]

        print self.curr_tok_typ
        print self.curr_tok_lex

        self.next_tok_typ = self.next_tok[0]
        self.next_tok_lex = self.next_tok[1]

        print self.next_tok_typ
        print self.next_tok_lex
        #self.line_num  = self.tokens[2]

    def _get(self):
        print self.curr_tok
        self.next_tok     = next(self.curr_tok)
        print self.next_tok


    '''
    def _get_next_tok(self):
        self.curr_tok_typ = self.next_tok_typ
        self.curr_tok_lex = self.next_tok_lex

        self.next_tok     = next(tokens);
        self.next_tok_typ = self.next_tok[0]
        self.next_tok_lex = self.next_tok[1]
        '''

    #def __init__(self, tokens):
    #    self.tokens = tokens
    #def __init__(self, token_lex, token_type, line_num):
    #    self.token_type = token_type;
    #    self.token_lex  = token_lex;
    #    self.line_num   = line_num;

    #def _get_next_tok(self):
    #    global curr_tok
    #    global curr_t
    #    global next_t
    #    global next_tok
    #    global curr_lex
    #    global next_lex

    #    global count

    #    if (count):
    #        curr_t = next(self.tokens)
    #        count = 0
    #    else:
    #        curr_t = next_t

    #    next_t = next(self.tokens)

    #    #print "[1]" + str(curr_t)
    #    #print "[1]" + str(next_t)

    #    curr_tok = curr_t[0]
    #    next_tok = next_t[0]

    #    #print "[2]" + str(curr_tok)
    #    #print "[2]" + str(next_tok)

    #    curr_lex = curr_t[1]
    #    next_lex = next_t[1]

    #    #print curr_lex
    #    #print next_lex

    #    return next_tok

    '''
    def _type_mark(self, token_type):
        self.token_type = token_type

        if (self.token_type in data_types):
            return self.token_type
        else:
            return 0

    # might change everything to y combinators
    def _if_statement(self):
        if (next_tok == "if"):
            self._get_next_tok()
            if (next_tok != "("):
                print_error("[syntax error]: was expecting '(', received: ", next_tok, line_num)
                next(f)
            else:
                self._get_next_tok()
                self._expression()
                if (next_tok == ")"):
                    self._get_next_tok()
                    if (next_tok != "then"):
                        print_error("[syntax error]: was expecting 'then', received: ", next_tok, line_num)
                        next(f)
                    else:
                        self._get_next_tok()
                        _statement()
                        if (next_tok == ";"):
                            self._get_next_tok()
                            if (next_tok == "else"):
                                self._get_next_tok()
                                return _if_statement()
                            elif (next_tok == "end"):
                                self._get_next_tok()
                                if (next_tok == "if"):
                                    self._get_next_tok()
                                    return
                                else:
                                    print_error("[syntax error]: missing keyword 'if' after 'end'", "", line_num)

    def _arith_op(self):
        if (relational)

    def _return(self):
        if (next_tok == "return"):
            # keep track of addresses, return
            # back to procedure call

    def _expression(self):
        i = 0
        r = []
        print next_tok
        print next_lex
        while (next_tok != ";"):
            self._get_next_tok()
            if ((next_lex == "not") and (next_tok not in reserved_ids)):
                self._get_next_tok()
                r.append(~self._expression())
                yield ~self._expression()
                fwrite.write("R[%i] = not(R[%i])\n" %(i, i))
                print r[0]
                continue
            if (next_tok == ")"):
                r.append(self._arith_op())
                return r[0]
            if (next_tok == "&"):
                self._get_next_tok()
                r.append(self._expression())
                r[0] = r[0] & r[1]
                fwrite.write("R[%i] = R[%i] & R[%i])\n" %(i, i, i+1))
            elif (next_tok == "|"):
                self._get_next_tok()
                r.append(self._expression())
                r[0] = r[0] | r[1]
                fwrite.write("R[%i] = R[%i] | R[%i])\n" %(i, i, i+1))
            else:
                r[0] = r[r.__len__()-1]
                return r[0]

    def _term(self):
        factor    = _factor()
        token_typ = factor[0]
        token_lex = factor[1]
        while (token_typ != -1):
            if (token_typ == 
                self._get_next_tok()
                if (next_lex == "/" and next_tok == "divide"):

    def _factor(self):
        if (next_lex == "false"):
            return (next_tok, next_lex)
        elif (next_lex == "true"):
            return (next_tok, next_lex)
        elif (next_lex == "string"):
            return (next_tok, next_lex)
        elif (next_tok == "integer" or next_lex == "float"):
            return (next_tok, next_lex)
        elif (next_tok == "id" and next_lex not in reserved_ids):
            return (next_tok, next_lex)
        elif (next_lex == "("):
            return (next_lex, self._expression())
        else:
            return -1

    def _array_delcaration(self):

        if (next_lex == "integer"):
            self._get_next_tok()
            if (next_tok == "]"):
                return
            else:
                print_error("[syntax error]: missing closed square bracket ']'", "", line_num)
        else:
            print_error("[syntax error]: array size must be of type int", "", line_num)

    def _variable_dec(self):
        global var_dec
        var_dec = 0

        # make sure token is not a reserved id
        if (next_tok not in reserved_ids):
            self._get_next_tok()
            # check if we have declared an array
            if (next_tok == "["):
                self._get_next_tok()
                self._array_delcaration()
            # check for variable initialization
            # come back to handle this
            elif (next_tok == ":"):
                self._get_next_tok()
                if (next_tok == "="):
                    pass

            # check for end of var declaration
            elif (next_tok == ";"):
                return
        else:
            print curr_tok
            print curr_lex
            print next_lex

    #def _parameter(self):

    def _parameter_list(self):
        if (self._type_mark(next_tok)):
            self._get_next_tok()
            self._declaration()
            if (var_dec and (next_tok == "in" or next_tok == "out"))
                if (next_tok == ","):
                    self._get_next_tok()
                    self._declaration()
                elif (next_tok == ")"):
                    self._get_next_tok()
                    self._procedure_body()

                    return

    def _procedure_dec(self):
        if (next_tok == "("):
            self._get_next_tok()
            self._parameter_list()

            return

    def _procedure_body(self):
        #_declaration
        _program_body()


    def _declaration(self):
        global var_dec
        global proc_dec

        print curr_tok

        # check for variable declaration
        if (curr_tok == self._type_mark(curr_tok) and next_tok == "id"):# and not(eof)):
            var_dec = 1
            return

        # check for procedure declaration
        elif (curr_tok == "procedure" and next_tok == "id"):
            proc_dec = 1
            return

    def _assignment(self):
        if (next_tok == "id")

    def _statement(self):
        if (assignment):
            self._get_next_tok()
            self._assignment()
        elif (if_stment):
            self._get_next_tok()
            self._if_statement()
        elif (loop_stment):
            self._get_next_tok()

    def _program_body(self):

        self._get_next_tok()
        print curr_tok

        if (curr_tok == "global"):
            self._get_next_tok()
            self._declaration()

            if (proc_dec)
                self._get_next_tok()
                self._procedure_dec()
            elif (var_dec)
                self._get_next_tok()
                self._variable_dec()

        # make sure to handle this
        elif (curr_tok == "begin"):
            if (var_dec or proc_dec):
                print_error("[syntax error]: cannot have declarations inside 'begin' statement", "", line_num)
            else:
                pass

        else:
            print_error("[syntax error]: must be of type 'global'", "", line_num)

        while (next_tok != "eof"): return _program_body()
        #while (not(eof)): return _program_body()
        #while (curr_tok != "end" and next_tok != "program"): return _program_body()

    def _program_header(self):

        self._get_next_tok()
        print curr_tok

        if ((curr_tok == "program" and next_tok == "id")):# and not(eof)):
            print next_lex
            self._get_next_tok()

            if(next_tok == "is"):
                print next_tok
                self._get_next_tok()
                self._program_body()

                return
            else:
                print_error("[syntax error]: missing 'is' keyword", "", line_num)
        else:
            print_error("[syntax error]: program header must start with 'program _id_'", "", line_num)

        #return
        '''

if (__name__ == "__main__"):
    main()
    parse = parser(get_tokens())
    #parse._get()
    #parse._program_header()
