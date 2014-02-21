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

data_types = ["integer","float","bool","string"]

class parser:
    def __init__(self, tokens):
        self.tokens   = tokens
        self.curr_tok = next(self.tokens)
        self.next_tok = next(self.tokens)

        self.curr_tok_typ = self.curr_tok[0]
        self.curr_tok_lex = self.curr_tok[1]

        self.next_tok_typ = self.next_tok[0]
        self.next_tok_lex = self.next_tok[1]

        #self.line_num  = self.tokens[2]

        self.var_dec = 0
        self.prc_dec = 0

        return

    def _get_next_tok(self):
        self.curr_tok_typ = self.next_tok_typ
        self.curr_tok_lex = self.next_tok_lex

        self.next_tok     = next(self.tokens);
        self.next_tok_typ = self.next_tok[0]
        self.next_tok_lex = self.next_tok[1]

        return

    def _type_mark(self, token_type):
        self.token_type = token_type

        if (self.token_type in data_types):
            return self.token_type
        else:
            return 0

    # might change everything to y combinators
    def _if_statement(self):
        if (self.next_tok_typ == "if"):
            self._get_next_tok()
            if (self.next_tok_lex != "("):
                print_error("[syntax error]: was expecting '(', received: ", self.next_tok_lex, line_num)
                next(f)
            else:
                self._get_next_tok()
                self._expression()
                if (self.next_tok_lex == ")"):
                    self._get_next_tok()
                    if (self.next_tok_typ != "then"):
                        print_error("[syntax error]: was expecting 'then', received: ", self.next_tok_typ, line_num)
                        next(f)
                    else:
                        self._get_next_tok()
                        _statement()
                        if (self.next_tok_lex == ";"):
                            self._get_next_tok()
                            if (self.next_tok_typ == "else"):
                                self._get_next_tok()
                                return _if_statement()
                            elif (self.next_tok_typ == "end"):
                                self._get_next_tok()
                                if (self.next_tok_typ == "if"):
                                    self._get_next_tok()
                                    return
                                else:
                                    print_error("[syntax error]: missing keyword 'if' after 'end'", "", line_num)

    def _arith_op(self):
        if (relational)

    def _return(self):
        if (self.next_tok_typ == "return"):
            # keep track of addresses, return
            # back to procedure call

    def _expression(self):
        i = 0
        r = []
        print self.next_tok_typ
        print self.next_tok_lex
        while (self.next_tok_lex != ";"):
            #if ((self.next_tok_typ == "not") and (self.next_tok_typ not in reserved_ids)):
            if (self.next_tok_typ == "not"):
                self._get_next_tok()
                if (self.next_tok_lex not in reserved_ids)):
                    self._get_next_tok()
                    r.append(~self._expression())
                    yield ~self._expression()
                    fwrite.write("R[%i] = not(R[%i])\n" %(i, i))
                    print r[0]
                    continue
            if (self.next_tok_typ == ")"):
                r.append(self._arith_op())
                return r[0]
            if (self.next_tok_typ == "&"):
                self._get_next_tok()
                r.append(self._expression())
                r[0] = r[0] & r[1]
                fwrite.write("R[%i] = R[%i] & R[%i])\n" %(i, i, i+1))
            elif (self.next_tok_typ == "|"):
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
                if (self.next_tok_lex == "/" and self.next_tok_typ == "divide"):

    def _factor(self):
        if (self.next_tok_lex == "false"):
            return (self.next_tok_typ, self.next_tok_lex)
        elif (self.next_tok_lex == "true"):
            return (self.next_tok_typ, self.next_tok_lex)
        elif (self.next_tok_lex == "string"):
            return (self.next_tok_typ, self.next_tok_lex)
        elif (self.next_tok_typ == "integer" or self.next_tok_lex == "float"):
            return (self.next_tok_typ, self.next_tok_lex)
        elif (self.next_tok_typ == "id" and self.next_tok_lex not in reserved_ids):
            return (self.next_tok_typ, self.next_tok_lex)
        elif (self.next_tok_lex == "("):
            return (self.next_tok_lex, self._expression())
        else:
            return -1

    def _array_delcaration(self):

        if (self.next_tok_lex == "integer"):
            self._get_next_tok()
            if (self.next_tok_typ == "]"):
                return
            else:
                print_error("[syntax error]: missing closed square bracket ']'", "", line_num)
        else:
            print_error("[syntax error]: array size must be of type int", "", line_num)

    def _variable_dec(self):
        self.var_dec = 0

        print self.next_tok_typ
        print self.next_tok_lex
        # make sure token is not a reserved id
        if (self.next_tok_lex not in reserved_ids):
            self._get_next_tok()
            # check if we have declared an array
            if (self.next_tok_lex == "["):
                self._get_next_tok()
                self._array_delcaration()
            # check for variable initialization
            # come back to handle this
            elif (self.next_tok_lex == ":"):
                self._get_next_tok()
                if (self.next_tok_lex == "="):
                    pass

            # check for end of var declaration
            elif (self.next_tok_lex == ";"):
                print self.next_tok_lex
                return

    #def _parameter(self):

    def _parameter_list(self):
        if (self._type_mark(self.next_tok_typ)):
            self._get_next_tok()
            self._declaration()
            if (self.var_dec and (self.next_tok_typ == "in" or self.next_tok_typ == "out")):
                if (self.next_tok_lex == ","):
                    self._get_next_tok()
                    self._declaration()
                elif (self.next_tok_lex == ")"):
                    self._get_next_tok()
                    self._procedure_body()

                    return

    def _procedure_dec(self):
        if (self.next_tok_lex == "("):
            self._get_next_tok()
            self._parameter_list()

            return

    def _procedure_body(self):
        #_declaration
        _program_body()


    def _declaration(self):

        # check for variable declaration
        if (self.next_tok_typ == self._type_mark(self.next_tok_typ)):
            self._get_next_tok()
            if (self.next_tok_typ == "id"):
                self.var_dec = 1
                return

        # check for procedure declaration
        elif (self.next_tok_typ == "procedure"):
            if (self.next_tok_typ == "id"):
                self.prc_dec = 1
                return

    #def _assignment(self):
    #    if (self.next_tok_typ == "id")

    #def _statement(self):
    #    if (assignment):
    #        self._get_next_tok()
    #        self._assignment()
    #    elif (if_stment):
    #        self._get_next_tok()
    #        self._if_statement()
    #    elif (loop_stment):
    #        self._get_next_tok()

    def _program_body(self):

        if (self.next_tok_typ == "global"):
            print self.next_tok_typ
            self._get_next_tok()
            print self.next_tok_typ
            self._declaration()

            if (self.prc_dec):
                #self._get_next_tok()
                self._procedure_dec()
            elif (self.var_dec):
                #self._get_next_tok()
                self._variable_dec()

        # make sure to handle this
        elif (self.curr_tok_typ == "begin"):
            if (self.var_dec or self.prc_dec):
                print_error("[syntax error]: cannot have declarations inside 'begin' statement", "", line_num)
            else:
                pass

        else:
            print_error("[syntax error]: must be of type 'global'", "", line_num)

        #while (self.next_tok_typ != "eof"): return _program_body()
        #while (not(eof)): return _program_body()
        #while (self.curr_tok_typ != "end" and self.next_tok_typ != "program"): return _program_body()

    def _program_header(self):

        print self.curr_tok_typ
        if ((self.curr_tok_typ == "program" and self.next_tok_typ == "id")):# and not(eof)):
            print self.next_tok_lex
            self._get_next_tok()

            if(self.next_tok_typ == "is"):
                print self.next_tok_typ
                self._get_next_tok()
                self._program_body()

                return
            else:
                print_error("[syntax error]: missing 'is' keyword", "", line_num)
        else:
            print_error("[syntax error]: program header must start with 'program _id_'", "", line_num)

        #return

if (__name__ == "__main__"):
    main()
    parse = parser(get_tokens())
    parse._program_header()
