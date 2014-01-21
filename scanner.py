import os
import sys

from tokens import token_table as token_table

f = open(sys.argv[1]).read()

line_cnt = 1
colm_pos = 1

curr_char = ""
next_char = ""

index = 0

tokens = []

#def end_of_line():
#
#    for char in tokens:
#        if (char == "\n"):
#            eol = 1
#
#        return eol

def get_next_char():
    global curr_char
    global next_char
    global index

    curr_char = f[index]

    if (index+1 == len(f)):
        next_char = None
    else:
        next_char = f[index+1]

    index += 1

def update_line_cnt():
    global line_cnt
    global colm_pos

    if (next_char == "\n"):
        line_cnt += 1
        colm_pos  = 1

    return line_cnt, colm_pos

def get_tokens():
    global line_cnt
    global colm_pos

    error = 0

    curr_token   = ""
    reserved_ids = ['string'   , 'int'  , 'bool'  , 'float'  ,
                    'global'   , 'in'   , 'out'   , 'if'     ,
                    'then'     , 'else' , 'case'  , 'for'    ,
                    'not'      , 'true' , 'false' , 'program',
                    'procedure', 'begin', 'return', 'end'    ]

    operators    = ["<", ">", "!", ":"]

    #while not(next_char is None):
    while (next_char is not(None)):

        get_next_char()

        # check if char is part of the alphabet
        if (curr_char.isalpha()):
            curr_token = curr_char

            # check for white space
            #if (curr_token == " "):

            # keep fetching the next char until it's no longer
            # alphanumeric and we have not hit the end of a new
            # line
            while (next_char.isalnum() and next_char != "\n"):
                curr_token += next_char
                get_next_char()
                colm_pos += 1

            #if (curr_token in token_table):
                #token.append(token_table[curr_token] + ', ' + curr_token)
            if (curr_token in reserved_ids):
                tokens.append(curr_token)
            else:
                tokens.append(("id", curr_token))

        # check if char is a digit or a decmial point
        if (curr_char.isdigit() or curr_char == "."):
            curr_token = curr_char
            error = 0

            # keep fetching the next char as long as the next
            # char is a digit or we do not have an extra decimal
            # point in our input stream
            while ((next_char.isdigit() or next_char == ".") and (next_char != "\n")):

                # check for more than one decimal point in input stream
                if (((next_char == ".") and (next_char not in curr_token)) or next_char.isdigit()):
                    curr_token += next_char
                    get_next_char()
                    colm_pos += 1
                else:
                    error = 1
                    break

            if (error):
                while (next_char != "\n"):
                    curr_token += next_char
                    get_next_char()
                    colm_pos += 1

                tokens.append(("unknown_token", curr_token))
                print "syntax error: '%s': line:%i:%i" % (curr_token, line_cnt, colm_pos)

            else:
                if (curr_token[0] == "."):
                    print "[warning]: leading zero is missing, it has been added"
                    curr_token = '0' + curr_token

                if (curr_token[-1] == "."):
                    print "[warning]: trailing zero is missing, it has been added"
                    curr_token += '0'

                if ("." in curr_token):
                    tokens.append(("float", curr_token))
                else:
                    tokens.append(("int"  , curr_token))

        # check for strings
        if (curr_char == "\""):
            curr_token = curr_char

            # keep fetching the next char as long as the next char
            # is not an end quote or an escape sequence
            while ((next_char not in ["\"", "\\"]) and (next_char != "\n")):
                curr_token += next_char
                get_next_char()
                colm_pos += 1

            if ((next_char == "\"") and (next_char != "\n")):
                curr_token += next_char
                get_next_char()
                colm_pos += 1
                tokens.append(("string", curr_token))

            else:
                print "missing end quote: line:%i:%i" % (line_cnt, colm_pos)
                tokens.append(("uknown_token", curr_token))

        #else:

        # ignore white space
        if (curr_char == " "): continue

        # check for operators
        if (curr_char in operators):
            curr_token = curr_char

            if (next_char == "="):
                curr_token += next_char
                get_next_char()
                colm_pos += 1
                tokens.append((token_table[curr_token], curr_token))

            if (next_char in operators):
                curr_token += next_char
                get_next_char()
                colm_pos += 1
                tokens.append(("unknown_token", curr_token))

        # check for division or comment
        if (curr_char == "/"):
            curr_token = curr_char

            #if ((next_char.isdigit() or next_char.isalpha()) and (next_char != "\n")):
            if (next_char != "/" and next_char != "\n"):
                colm_pos += 1
                tokens.append((token_table[curr_token], curr_token))

            elif (next_char == "/"):
                while (next_char != "\n"):
                    curr_token += next_char
                    get_next_char()
                    colm_pos += 1

                # most likely token_table will be gone, much simplier to just
                # pass in the strings directly
                tokens.append((token_table[curr_token[0:2]], curr_token))

        if (curr_char == "\\"):
            curr_token = curr_char

            if (next_char in ["t", "n"] and next_char != "\n"):
                curr_token += next_char
                get_next_char()
                colm_pos += 1

            else:
                print "escape sequence, %s is not supported: line:%i:%i" % (curr_token, line_cnt, colm_pos)

            tokens.append((token_table[curr_token], curr_token))

            #if (curr_char in token_table):
            #    print "wtf"
            #    tokens.append(token_table[curr_char] + ", " + curr_char)

        update_line_cnt()

    print tokens

def main():

    program_file = sys.argv[1]
    if (program_file.endswith('.ee')):
        get_tokens()

    else:
        print "file format not recognized"

main()
