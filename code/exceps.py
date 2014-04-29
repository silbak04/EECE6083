class ErrorToken(Exception):
    def __init__(self, exp_tok, rec_tok):
        self.exp_tok  = exp_tok
        self.rec_tok  = rec_tok

        return

    def print_error(self, err_msg):
        self.err_msg  = err_msg

        red     = '\033[31m'
        default = '\033[0m'

        print red + "[syntax error]: " + default + "%s" %(self.err_msg)

        return

    def print_warning(self, err_msg):
        self.err_msg  = err_msg

        yellow  = '\033[93m'
        default = '\033[0m'

        print yellow + "[warning]: " + default + "%s" %(self.err_msg)
