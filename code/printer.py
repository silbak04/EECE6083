def print_error(error_message, token, line):

    red     = '\033[31m'
    default = '\033[0m'

    print red + "[error]: " + default + "%s%s on line: %i" % (error_message, token, line)
    scanner_error = True

    return scanner_error

def print_warning(warning_message, line):

    yellow  = '\033[93m'
    default = '\033[0m'

    print yellow + "[warning]: " + default + "%s on line: %i" % (warning_message, line)
    return
