symbol_table = {}

class token_symbol:
    def __init__(self):
        self.type = None
        self.lex = None
        self.value = None
        self.address = None
        self.line = None
        self.p_in = None
        self.p_out = None
        self.array_size = None
        self.label = None
        self.data_type = None
        self.r_addr = None
        self.procedure = None
        self.proc_local = None
        self.proc_name = None
        self.ident = None
        #self.local = []
        self.local = None
        self.param_list = []
        self.param_count = None
        self.size = None
