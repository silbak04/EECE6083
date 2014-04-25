#!/usr/bin/env python
#
# Copyright (C) 2014 by Samir Silbak
#
# Compiler Thoery - Parser/Type Checker/Code Generator
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

from scanner import *
from exceps  import *
from symbol_table import *

r = []
reg = []

i = 0
count = 0
if_sub_idx = -1
for_sub_idx = -1

class parser(object):
    def __init__(self, tokens):
        self.tokens = tokens

        self.curr_token = next(self.tokens)

        self.curr_tok      = token_symbol()
        self.curr_tok.type = self.curr_token[0]
        self.curr_tok.lex  = self.curr_token[1]
        self.curr_tok.line = self.curr_token[2]

        #self.var_dec = False
        self.prc_dec = False
        self.prc_call = False

        self._assign = False
        self._if     = False
        self._for    = False
        self._return = False

        self.mem_addr = 0
        self.not_exp = False
        self.local = False
        self.proc_name = None
        self.prc_var_dec = False
        self.prog_body = False

        return

    def _get_next_tok(self):

        self.curr_token    = next(self.tokens)
        self.curr_tok      = token_symbol()
        self.curr_tok.type = self.curr_token[0]
        self.curr_tok.lex  = self.curr_token[1]
        self.curr_tok.line = self.curr_token[2]

        return self.curr_tok

    def _skip_line(self):
        while (next_char != "\n"):
            self._get_next_tok()
            continue
        return

    def _check_for_semicolon(self):
        try:
            if (self.curr_tok.lex != ";"):
                raise ErrorToken(";", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

    def _if_error(self, error):
        # TODO: change how this is whole function is handled
        self.error = error
        self._get_next_tok()
        '''
        if we get an error of 1, this means that we did not receive '('
        token, so check for expression, keep parsing then return from error,
        go back to if statement, try to parse the next correct token so we do
        not have to be redundant in here and reparse everything.  if we get
        an error back in 'if' block and it's none of these cases, then we're
        just going to go ahead and skip the whole line
        '''
        if (self.error == 1):
            self._expression()
            return self._get_next_tok()
        # error 2: we did not receive ')' token after expression, get next
        # 'correct' token, return back to _if_statement and try to keep parsing
        if (self.error == 2):
          return self._get_next_tok()
        if (self.error == 3):
          return self._get_next_tok()
        if (self.error == 4):
          return self._get_next_tok()
        if (self.error == 5):
            return self._get_next_tok()
        if (self.error == 6):
            return self._get_next_tok()
        if (self.error == 7):
            return self._get_next_tok()

    # <statement> ::= <assignment_statement>
    #               | <if_statement>
    #               | <loop_statement>
    #               | <return_statement>
    #               | <procedure_call>
    def _statement(self):
        global count
        global i
        global if_sub_idx
        global for_sub_idx

        # check for assignment
        if (not(self.prc_call) and (self.curr_tok.type == "id") and
           (self.curr_tok.lex not in reserved_ids)):
            self._assignment()

            # assignment is done, assign register to memory location
            if (self.prc_dec):
                i+=1
                f.write("R[%i] = M[FP+%i];\n" %(i, symbol_table[reg[0].lex].address))
                f.write("M[R[%i]] = R[%i];\n" %(i, i-1))
                i+=1
            else:
                f.write("M[FP+%i] = R[%i];\n" %(symbol_table[reg[0].lex].address, i))

            #reg[0].value = int(r[0])
            self._check_for_semicolon()
            a = self._get_next_tok()
            print "=================================="
            print "NEXT TOKEN BEFORE LEAVING STATEMENT"
            print a.lex
            print "=================================="
            return a.lex
            #return self._get_next_tok()

        if (self.curr_tok.type == "if"):
            self._get_next_tok()
            if_sub_idx+=1

            f.write("\n/* if statement */\n")

            count = 1
            self._if_statement(if_sub_idx)

            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "for"):
            self._get_next_tok()
            for_sub_idx+=1

            f.write("\n/* for loop statement */\n")

            count = 1
            self._for_loop(for_sub_idx)

            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "return"):
            try:
                if (self.prc_dec == 0):
                    raise ErrorToken("return", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was not expecting: '%s' outside of procedure, received: '%s' on line: %i" \
                                                   %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return

            count = 1
            self._get_next_tok()

            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "id" and self.prc_call):
            print "PROCEDURE CALL"
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            num_args = self._argument_list()
            try:
                if (self.curr_tok.lex != ")"):
                    raise ErrorToken(")", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                f.write("/* calling '%s' procedure */\n" %(symbol_table[self.proc_name]))
                f.write("R[%i] = M[FP+0]\n" %(i))
                self._get_next_tok()
                self._check_for_semicolon()

            try:
                if (num_args != symbol_table[self.proc_name].param_count):
                    raise ErrorToken(num_args, symbol_table[self.proc_name].param_count)
            except ErrorToken, e:
                e.print_error("was expecting '%s' arguments, received: '%s' arguments on line: %i" \
                                                                        %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return

            count = 1
            self.prc_call = 0
            return self._get_next_tok()
        else:
            return

    # <assignment_statement> ::=
    #           <destination> := <expression>

    # <destination> ::=
    #           <identifier> [ [ <expression> ] ]
    def _assignment(self):

        print "=================ASSIGNMENT===================="
        print "Variable %s is getting assigned" %(self.curr_tok.lex)
        print "value of prc call %i" %(self.prc_call)

        f.write("\n/* assigned statement */\n")
        try:
            if (self.curr_tok.lex not in symbol_table.keys()):
                raise ErrorToken(None, self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("variable: '%s' has not been delcared on line: %i" \
                                                            %(e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        try:
            #reg.append(symbol_table[self.curr_tok.lex])
            reg.insert(0, symbol_table[self.curr_tok.lex])
            #reg.append(symbol_table[self.curr_tok.lex])
            #print reg[0].data_type
            self._get_next_tok()
            if (self.curr_tok.lex != ":="):
                raise ErrorToken(":=", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
        else:
            self._get_next_tok()
            self._assign = 1
            count = 1

            try:
                if (self._expression() == -1):
                    raise ErrorToken("expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                return

    # <if_statement> ::=
    #                if ( <expression> ) then ( <statement> ; )+
    #                [ else ( <statement> ; )+ ]
    #                end if
    def _if_statement(self, if_sub_idx):

        # (
        try:
            if (self.curr_tok.lex != "("):
                raise ErrorToken("(", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            _if_error(1)

        # <expression>
        else:
            self._get_next_tok()
            if (self.curr_tok.lex not in symbol_table.keys()):
                symbol_table[self.curr_tok.lex] = self.curr_tok
                symbol_table[self.curr_tok.lex].data_type = self.curr_tok.type
                reg.insert(0, symbol_table[self.curr_tok.lex])

            try:
                if (self._expression() == -1):
                    raise ErrorToken("expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                self._expression()

        # )
        try:
            if (self.curr_tok.lex != ")"):
                raise ErrorToken(")", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            _if_error(2)
        else:
            self._get_next_tok()

        # then
        try:
            if (self.curr_tok.type != "then"):
                raise ErrorToken("then", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            _if_error(3)

        # <statement>
        else:
            print "getting statement"
            print self._get_next_tok().lex
            f.write("if (R[%i] == 0) goto if_subroutine_%i;\n" %(i, if_sub_idx))

            try:
                # make sure the we have at least 1 statement
                if (self._statement() == None and count == 0):
                    #raise ErrorToken("missing statement after 'then' in 'if' block", "", line_num)
                    raise ErrorToken("statement", "no statement")
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                _if_error(4)

            else:
                self._statement()

            if (self.curr_tok.type == "else"):
                f.write("goto if_subroutine_%i;\n" %(if_sub_idx+1))
                f.write("if_subroutine_%i:\n"      %(if_sub_idx))
                if_sub_idx+=1

                self._get_next_tok()

                try:
                    if (self._statement() == None and count == 0):
                        #raise ErrorToken("missing statement after 'then' in 'if' block", "", line_num)
                        raise ErrorToken("statement", "no statement")
                except ErrorToken, e:
                    e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                  %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    _if_error(5)
                else:
                    self._statement()

                f.write("if_subroutine_%i:\n" %(if_sub_idx))

            #else:
            #    f.write("subroutine_%i:\n" %(if_sub_idx))

            if (self.curr_tok.lex == "end"):
                print "end test"
                self._get_next_tok()
                try:
                    if (self.curr_tok.lex != "if"):
                        raise ErrorToken("if", self.curr_tok.lex)
                except ErrorToken, e:
                    e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                  %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    _if_error(6)
                else:
                    return self._get_next_tok()

    # <loop_statement> ::=
    #                 for ( <assignment_statement> ;
    #                      <expression> )
    #                       ( <statement> ; )*
    #                 end for
    def _for_loop(self, for_sub_idx):

        # (
        try:
            if (self.curr_tok.lex != "("):
                raise ErrorToken("(", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()

        # <assignment statement>
        try:
            self._statement()
            if (not(self._assign)):
                raise ErrorToken("assignment statement", None)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        # <expression>
        else:
            self._get_next_tok()
            self._expression()
            self._get_next_tok()
        # )
        try:
            if (self.next_tok_lex != ")"):
                raise ErrorToken(")", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            _skip_line()
            return
        else:
            self._get_next_tok()
        # <statement>
        try:
            if (self._statement() == None and count == 0):
                raise ErrorToken("statement", "no statement", line_num)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            _skip_line()
            return

        if (self.next_tok_lex == "end"):
            self._get_next_tok()
            try:
                if (self.next_tok_lex != "for"):
                    raise ErrorToken("for", self.next_tok_lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
                _skip_line()
                return
            else:
                return

    def _expression(self):
        i = 0
        print self.next_tok_typ
        print self.next_tok_lex
        while (self.next_tok_lex != ";"):
            #if ((self.next_tok_typ == "not") and (self.next_tok_typ not in reserved_ids)):
            self._get_next_tok()
            if (self.next_tok_typ == "not"):
                self._get_next_tok()
                r.append(~self._expression(self._get_next_tok())
                #yield ~self._expression()
                # could be "notting" itself or another
                # register before assigning to r[0], so
                # this needs to be handled differently
                f.write("R[%i] = not(R[%i])\n" %(i, i))
                print r[0]
                continue
            if (self.next_tok_typ == ")"):
                r.append(self._arith_op())
                return r[0]
            elif (self.next_tok_typ == "|"):
                self._get_next_tok()
                r.append(self._expression())
                r[0] = r[0] | r[1]
                f.write("R[%i] = R[%i] | R[%i])\n" %(i, i, i+1))
            elif (self.next_tok_typ == "&"):
                self._get_next_tok()
                r.append(self._expression())
                r[0] = r[0] & r[1]
                f.write("R[%i] = R[%i] & R[%i])\n" %(i, i, i+1))
            else:
                r[0] = r[r.__len__()-1]
                return r[0]

    def _arith_op(self):
        r.append(self._relation())
        if (self.next_tok_lex == "+"):
            r[0] = r[0] + r[1]
            f.write("R[%i] = R[%i] + R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == "-"):
            r[0] = r[0] - r[1]
            f.write("R[%i] = R[%i] - R[%i]\n" %(i, i+1))
        else:
            return r[0]

    def _relation(self):

        r.append(self._term())
        if (self.next_tok_lex == "!="):
            if (r[0] != r[1]):
                f.write("R[%i] != R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == "=="):
            if (r[0] == r[1]):
                f.write("R[%i] == R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == ">"):
            if (r[0] > r[1]):
                f.write("R[%i] > R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == "<="):
            if (r[0] <= r[1]):
                f.write("R[%i] <= R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == ">="):
            if (r[0] >= r[1]):
                f.write("R[%i] >= R[%i]\n" %(i, i+1))
        elif (self.next_tok_lex == "<"):
            if (r[0] < r[1]):
                f.write("R[%i] < R[%i]\n" %(i, i+1))
                return 1
            else:
                return 0
        else:
            return r[0]
        r.append(self._relation())

    def _term(self):
        i = 0
        r.append(self._factor())
        #while (r[0] != -1):
        while (self._factor() != -1):
            if (self.next_tok_typ != "integer" or self.next_tok_typ != "float"):
                self._get_next_tok()
                continue
            if (self.next_tok_typ == "divide"):
                self._get_next_tok()
                r.append(self._term())
                r[0] = r[0] / r[1]
                f.write("R[%i] = R[%i] / R[%i])\n" %(i, i, i+1))
            elif (self.next_tok_typ == "mult"):
                self._get_next_tok()
                r.append(self._term())
                r[0] = r[0] * r[1]
                f.write("R[%i] = R[%i] * R[%i])\n" %(i, i, i+1))
            else:
                return r[0]

    def _factor(self):
        if (self.next_tok_lex == "false"):
            return self.next_tok_typ
        elif (self.next_tok_lex == "true"):
            return self.next_tok_typ
        elif (self.next_tok_typ == "string"):
            return self.next_tok_lex
        elif (self.next_tok_typ == "integer" or self.next_tok_typ == "float"):
            return self.next_tok_lex
        elif (self.next_tok_typ == "id" and self.next_tok_lex not in reserved_ids):
            return self.next_tok_lex
        elif (self.next_tok_lex == "("):
            return self._expression()
        else:
            return -1

    def _array_size(self):

        try:
            if (self.next_tok_lex == "integer"):
                self._get_next_tok()
            else:
                raise ErrorToken("integer", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.next_tok_typ == "]"):
                self._get_next_tok()
            else:
                raise ErrorToken("]", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.next_tok_lex != ";"):
                raise ErrorToken(";", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        return

    def _variable_dec(self):
        print self.next_tok_typ
        print self.next_tok_lex
        try:
            # make sure token is not a reserved id
            if (self.next_tok_typ == "id" and self.next_tok_lex not in reserved_ids):
                self._get_next_tok()
            else:
                raise ErrorToken("identifier", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
            # check if we have declared an array
        try:
            if (self.next_tok_lex == "["):
                self._get_next_tok()
                self._array_size()
            elif (self.next_tok_lex == ";"):
                return self.next_tok_lex
            else:
                raise ErrorToken("[ or ;", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        return

    def _parameter_list(self):

        try:
            if (self.next_tok_typ == self._type_mark(self.next_tok_typ)):
                self._get_next_tok()
                self._declaration()
            else:
                raise ErrorToken("data type", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.var_dec and (self.next_tok_typ == "in" or self.next_tok_typ == "out")):
                self.var_dec = 0
                self._get_next_tok()
            else:
                raise ErrorToken("variable declaration in/out", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.next_tok_lex != ","):
                self._get_next_tok()
                self._declaration()
            elif (self.next_tok_lex == ")"):
                self._get_next_tok()
                self._procedure_body()
            else:
                raise ErrorToken(", or )", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return

        return

    def _procedure_header(self):
        try:
            if (self.next_tok_typ == "id" and self.next_tok_lex not in reserved_ids):
                self._get_next_tok()
            else:
                raise ErrorToken("identifier", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.next_tok_lex == "("):
                self._get_next_tok()
                if (self.next_tok_lex != ")"):
                    self._parameter_list()
                else:
                    return
            else:
                raise ErrorToken("(", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        return

    def _procedure_body(self):
        #_declaration
        self._program_body()

    def _declaration(self):

        try:
            # check for variable declaration
            if (self.next_tok_typ == self._type_mark(self.next_tok_typ)):
                self._get_next_tok()
                self._variable_dec()
                self.var_dec = 1
            # check for procedure declaration
            elif (self.next_tok_typ == "procedure"):
                self._get_next_tok()
                self._procedure_header()
                self.prc_dec = 1
            else:
                raise ErrorToken("variable/procedure declaration", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        return

    def _assignment(self):
        self._expression()
        self._get_next_tok()
        try:
            if (self.next_tok_lex != ";"):
                raise ErrorToken(";", self.next_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return

    def _program_body(self):

        try:
            if (self.next_tok_typ == "global"):
                print self.next_tok_typ
                self._get_next_tok()
                print self.next_tok_typ
                self._declaration()
            elif (self.next_tok_typ == "begin"):
                self._get_next_tok()
                _statement()
            else:
                raise ErrorToken("global/begin", self.next_tok_typ)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return

        while (self.next_tok_typ != "eof"): return _program_body()

    def _program_header(self):

        print self.curr_tok_typ
        try:
            if (self.curr_tok_typ != "program"):
                raise ErrorToken("program", self.curr_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        try:
            if (self.next_tok_typ != "id")):# and not(eof)):
                raise ErrorToken("id", self.curr_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        else:
            print self.next_tok_lex
            self._get_next_tok()
        try:
            if(self.next_tok_typ != "is"):
                raise ErrorToken("is", self.curr_tok_lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" %(e.exp_tok, e.rec_tok, self.line_num))
            self._skip_line()
            return
        else:
            print self.next_tok_typ
            self._get_next_tok()
            self._program_body()

        return

if (__name__ == "__main__"):
    if (check_src_file()):
        #f = open("good_test1.c")
        parse = parser(get_tokens())
        parse._program_header()
    #parse._get_next_tok()
