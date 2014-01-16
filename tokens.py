# https://www.ics.uci.edu/~pattis/ICS-31/lectures/tokens.pdf
# http://ee.hawaii.edu/~tep/EE160/Book/chap14/subsection2.1.1.5.html
# https://stackoverflow.com/questions/15599639/whats-perfect-counterpart-in-python-for-while-not-eof

#class token_symb(set):
#    def __getattr__(self, token):
#        if token in self:
#            return token
#        raise AttributeError
#
#tokens = token_symb(["COMMA"])
#tokens.COMMA = ","
#print tokens.COMMA

token_table = {
        'string'    : 'string',
        'int'       : 'int',
        'bool'      : 'bool',
        'float'     : 'float',
        'global'    : 'global',
        'in'        : 'in',
        'out'       : 'out',
        'if'        : 'if',
        'then'      : 'then',
        'else'      : 'else',
        'case'      : 'case',
        'for'       : 'for',
        'and'       : 'and',
        'or'        : 'or',
        'not'       : 'not',
        'program'   : 'program',
        'procedure' : 'procedure',
        'begin'     : 'begin',
        'return'    : 'return',
        'end'       : 'end',
        '_'         : 'under_score',
        '\''        : 'tick',
        '('         : 'open_paren',
        ')'         : 'closed_paren',
        '{'         : 'open_brace',
        '}'         : 'closed_brace',
        '='         : 'eq',
        '<'         : 'lt',
        '>'         : 'gt',
        '<='        : 'lte',
        '>='        : 'gte',
        ':='        : 'coloneq',
        '!='        : 'noteq',
        '+'         : 'plus',
        '-'         : 'minus',
        '*'         : 'star',
        '/'         : 'slash',
        ','         : 'comma',
        ':'         : 'colon',
        ';'         : 'semicolon',
        '.'         : 'dot',
        '//'        : 'double_slash'
        }
