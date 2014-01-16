import os
import sys

from tokens import token_table as token_table

f = open(sys.argv[1])
token = []

class scanner:

    def read_file():
        dot_cnt  = 0
        line_cnt = 0
        colm_pos = 1

        temp_tokens = ""

        #lines = f.read().splitlines()
        #for line in lines:
        #    for char in line:
        #for char in f.read().strip(' '):
        for char in f.read():
            colm_pos += 1
            if ((char.isdigit() or char == ".") and dot_cnt <= 1):
                temp_tokens += char
                if (char == "."   ): dot_cnt += 1
                #if (char.isdigit()): dot_cnt = 0

            else:
                print "no good son"
                break
                #return

            if (char in token_table):
                print token_table[char]
            if (char[-1] == "\n"):
                dot_cnt  =  0
                line_cnt += 1
                colm_pos =  1
            #char = char.replace(" ", "")
            #token.append(char)
            #if (char.is
            #if (char.isdigit() or char == "."):
            #    if (char.isdigit()):
            #        temp_tokens += char
            #print temp_tokens
        #    if (char.isdigit()):
        #        print token_table['int']
            #else:
            #    print "token not supported %s", char
            #colm_pos += 1
            ##if token not in token_table

        #for i in range(len(line)):
        #    if ((line[i].isdigit() and line[i+1].isalpha()) or
        #        (line[i].isalpha() and line[i+1].isdigit())):
        #        print hello

        #print line_cnt
        #print colm_pos
        #print token

    #def end_of_line():

    def main():
        #print tokens.OR
        #if __init__ = "main"
        read_file()

    main()
