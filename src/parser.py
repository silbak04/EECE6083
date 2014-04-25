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
            print "BEFORE GOING TO EXPRESSION!!!!!!!!!!!!!!!!!!!!!!!!!"
            print self.curr_tok.lex
            print "BEFORE GOING TO EXPRESSION!!!!!!!!!!!!!!!!!!!!!!!!!"
            if (self.curr_tok.lex not in symbol_table.keys()):
                symbol_table[self.curr_tok.lex] = self.curr_tok
                symbol_table[self.curr_tok.lex].data_type = self.curr_tok.type
                #reg.append(symbol_table[self.curr_tok.lex])
                reg.insert(0, symbol_table[self.curr_tok.lex])

            f.write("if (R[%i] == 0) goto for_subroutine_%i:\n" %(i, for_sub_idx))
            try:
                if (self._expression() == -1):
                    raise ErrorToken("expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                self._expression()

        # )
        try:
            if (self.curr_tok.lex != ")"):
                raise ErrorToken(")", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()

        # <statement>
        try:
            if (self._statement() == None and count == 0):
                raise ErrorToken("statement", "no statement", line_num)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        # TODO: add try/except...
        if (self.curr_tok.lex == "end"):
            self._get_next_tok()
            try:
                if (self.curr_tok.lex != "for"):
                    raise ErrorToken("for", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                f.write("for_subroutine_%i:\n" %(for_sub_idx))
                return self._get_next_tok()

    # <procedure_call> ::=
    #            <identifier> ( [<argument_list>] )

    # <argument_list> ::=
    #            <expression>, <argument_list>
    #          | <expression>
    def _argument_list(self):
        num_of_args = 0
        while (self._get_next_tok() != ")"):
            num_of_args+=1
            self._expression()
            if (self.curr_tok.lex == ","): continue

        return num_of_args

    # <expression> ::= <expression> & <arithOp>
    #                | <expression> | <arithOp>
    #                | [ not ] <arithOp>
    def _expression(self):
        global i
        print "'%s, %s' on line: %d" %(self.curr_tok.type, self.curr_tok.lex, self.curr_tok.line)
        print "in exp"

        if (self.curr_tok.lex == "not"):
            self._get_next_tok()
            self.not_exp = 1;

        lhs = self._arith_op()
        if (self.not_exp):
            self.not_exp = 0
            i+=1
            f.write("R[%i] = ~R[%i];\n" %(i, lhs))
            lhs = i

        while (self.curr_tok.lex == "&" or self.curr_tok.lex == "|"):
            if (self.curr_tok.lex == "|"):
                i+=1
                self._get_next_tok()
                rhs = self._arith_op()
                i+=1

                lhs = i

            elif (self.curr_tok.lex == "&"):
                i+=1
                self._get_next_tok()
                rhs = self._arith_op()
                i+=1

                f.write("R[%i] = R[%i] & R[%i];\n" %(i, lhs, rhs))
                lhs = i

    # <arithOp> ::= <arithOp> + <relation>
    #             | <arithOp> - <relation>
    #             | <relation>
    def _arith_op(self):
        global i

        print "in arith"
        lhs = self._relation()

        while (self.curr_tok.lex == "+" or self.curr_tok.lex == "-"):
            if (self.curr_tok.lex == "+"):
                print "in arith: in plus before"

                i+=1
                self._get_next_tok()
                rhs = self._relation()
                i+=1

                print "in arith: in plus after"

                f.write("R[%i] = R[%i] + R[%i];\n" %(i, lhs, rhs))
                lhs = i

            if (self.curr_tok.lex == "-"):
                print "in arith: in minus before"

                i+=1
                self._get_next_tok()
                rhs = self._relation()
                i+=1

                print "in arith: in minus after"

                f.write("R[%i] = R[%i] - R[%i];\n" %(i, lhs, rhs))
                lhs = i

        return i

    # <relation> ::= <relation> < <term>
    #              | <relation> >= <term>
    #              | <relation> <= <term>
    #              | <relation> > <term>
    #              | <relation> == <term>
    #              | <relation> != <term>
    #              | <term>
    def _relation(self):
        global i

        print "in relation"
        lhs = self._term()

        while (self.curr_tok.lex in ["!=", "==", ">", "<=", ">=", "<"]):
            if (self.curr_tok.lex == "!="):
                print "in rel: in !="

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] != R[%i];\n" %(i, lhs, rhs))
                lhs = i

            elif (self.curr_tok.lex == "=="):
                print "in rel: in =="

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] == R[%i];\n" %(i, lhs, rhs))
                lhs = i

            elif (self.curr_tok.lex == ">"):
                print "in rel: in >"

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] > R[%i];\n" %(i, lhs, rhs))
                lhs = i

            elif (self.curr_tok.lex == "<="):
                print "in rel: in <="

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] <= R[%i];\n" %(i, lhs, rhs))
                lhs = i

            elif (self.curr_tok.lex == ">="):
                print "in rel: in >="

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] >= R[%i];\n" %(i, lhs, rhs))
                lhs = i

            elif (self.curr_tok.lex == "<"):
                print "in rel: in <"

                i+=1
                self._get_next_tok()
                rhs = self._term()
                i+=1

                f.write("R[%i] = R[%i] < R[%i];\n" %(i, lhs, rhs))
                lhs = i

        return i

    # <term> ::= <term> * <factor>
    #         |  <term> / <factor>
    #         |  <factor>
    def _term(self):
        global i

        print "in term"
        lhs = self._factor()

        while (self.curr_tok.lex == "/" or self.curr_tok.lex == "*"):
            if (self.curr_tok.lex == "*"):
                print "in term: in mult before"

                i+=1
                self._get_next_tok()
                rhs = self._factor()
                i+=1

                print "in term: in mult after"

                f.write("R[%i] = R[%i] * R[%i];\n" %(i, lhs, rhs))
                lhs = i

            if (self.curr_tok.lex == "/"):
                print "in term: in div before"

                i+=1
                self._get_next_tok()
                rhs = self._factor()
                i+=1

                print "in term: in div after"

                f.write("R[%i] = R[%i] / R[%i];\n" %(i, lhs, rhs))
                lhs = i

        return i

    # <factor> ::= ( <expression> )
    #            | [ - ] <name>
    #            | [ - ] <number>
    #            | <string>
    #            | true
    #            | false
    def _factor(self):
        global i

        if (self.curr_tok.lex == "("):
            print "=================GOING BACK IN EXP=================="
            print "in factor: before exp"
            self._get_next_tok()
            self._expression()
            print "in factor: after exp"
            print "=================RETURNED FROM EXP=================="
            try:
                if (self.curr_tok.lex != ")"):
                    raise ErrorToken(")", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                self._get_next_tok()
                return i

        # name
        if (self.curr_tok.type == "id" and self.curr_tok.lex not in reserved_ids):
            print "in factor: id"

            try:
                if (reg[0].value == None):
                    raise ErrorToken("variable initialization", "uninitialized variable")
            except ErrorToken, e:
                e.print_warning("was expecting '%s', received: '%s' on line: %i" \
                                                                  %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                symbol_table[self.curr_tok.lex].value = 0

            try:
                if (reg[0].data_type != symbol_table[self.curr_tok.lex].data_type):
                #if (reg[0].data_type != self.curr_tok.data_type):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.data_type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                #r.append(reg[0].value)
                r.insert(0, symbol_table[self.curr_tok.lex].value)
                print "===========================NAME=========================="
                #print "variable %s is being assigned value: %i" %(self.curr_tok.lex, int(r[0]))
                print self.curr_tok.lex
                #print   "R[%i] = M[%i]"    %(i, symbol_table[self.curr_tok.lex].address)
                print   "R[%i] = %i"        %(i, int(symbol_table[self.curr_tok.lex].value))
                f.write("R[%i] = M[FP+%i];\n" %(i+1, symbol_table[self.curr_tok.lex].address))
                i+=1
                #if (self.not_exp): self.not_exp = 0; f.write("R[%i] = ~R[%i];\n" %(i+1, i))
                print "===========================NAME=========================="
                print "RETURNING INDEX VALUE"
                print i
                print "RETURNING INDEX VALUE"
                self._get_next_tok()
                return i

        # number
        if (self.curr_tok.type == "integer" or self.curr_tok.type == "float"):
            print "in factor: integer"
            print "VALUE OF INDEX: %i" %(i)

            try:
                if (reg[0].data_type != self.curr_tok.type):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                return
            else:
                reg[0].value = self.curr_tok.lex
                #f.write("R[%i] = %i;\n" %(i, int(self.curr_tok.lex)))
                f.write("R[%i] = %d;\n" %(i, int(reg[0].value)))
                #i+=1
                self._get_next_tok()
                return i

        # negative name/number/expression
        if (self.curr_tok.type == "minus"):
            self._get_next_tok()
            try:
                if (self.curr_tok.type == "integer" or self.curr_tok.type == "float"):
                    print "in factor->minus: integer"
                    print self.curr_tok.lex
                    if (reg[0].lex == self.curr_tok.lex):
                        try:
                            if (reg[0].value == None):
                                raise ErrorToken("variable initialization", "uninitialized variable")
                        except ErrorToken, e:
                            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    try:
                        if (reg[0].data_type != self.curr_tok.type):
                            raise ErrorToken(reg[0].data_type, self.curr_tok.type)
                    except ErrorToken, e:
                        e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                             %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    else:
                        f.write("R[%i] = %i;\n"         %(i, int(self.curr_tok.lex)))
                        f.write("R[%i] = -1 * R[%i];\n" %(i+1, i))

                        i+=1
                        self._get_next_tok()
                        return i

                elif (self.curr_tok.type == "id" and self.curr_tok.lex not in reserved_ids):
                    print "in fact->minus: id"
                    if (reg[0].lex == self.curr_tok.lex):
                        try:
                            if (reg[0].value == None):
                                raise ErrorToken("variable initialization", "uninitialized variable")
                        except ErrorToken, e:
                            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    try:
                        if (reg[0].data_type != symbol_table[self.curr_tok.lex].data_type):
                        #if (reg[0].data_type != self.curr_tok.data_type):
                            raise ErrorToken(reg[0].data_type, self.curr_tok.data_type)
                    except ErrorToken, e:
                        e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                             %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    else:
                        print "===========================MINUS NAME=========================="
                        f.write("R[%i] = M[FP+%i];\n"   %(i, symbol_table[self.curr_tok.lex].address))
                        f.write("R[%i] = -1 * R[%i];\n" %(i+1, i))
                        print "===========================MINUS NAME=========================="

                        i+=1
                        self._get_next_tok()
                        return i

                elif (self.curr_tok.type == "("):
                    print "in factor->minus: exp"
                    print "=================GOING BACK IN EXP=================="
                    self._get_next_tok()
                    self._expression()
                    print "=================RETURNED FROM EXP=================="
                    try:
                        if (self.curr_tok.lex != ")"):
                            raise ErrorToken(")", self.curr_tok.lex)
                    except ErrorToken, e:
                        e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                      %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                        self._skip_line()
                        return
                    else:
                        self._get_next_tok()
                        return i
                else:
                    raise ErrorToken("integer/identifier/expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))

        # string
        if (self.curr_tok.type == "string"):
            print "in factor: string"
            try:
                if (reg[0].data_type != self.curr_tok.type):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                # TODO: needs to be handled properly...
                #f.write("R[%i] = %i;\n" %(i, int(r[i])))

                i+=1
                self._get_next_tok()
                return i

            '''
            try:
                if (reg[0].data_type != symbol_table[self.curr_tok.lex].data_type):
                    #if (reg[0].data_type != self.curr_tok.data_type):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.data_type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                r.append(reg[0].value)
                print   "R[%i] = M[FP+%i]"    %(i, symbol_table[self.curr_tok.lex].address)
                f.write("R[%i] = M[FP+%i];\n" %(i, symbol_table[self.curr_tok.lex].address))
                self._get_next_tok()
                return i
            '''

        # true
        if (self.curr_tok.lex == "true"):
            print "in factor: true"
            # convert true -> 1
            reg[0].value = 1
            try:
                if (reg[0].data_type == "float"):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.type)
                    #raise ErrorToken(reserved_ids[0:3], self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return

            if (reg[0].data_type == "integer"):
                reg[0].data_type = "bool"
                reg[0].lex = 0

            f.write("R[%i] = %i;\n" %(i, int(reg[0].value)))
            self._get_next_tok()
            return i

        # false
        if (self.curr_tok.lex == "false"):
            print "in factor: false"
            # convert false -> 0
            reg[0].value = 0
            try:
                if (reg[0].data_type == "float"):
                    raise ErrorToken(reg[0].data_type, self.curr_tok.type)
                    #raise ErrorToken(reserved_ids[0:3], self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return

            if (reg[0].data_type == "integer"):
                reg[0].data_type = "bool"
                reg[0].lex = 0

            f.write("R[%i] = %i;\n" %(i, int(reg[0].value)))
            self._get_next_tok()
            return i

        return -1

    # <type_mark> ::= integer
    #               | float
    #               | bool
    #               | string
    def _type_mark(self, data_type):
        self.data_type = data_type

        try:
            if (self.data_type not in data_types):
                raise ErrorToken(None, self.data_type)
        except ErrorToken, e:
            e.print_error("data type: '%s' is not supported on line: %i" \
                                                                      %(e.rec_tok, self.curr_tok.line))
        else:
            return self.data_type

    # <array_size> ::= <number>
    def _array_size(self):

        try:
            if (self.curr_tok.lex == "integer"):
                self._get_next_tok()
            else:
                raise ErrorToken("integer", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        try:
            if (self.curr_tok.type == "]"):
                self._get_next_tok()
            else:
                raise ErrorToken("]", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        try:
            if (self.curr_tok.lex != ";"):
                raise ErrorToken(";", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        return

    #<variable_declaration> ::=
    #                    <type_mark> <identifier>
    #                    [ [ <array_size> ] ]
    def _variable_dec(self):

        print "'%s, %s' on line: %d" %(self.curr_tok.type, self.curr_tok.lex, self.curr_tok.line)
        identifier = None
        try:
            # make sure token is not a reserved id
            if (self.curr_tok.type == "id" and self.curr_tok.lex not in reserved_ids):
                if (self.prc_var_dec):
                    identifier = self.curr_tok.lex
                    self._get_next_tok()
                    return identifier
                self._get_next_tok()
            else:
                raise ErrorToken("identifier", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

        try:
            # check if we have declared an array
            if (self.curr_tok.lex == "["):
                self._get_next_tok()
                self._array_size()
            elif (self.curr_tok.lex == ";"):
                print "'%s' on line: %d" %(self.curr_tok.lex, self.curr_tok.line)
                return self._get_next_tok()
            else:
                raise ErrorToken("'[' or ';'", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        return

    #<parameter_list> ::=
    #                  <parameter> , <parameter_list>
    #                | <parameter>

    #<parameter> ::= <variable_declaration> (in | out)
    def _parameter_list(self):

        print "PARAMETER LIST"
        print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
        data_type = None
        identifier = None
        num_parameters = 0

        while (self.curr_tok.lex != ")" and self.curr_tok.lex != "\n"):
            try:
                if (self.curr_tok.type != self._type_mark(self.curr_tok.type)):
                    raise ErrorToken("data type", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                data_type = self.data_type
                self.prc_var_dec = 1
                self._get_next_tok()
                identifier = self._variable_dec()

            try:
                if ((self.curr_tok.type != "in" and self.curr_tok.type != "out")):
                    raise ErrorToken("variable declaration in/out", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                num_parameters+=1
                symbol_table[self.proc_name].param_list.append((data_type, identifier, self.curr_tok.type))
                symbol_table[self.proc_name].param_count = num_parameters
                self._get_next_tok()

            if (self.curr_tok.lex == ","): self._get_next_tok()

        return

    # <procedure_header> :: =
    #                     procedure <identifier>
    #                     ( [<parameter_list>] )
    def _procedure_header(self):

        print "PROCEDURE HEADER"

        try:
            if (self.curr_tok.type != "id" or self.curr_tok.lex in reserved_ids):
                raise ErrorToken("non-reserved identifier", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)

        try:
            if (self.curr_tok.lex != "("):
                raise ErrorToken("(", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._parameter_list()
            try:
                if (self.curr_tok.lex != ")"):
                    raise ErrorToken(")", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                self.prc_var_dec = 0
                f.write("%s:\n" %(self.proc_name))

            print "leaving procedure header going to proc bod"
            self._get_next_tok()
            self._procedure_body()
            print "returned from proc body back in _procedure_header"

        return

    # <procedure_body> ::=
    #                  ( <declaration> ; )*
    #             begin
    #                  ( <statement> ; )*
    #             end procedure
    def _procedure_body(self):
        global i

        print "PROCEDURE BODY"
        print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
        while (self.prc_dec):
            if (self.curr_tok.type == "global"):
                # TODO: change this...variable inside procedure needs to be
                # local...
                symbol_table[self.proc_name].local = 0
                self._get_next_tok()
                print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
                self._declaration()
            elif (self.curr_tok.type == "begin"):
                self._get_next_tok()
                print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)

                #while (self._statement() in ["id","if","else","for","return"]):
                while (self._statement() != "None"):
                    if (self.curr_tok.type == "end"): break

                    if (self.curr_tok.lex in symbol_table.keys()):
                        if (symbol_table[self.curr_tok.lex].procedure):
                            self.prc_call = 1
                    continue
                print self.curr_tok.type

            else:
                # TODO: INCASE YOU FORGET WE SHOULD PROBABLY BE KEEPING
                # TRACK OF PROGRAM NAME AND ADD A SYMBOL TABLE FOR PROGRAM
                # NAME AND ALL ATTRIBUTES ASSOCIATED WITH IT
                if (self.curr_tok.lex == "end"): break
                # TODO: change this...variable inside procedure needs to be
                # local...
                symbol_table[self.proc_name].local = 1
                self._declaration()
                print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)

        try:
            if (self.curr_tok.lex != "end"):
                raise ErrorToken("end", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            return
        else:
            self.prc_dec = 0
            self._get_next_tok()

        try:
            print "AFTER EMPTRY STATEMENTS PROCEDURE=============="
            if (self.curr_tok.type != "procedure"):
                raise ErrorToken("procedure", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            return

        try:
            self._get_next_tok()
            print "AFTER EMPTRY STATEMENTS PROCEDURE=============="
            if (self.curr_tok.lex != ";"):
                raise ErrorToken(";", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            return
        else:
            self._get_next_tok()
            f.write("R[%i] = M[FP-2];\n" %(i))
            f.write( "FP = M[FP-1];\
                    \nSP = SP-1;\
                    \nSP = SP-%i;\n" %(symbol_table[self.proc_name].param_count))
            f.write("goto (*void*)R[%i]\n" %(i))
            i+=1
            return
        return

    # <declaration> ::=
    #        [ global ] <procedure_declaration>
    # |      [ global ] <variable_declaration>
    def _declaration(self):

        print "DECLARATION"
        try:
            # check for procedure declaration
            if (self.curr_tok.type == "procedure"):
                # create local symbol table
                # after proc is done, destroy local sym table
                self._get_next_tok()

                self.proc_name = self.curr_tok.lex
                print "=="*40
                print "'%s' on line: %d" %(self.proc_name, self.curr_tok.line)
                print "=="*40

                symbol_table[self.proc_name] = self.curr_tok
                symbol_table[self.proc_name].procedure = 1

                print "'%s' on line: %d" %(self.curr_tok.lex, self.curr_tok.line)

                self.prc_dec = 1
                self._procedure_header()

            # check for variable declaration
            elif (self.curr_tok.type == self._type_mark(self.curr_tok.type)):
                self._get_next_tok()

                # make sure we are not declaring the same variable more than
                # once
                try:
                    if (self.curr_tok.lex in symbol_table.keys()):
                        raise ErrorToken(None, self.curr_tok.lex)
                except ErrorToken, e:
                    e.print_error("variable: '%s' has already been delcared on line: %i" \
                                                                  %(e.rec_tok, self.curr_tok.line))
                else:
                    # fp
                    self.curr_tok.address = self.mem_addr
                    self.mem_addr+=1

                    # add the current token in the symbol table and assign the
                    # data type with the current token
                    symbol_table[self.curr_tok.lex] = self.curr_tok
                    symbol_table[self.curr_tok.lex].data_type = self.data_type

                    if (self.local):
                        symbol_table[self.curr_tok.lex].local = 0
                    else:
                        self.local = 0
                        symbol_table[self.curr_tok.lex].local = 1

                    print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
                    self._variable_dec()
                    print "'%s, %s' on line: %d" %(self.curr_tok.type, self.curr_tok.lex, self.curr_tok.line)
                    #self.var_dec = 1

            else:
                raise ErrorToken("variable/procedure declaration", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        return self.curr_tok

    # <program_body> ::=
    #                ( <declaration> ; )*
    #            begin
    #                ( <statement> ; )*
    #            end program
    def _program_body(self):

        print "PROGRAM BODY"
        print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
        if (self.curr_tok.type == "global"):
            self.local = 0
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._declaration()

        elif (self.curr_tok.type == "begin"):
            self._get_next_tok()
            f.write("\nmain:\n")
            while (self._statement() != "None"):
                if (self.curr_tok.type == "end"): break

                # check to see if current statement is a procedure call
                if (self.curr_tok.lex in symbol_table.keys()):
                    if (symbol_table[self.curr_tok.lex].procedure):
                        self.prc_call = 1

                if (self.prc_call):
                    f.write("SP = SP + %d;\n" %(symbol_table[self.proc_name].param_count))

                continue
            return

        else:
            self.local = 1
            self._declaration()

        if (self.curr_tok.type != "eof"): return self._program_body()
        #while (self.prog_body): return self._program_body()

    # <program_header> ::=
    #                    program <identifier> is
    def _program_header(self):

        print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
        try:
            if (self.curr_tok.type != "program"):
                raise ErrorToken("program", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.lex, self.curr_tok.line)

        try:
            if (self.curr_tok.type != "id"):# and not(eof)):
                raise ErrorToken("id", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.lex, self.curr_tok.line)

        try:
            if (self.curr_tok.type != "is"):
                raise ErrorToken("is", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._program_body()
            self.prog_body = 1

        # once we have returned from the program body, we need to
        # check to make sure the user has 'ended' the program correctly
        try:
            if (self.curr_tok.lex != "end"):
                raise ErrorToken("end", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
        try:
            self._get_next_tok()
            if (self.curr_tok.type != "program"):
                raise ErrorToken("program", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            return

        return

if (__name__ == "__main__"):
    if (check_src_file()):
        # TODO: if scanner/parser generates error, we do not want to generate
        # any code, so i need to terminate properly and make sure no code is
        # generate if error
        f = open("gen.c", "w")
        f.write("#include \"../runtime/runtime.h\"\n")
        f.write("int main(void)\n")
        f.write("{\n")
        f.write("goto main;\n")
        f.write(open("../runtime/runtime_inline.c").read())
        f.write('\n')

        parse = parser(get_tokens())
        parse._program_header()

        f.write("return 0;\n")
        f.write("}\n")
