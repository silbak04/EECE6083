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
indent = '    '

i = 1
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
        self.proc_dec = False
        self.proc_call = False
        self.proc_args = False
        self.sp_offset = 0
        self._predefined_proc = None
        self.string_proc = 0
        self.global_vars = 0

        self._assign = False
        self._if     = False
        self._for    = False
        self._return = False

        self.not_exp = False
        self.var = None

        #self.mem_addr = 0
        self.mem_addr = [0]
        self.local = False
        self.proc_name = None
        self.prc_var_dec = False
        self.prog_body = False
        self.label_idx = 0

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
        print "CHECK FOR SEMICOLON"
        print self.curr_tok.lex
        try:
            if (self.curr_tok.lex != ";"):
                raise ErrorToken(";", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return

    def _built_in_procedure(self):

        if self.curr_tok.lex in ['putinteger', 'putbool', 'putstring', 'putfloat']:
            if self.curr_tok.lex == "putstring": self.string_proc = 1

            if self.curr_tok.lex not in symbol_table.keys():
                symbol_table[self.curr_tok.lex] = token_symbol()
                symbol_table[self.curr_tok.lex].type = 'procedure'
                symbol_table[self.curr_tok.lex].lex  = 'procedure'
                symbol_table[self.curr_tok.lex].param_list.append([self.curr_tok.lex[3:], '', 'in'])

            self.proc_call = 1
            self._predefined_proc = 1
            self.proc_name = self.curr_tok.lex

        if self.curr_tok.lex in ['getinteger', 'getbool', 'getstring', 'getfloat']:
            if self.curr_tok.lex not in symbol_table.keys():
                symbol_table[self.curr_tok.lex] = token_symbol()
                symbol_table[self.curr_tok.lex].type = 'procedure'
                symbol_table[self.curr_tok.lex].lex  = 'procedure'
                symbol_table[self.curr_tok.lex].param_list.append([self.curr_tok.lex[3:], '', 'out'])

            self.proc_call = 1
            self._predefined_proc = 1
            self.proc_name = self.curr_tok.lex

        return

    def _check_for_proc_call(self):

        if (self.curr_tok.lex in symbol_table.keys()):
            if (symbol_table[self.curr_tok.lex].procedure):
                self.proc_call = 1

        return self.proc_call

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

    '''
    def _check_global(self):
        if symbol_table[
    '''

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

        #self.var = self.curr_tok.lex
        self.var = self.curr_tok
        print "STATEMENTTTTTTTTTTTTTTTTTTTTTTTTTTTT"
        print self.var.lex
        print "STATEMENTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

        # check for assignment
        if (not(self.proc_call) and (self.curr_tok.type == "id") and
           (self.curr_tok.lex not in reserved_ids)):
            self._assignment()

            # assignment is done, assign register to memory location
            if (self.proc_dec):
                #i+=1
                # f.write(indent+"R[%d] = M[FP+%d];\n" %(i, symbol_table[reg[0].lex].address+self.mem_addr))
                #f.write(indent+"R[%d] = M[FP+%d];\n" %(i, symbol_table[self.var.lex].address+self.mem_addr))
                #f.write(indent+"R[%d] = M[FP+%d];\n" %(i, self.mem_addr[-1]))
                f.write(indent+"R[%d] = M[FP+%d];\n" %(i, symbol_table[self.var.lex].address))

                ''''
                if symbol_table[reg[0].lex].local:
                    f.write(indent+"R[%d] = M[FP+%d];\n" %(i, symbol_table[reg[0].lex].address+self.mem_addr))
                else:
                    f.write(indent+"R[%d] = M[%d];\n" %(i, symbol_table[reg[0].lex].address+self.mem_addr))
                '''

                f.write(indent+"M[R[%d]] = R[%d];\n" %(i, i-1))
                i+=1
            else:
                #f.write(indent+"M[FP+%i] = R[%i];\n" %(symbol_table[reg[0].lex].address, i-1))
                f.write(indent+"M[FP+%i] = R[%i];\n" %(symbol_table[self.var.lex].address, i-1))
                i+=1
                '''
                if symbol_table[reg[0].lex].local:
                    f.write(indent+"M[FP+%i] = R[%i];\n" %(symbol_table[reg[0].lex].address, i-1))
                else:
                    f.write(indent+"M[%i] = R[%i];\n" %(symbol_table[reg[0].lex].address, i-1))
                '''

            #reg[0].value = int(r[0])
            print "CHECK FOR SEMI IN ASSIGNMENT"
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

            f.write("\n"+indent+"/* if statement */\n")

            count = 1
            self._if_statement(if_sub_idx)

            print "CHECK FOR SEMI IN IF"
            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "for"):
            self._get_next_tok()
            for_sub_idx+=1

            f.write("\n"+indent+"/* for loop statement */\n")

            count = 1
            self._for_loop(for_sub_idx)

            print "CHECK FOR SEMI IN FOR"
            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "return"):
            try:
                if (self.proc_dec == 0):
                    raise ErrorToken("return", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was not expecting: '%s' outside of procedure, received: '%s' on line: %i" \
                                                   %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return

            count = 1
            self._get_next_tok()

            print "CHECK FOR SEMI IN RETURN"
            self._check_for_semicolon()
            return self._get_next_tok()

        if (self.curr_tok.type == "id" and self.proc_call):
            print "PROCEDURE CALL"
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            f.write(indent+"/* calling '%s' procedure */\n" %(self.proc_name))

            arg, num_args = self._argument_list()
            print "NUMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
            print num_args
            print "NUMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
            self.sp_offset = arg - num_args

            print "NUMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
            print self.sp_offset
            print "NUMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"

            try:
                if (self.curr_tok.lex != ")"):
                    raise ErrorToken(")", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                self.proc_args = False
                self._get_next_tok()
                print "CHECK FOR SEMI IN PROC CALL"
                self._check_for_semicolon()

            try:
                if (num_args != symbol_table[self.proc_name].param_count):
                    raise ErrorToken(num_args, symbol_table[self.proc_name].param_count)
            except ErrorToken, e:
                e.print_error("was expecting '%s' argument(s), received: '%s' argument(s) on line: %i" \
                                                                        %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            else:
                #i+=1
                self.label_idx += 1
                f.write(indent+"R[%s] = (int)&&return_from_%s_%i;\n" %(i, self.proc_name, self.label_idx))
                f.write(indent+"M[SP] = R[%s];\n" %(i))
                f.write(indent+"SP++;\n")
                i+=1

                #if symbol_table[self.curr_tok.lex].local:
                f.write(indent+"R[%s] = FP;\n" %(i))
                #else:
                    #f.write(indent+"R[%s] = FP;\n" %(i))

                f.write(indent+"M[SP] = R[%s];\n" %(i))
                f.write(indent+"SP++;\n")
                f.write(indent+"FP = SP;\n")
                while self.sp_offset < arg:
                    f.write(indent+"M[SP] = R[%s];\n" %(self.sp_offset))
                    f.write(indent+"SP++;\n")
                    self.sp_offset+=1

                self.sp_offset = 0
                f.write(indent+"goto %s;\n"    %(self.proc_name))
                f.write("return_from_%s_%i:\n" %(self.proc_name, self.label_idx))

            count = 1
            self.proc_call = 0
            self.string_proc = 0
            self._predefined_proc = None
            i+=1
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
        print "value of prc call %i" %(self.proc_call)

        f.write("\n"+indent+"/* assigned statement */\n")
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
                self._assign = 0

        return

    # <if_statement> ::=
    #                if ( <expression> ) then ( <statement> ; )+
    #                [ else ( <statement> ; )+ ]
    #                end if
    def _if_statement(self, if_sub_idx):

        print "INNNNNNNNNN IF"

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
            # TODO: might need to change the way i'm doing this
            # if(x) <--- we want to save 'x'
            self.var = self.curr_tok
            if (self.curr_tok.lex not in symbol_table.keys()):
                #symbol_table[self.curr_tok.lex] = token_symbol()
                symbol_table[self.curr_tok.lex] = self.curr_tok
                symbol_table[self.curr_tok.lex].data_type = self.curr_tok.type
                reg.insert(0, symbol_table[self.curr_tok.lex])

            try:
                if (self._expression() == -1):
                    raise ErrorToken("expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            #else:
            #    self._expression()

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
            f.write(indent+"if (R[%i] == 0) goto if_subroutine_%i;\n" %(i-1, if_sub_idx))

            #while (self._statement() == None and count):
            while self._statement() not in ["else", "end", "None"]:
                continue

            '''
            try:
                # TODO: might need to change the way i'm doing this
                #self.var = self.curr_tok
                #print self.var.lex

                # check for built in procedure/procedure call
                self._built_in_procedure()
                self._check_for_proc_call()

                # make sure the we have at least 1 statement
                if (self._statement() == None and count == 0):
                    #raise ErrorToken("missing statement after 'then' in 'if' block", "", line_num)
                    raise ErrorToken("statement", "no statement")
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                _if_error(4)

            #else:
            #    self._statement()
            '''

            if (self.curr_tok.type == "else"):
                f.write(indent+"goto if_subroutine_%i;\n" %(if_sub_idx+1))
                f.write("if_subroutine_%i:\n"             %(if_sub_idx))
                if_sub_idx+=1

                self._get_next_tok()
                self._built_in_procedure()
                self._check_for_proc_call()

                while self._statement() not in ["else", "end", "None"]:
                    #if (self.curr_tok.type == "end"): break
                    continue

                '''
                try:
                    if (self._statement() == None and count == 0):
                        #raise ErrorToken("missing statement after 'then' in 'if' block", "", line_num)
                        raise ErrorToken("statement", "no statement")
                except ErrorToken, e:
                    e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                                  %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                    _if_error(5)
                #else:
                #    self._statement()
                '''

                f.write("if_subroutine_%i:\n" % if_sub_idx)

            #else:
            #    f.write(indent+"subroutine_%i:\n" %(if_sub_idx))

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

            f.write(indent+"if (R[%i] == 0) goto for_subroutine_%i:\n" %(i, for_sub_idx))
            try:
                if (self._expression() == -1):
                    raise ErrorToken("expression", self.curr_tok.lex)
            except ErrorToken, e:
                e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                              %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                self._skip_line()
                return
            #else:
            #    self._expression()

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
        self._built_in_procedure()
        self._check_for_proc_call()

        while self._statement() not in ["else", "None"]:
            continue

        '''
        try:

            self._built_in_procedure()
            self._check_for_proc_call()

            if (self._statement() == None and count == 0):
                raise ErrorToken("statement", "no statement", line_num)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        '''

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
                f.write(indent+"for_subroutine_%i:\n" %(for_sub_idx))
                return self._get_next_tok()

    # <procedure_call> ::=
    #            <identifier> ( [<argument_list>] )

    # <argument_list> ::=
    #            <expression>, <argument_list>
    #          | <expression>
    def _argument_list(self):
        num_of_args = 0
        self._get_next_tok()
        while self.curr_tok.lex != ")":

            num_of_args+=1
            self.proc_args = True

            #exp = self.curr_tok.lex
            # TODO: remove this local variable
            exp = self.curr_tok
            self.var.lex = exp.lex
            print "EXPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
            print self.var.lex
            print exp.lex
            print exp.type
            #print symbol_table[exp.lex].data_type
            print "EXPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"

            f.write("//IN BEG"+exp.lex+"\n")
            # check to see if procedure call is one we have predefined for runtime
            if self._predefined_proc and self.string_proc:
                if self.curr_tok.lex not in symbol_table.keys():
                    self.var.lex = exp.lex
                    symbol_table[exp.lex] = token_symbol()
                    symbol_table[exp.lex].data_type = exp.type

                    symbol_table[exp.lex].address = self.mem_addr[-1]
                    self.mem_addr[-1] += 1

                    f.write(indent+"//STRING PROC\n")
                    #symbol_table[self.proc_name].param_list[0][1] = self.curr_tok.lex
                    symbol_table[self.proc_name].param_list[0][1] = exp.lex
                    symbol_table[self.proc_name].param_count = num_of_args

            arg = self._expression()

            if self._predefined_proc and not self.string_proc:
                if self.curr_tok.lex not in symbol_table.keys():
                    f.write("//"+indent+exp.lex+"\n")
                    symbol_table[self.proc_name].param_list[0][1] = exp.lex
                    symbol_table[self.proc_name].param_count = num_of_args

            # check to see if argument is in/out and local/global
            if self._predefined_proc and symbol_table[self.proc_name].param_list[num_of_args-1][2] == "in" and symbol_table[exp.lex].local:
                f.write("//innnnn"+indent+self.proc_name+"\n")
                f.write("//"+indent+exp.lex+"\n")
                print "CHECKINGGGGGGGGGGGGGGGGGGGGGGGGG"
                print exp.type
                print "CHECKINGGGGGGGGGGGGGGGGGGGGGGGGG"
                f.write(indent+"R[%s] = M[FP+%s];\n" %(arg-1, symbol_table[exp.lex].address))
                '''
                if symbol_table[self.curr_tok.lex].local:
                    f.write(indent+"R[%s] = M[FP+%s];\n" %(arg-1, symbol_table[exp.lex].address))
                else:
                    f.write(indent+"R[%s] = M[%s];\n" %(symbol_table[exp.lex].address))
                '''

            if symbol_table[self.proc_name].param_list[num_of_args-1][2] == "out" and symbol_table[exp.lex].local:
                f.write("//outtttt"+indent+self.proc_name+"\n")
                f.write("//"+indent+exp.lex+"\n")
                f.write(indent+"R[%s] = FP+%s;\n" %(arg-1, symbol_table[exp.lex].address))
                '''
                if symbol_table[self.curr_tok.lex].local:
                    f.write(indent+"R[%s] = FP+%s;\n" %(arg-1, symbol_table[exp.lex].address))
                else:
                    f.write(indent+"R[%s] = %s;\n" % symbol_table[exp.lex].address)
                '''

            if symbol_table[exp.lex].local == 0:
                f.write("//none"+indent+self.proc_name+"\n")
                f.write("")
                f.write("//"+indent+exp.lex+"\n")
                f.write(indent+"R[%s] = %s;\n" %(arg-1, symbol_table[exp.lex].address))

            if self.curr_tok.lex == ",": self._get_next_tok(); continue

        #symbol_table[self.proc_name].param_count = num_of_args
        return arg, num_of_args

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
            f.write(indent+"R[%i] = ~R[%i];\n" %(lhs, lhs-1))
            i+=1
            lhs = i

        while (self.curr_tok.lex == "&" or self.curr_tok.lex == "|"):
            if (self.curr_tok.lex == "|"):
                self._get_next_tok()
                rhs = self._arith_op()

                f.write(indent+"R[%i] = R[%i] | R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == "&"):
                self._get_next_tok()
                rhs = self._arith_op()

                f.write(indent+"R[%i] = R[%i] & R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

        return i

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

                self._get_next_tok()
                rhs = self._relation()

                print "in arith: in plus after"

                f.write(indent+"R[%i] = R[%i] + R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            if (self.curr_tok.lex == "-"):
                print "in arith: in minus before"

                self._get_next_tok()
                rhs = self._relation()

                print "in arith: in minus after"

                f.write(indent+"R[%i] = R[%i] - R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
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

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] != R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == "=="):
                print "in rel: in =="

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] == R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == ">"):
                print "in rel: in >"

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] > R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == "<="):
                print "in rel: in <="

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] <= R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == ">="):
                print "in rel: in >="

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] >= R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            elif (self.curr_tok.lex == "<"):
                print "in rel: in <"

                self._get_next_tok()
                rhs = self._term()

                f.write(indent+"R[%i] = R[%i] < R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
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

                self._get_next_tok()
                rhs = self._factor()

                print "in term: in mult after"

                f.write(indent+"R[%i] = R[%i] * R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
                lhs = i

            if (self.curr_tok.lex == "/"):
                print "in term: in div before"

                self._get_next_tok()
                rhs = self._factor()

                print "in term: in div after"

                f.write(indent+"R[%i] = R[%i] / R[%i];\n" %(i, lhs-1, rhs-1))
                i+=1
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
                if not self._assign:
                    raise ErrorToken("variable initialization", "uninitialized variable")
            except ErrorToken, e:
                e.print_warning("was expecting '%s', received: '%s' on line: %i" \
                                                                      %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                #symbol_table[self.curr_tok.lex].value = 0

            try:
                print symbol_table[self.var.lex].data_type
                if self._assign:
                    #if (reg[0].data_type != symbol_table[self.curr_tok.lex].data_type):
                    #if (reg[0].data_type != self.curr_tok.data_type):
                    if (symbol_table[self.var.lex].data_type != symbol_table[self.curr_tok.lex].data_type):
                        #raise ErrorToken(reg[0].data_type, self.curr_tok.data_type)
                        raise ErrorToken(symbol_table[self.var.lex].data_type, symbol_table[self.curr_tok.lex].data_type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                         %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                #r.append(reg[0].value)
                #r.insert(0, symbol_table[self.curr_tok.lex].value)
                print "===========================NAME=========================="
                #print "variable %s is being assigned value: %i" %(self.curr_tok.lex, int(r[0]))
                print self.curr_tok.lex
                #print   "R[%i] = M[%i]"    %(i, symbol_table[self.curr_tok.lex].address)
                print   "R[%i] = %s"        %(i, symbol_table[self.curr_tok.lex].value)
                #if not self.proc_args:
                f.write("//comment"+"\n")
                f.write(indent+"R[%i] = M[FP+%i];\n" %(i, symbol_table[self.curr_tok.lex].address))

                '''
                if symbol_table[self.curr_tok.lex].local:
                    f.write(indent+"R[%i] = M[FP+%i];\n" %(i, symbol_table[self.curr_tok.lex].address))
                else:
                    f.write(indent+"R[%i] = M[%i];\n" % symbol_table[self.curr_tok.lex].address)
                '''

                i+=1
                #if (self.not_exp): self.not_exp = 0; f.write(indent+"R[%i] = ~R[%i];\n" %(i+1, i))
                print "===========================NAME=========================="
                print "RETURNING INDEX VALUE"
                print i
                print "RETURNING INDEX VALUE"
                print self._get_next_tok().lex
                return i

        # number
        if (self.curr_tok.type == "integer" or self.curr_tok.type == "float"):
            print "in factor: integer"
            print "VALUE OF INDEX: %i" %(i)

            try:
                #if (reg[0].data_type != self.curr_tok.type):
                #print symbol_table[self.var.lex].data_type
                #print self.exp.lex
                print symbol_table[self.var.lex].data_type
                #if (self.var.data_type != self.curr_tok.type):
                if (symbol_table[self.var.lex].data_type != self.curr_tok.type):
                    #raise ErrorToken(reg[0].data_type, self.curr_tok.type)
                    raise ErrorToken(symbol_table[self.var.lex].data_type, self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
                return
            else:
                #reg[0].value = self.curr_tok.lex
                if self.curr_tok.type == "float":
                    #f.write(indent+"tmp_float = %s;\n" % reg[0].value)
                    f.write(indent+"tmp_float = %s;\n" % self.curr_tok.lex)
                    f.write(indent+"memcpy(&R[%s], &tmp_float, sizeof(float));\n" % i)
                else:
                    #f.write(indent+"R[%i] = %s;\n" % (i, reg[0].value))
                    f.write(indent+"R[%i] = %s;\n" % (i, self.curr_tok.lex))
                i+=1
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
                        f.write(indent+"R[%i] = %i;\n"         %(i, int(self.curr_tok.lex)))
                        i+=1
                        f.write(indent+"R[%i] = -1 * R[%i];\n" %(i, i-1))
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
                        f.write(indent+"R[%i] = M[FP+%i];\n"   %(i, symbol_table[self.curr_tok.lex].address))
                        '''
                        if symbol_table[self.curr_tok.lex].local:
                            f.write(indent+"R[%i] = M[FP+%i];\n"   %(i, symbol_table[self.curr_tok.lex].address))
                        else:
                            f.write(indent+"R[%i] = M[%i];\n"   % symbol_table[self.curr_tok.lex].address)
                        '''

                        i+=1
                        f.write(indent+"R[%i] = -1 * R[%i];\n" %(i, i-1))
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
            size = 100
            symbol_table[self.var.lex].size = size
            print "in factor: string"
            print symbol_table[self.var.lex].data_type

            try:
                if (symbol_table[self.var.lex].data_type != self.curr_tok.type):
                    raise ErrorToken(symbol_table[self.var.lex].data_type, self.curr_tok.type)
            except ErrorToken, e:
                e.print_error("mismatched data types: was expecting '%s', received: '%s' on line: %i" \
                                                                     %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            else:
                for t,c in enumerate(self.curr_tok.lex):
                    f.write(indent+"tmp_string[%s] = '%s';\n" % (t,c))

                f.write("//"+str(symbol_table[self.var.lex].address)+"\n")
                f.write("//"+str(self.mem_addr)+"\n")
                f.write(indent+"tmp_string[%s] = '\\0';\n" % (t+1))
                #f.write(indent+"memcpy(&M[FP+%s], tmp_string, MAX_STR_LEN);\n" % (symbol_table[self.var].address+self.mem_addr))
                f.write(indent+"memcpy(&M[FP+%s], tmp_string, MAX_STR_LEN);\n" % self.mem_addr[-1])
                #f.write(indent+"memcpy(&M[FP+%s], tmp_string, MAX_STR_LEN);\n" % symbol_table[self.var].address+size)
                f.write(indent+"SP = SP + %d;\n"    % symbol_table[self.var.lex].size)
                #f.write(indent+"R[%i] = FP + %s;\n" % (i, symbol_table[self.var].address+self.mem_addr))
                f.write(indent+"R[%i] = FP + %s;\n" % (i, self.mem_addr[-1]))
                symbol_table[self.var.lex].address = self.mem_addr[-1]
                self.mem_addr[-1] += symbol_table[self.var.lex].size
                #self.mem_addr[-1] += symbol_table[self.var.lex].address + symbol_table[self.var.lex].size
                #self.mem_addr += symbol_table[self.var].address + symbol_table[self.var].size
                f.write("//"+indent+"SIZEEEEEEEEEEEEEEEEEEEEEE"+str(self.mem_addr)+"\n")

                i+=1
                self._get_next_tok()
                return i

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

            f.write(indent+"R[%i] = %i;\n" %(i, int(reg[0].value)))
            i+=1
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

            f.write(indent+"R[%i] = %i;\n" %(i, int(reg[0].value)))
            i+=1
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
            if (self.curr_tok.lex != "integer"):
                raise ErrorToken("integer", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()

        try:
            if (self.curr_tok.type != "]"):
                raise ErrorToken("]", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        else:
            self._get_next_tok()

        self._check_for_semicolon()
        '''
        try:
            if (self.curr_tok.lex != ";"):
                raise ErrorToken(";", self.curr_tok.lex)
        except ErrorToken, e:
            e.print_error("was expecting '%s', received: '%s' on line: %i" \
                                                          %(e.exp_tok, e.rec_tok, self.curr_tok.line))
            self._skip_line()
            return
        return
        '''

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
    #                    <parameter> , <parameter_list>
    #                  | <parameter>

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
                symbol_table[self.proc_name].param_list.append([data_type, identifier, self.curr_tok.type])
                symbol_table[self.proc_name].param_count = num_parameters
                print "PLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
                print "ADDING TOKEN: %s to symbol table" % identifier
                print "TOKEN has data type: %s" % data_type
                symbol_table[identifier] = token_symbol()
                symbol_table[identifier].address = self.mem_addr[-1]
                print "TOKEN has mem addr: %s" % symbol_table[identifier].address
                print "PLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
                symbol_table[identifier].data_type = data_type
                symbol_table[identifier].local = 1

                self.mem_addr[-1] += 1
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
            self.mem_addr.append(0)
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
        while (self.proc_dec):
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
                f.write(indent+"SP = SP + 1;\n")

                # set up/check for built in procedures
                self._built_in_procedure()

                #while (self._statement() in ["id","if","else","for","return"]):
                while (self._statement() != "None"):
                    if (self.curr_tok.type == "end"): break

                    # set up/check for built in procedures
                    self._built_in_procedure()
                    self._check_for_proc_call()

                    '''
                    if (self.curr_tok.lex in symbol_table.keys()):
                        if (symbol_table[self.curr_tok.lex].procedure):
                            self.proc_call = 1
                    '''

                    continue

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
            self.proc_dec = 0
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
            f.write(indent+"R[%i] = M[FP-2];\n" %(i))
            f.write(indent+"FP = M[FP-1];\n")
            f.write(indent+"SP = SP-1;\n")
            f.write(indent+"SP = SP-%i;\n" %(symbol_table[self.proc_name].param_count))
            f.write(indent+"SP = SP-2;\n")
            f.write(indent+"goto *(void*)R[%i];\n" %(i))
            self.mem_addr.pop()
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

                self.proc_dec = 1
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
                    #self.curr_tok.address = self.mem_addr

                    # add the current token in the symbol table and assign the
                    # data type with the current token
                    symbol_table[self.curr_tok.lex] = self.curr_tok
                    symbol_table[self.curr_tok.lex].data_type = self.data_type
                    #symbol_table[self.curr_tok.lex].address = self.curr_tok.address
                    print "DEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
                    print "ADDING TOKEN: %s to symbol table" % self.curr_tok.lex
                    print "TOKEN has data type: %s" % self.data_type
                    symbol_table[self.curr_tok.lex].address = self.mem_addr[-1]
                    self.mem_addr[-1] += 1
                    print "TOKEN has mem addre locat at: %s" % symbol_table[self.curr_tok.lex].address
                    print "DEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"

                    if (self.local):
                        symbol_table[self.curr_tok.lex].local = 1
                    else:
                        self.local = 0
                        symbol_table[self.curr_tok.lex].local = 0

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
        global i

        print "PROGRAM BODY"
        print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
        if (self.curr_tok.type == "global"):
            self.local = 0
            self.global_vars += 1
            self._get_next_tok()
            print "'%s' on line: %d" %(self.curr_tok.type, self.curr_tok.line)
            self._declaration()

        elif (self.curr_tok.type == "begin"):
            self._get_next_tok()
            f.write("\nmain:\n")
            f.write(indent+"FP = 0;\n")
            #f.write(indent+"FP = %s;\n" % self.global_vars)
            f.write(indent+"SP = FP;\n")

            '''
            for symbol in symbol_table:
                if not symbol_table[symbol].local:
            '''

            # set up/check for built in procedures
            self._built_in_procedure()

            while (self._statement() != "None"):
                if (self.curr_tok.type == "end"): break

                # set up/check for built in procedures
                self._built_in_procedure()

                # check to see if current statement is a procedure call
                self._check_for_proc_call()
                '''
                if (self.curr_tok.lex in symbol_table.keys()):
                    if (symbol_table[self.curr_tok.lex].procedure):
                        self.proc_call = 1
                '''

                if self.proc_call and not self._predefined_proc:
                    f.write(indent+"SP = SP + %d;\n" %symbol_table[self.proc_name].param_count)

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
        f.write("int main(void) {\n")
        f.write(indent+"goto main;\n")
        f.write(open("../runtime/runtime_inline.c").read())
        f.write('\n')

        parse = parser(get_tokens())
        parse._program_header()

        f.write("return 0;\n")
        f.write("}\n")