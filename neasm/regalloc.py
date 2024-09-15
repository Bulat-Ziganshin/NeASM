import re, registers

# Allocates registers for variables from the common pool
class RegisterAllocator:
    def __init__(self, reserve = []):
        # Initialize the free register lists. Here we keep registers which aren't yet allocated.
        self.free_regs      = [x for x in registers.reg  if x not in reserve]
        self.free_simd_regs = [x for x in registers.xmm  if x not in reserve]

        self.var_type     = dict()      # declared var types (id->type mapping)
        self.first_line   = dict()      # first line where a var was used (id->linenum mapping)
        self.last_line    = dict()      # last line where a var was used
        self.var_register = dict()      # register assigned to a var (id->register mapping)

    # Allocate one register of given type from the corresponding free list
    def alloc_reg(self, typ = 'r'):
        if typ == 'r':
            return self.free_regs.pop(0)
        else:
            return typ + self.free_simd_regs.pop(0)[1:]

    # Allocate n registers from the free list
    def alloc_regs(self, n, typ = 'r'):
        return [self.alloc_reg(typ)  for _ in range(n)]

    # Return registers to the free list
    def free_reg(self, *regs):
        for reg in regs:
            if reg[0] in "xyz":
                self.free_simd_regs.insert(0, "x" + reg[1:])
            else:
                self.free_regs.insert(0, reg)

    # Declare ids as variable names that will require register allocation
    def try_process_directive(self, directive, *params):
        if re.fullmatch(r'(xmm_|ymm_|zmm_)?register(s)?', directive):
            for id_list in params:
                # id_list is a list of ids, separated by commas
                for id in re.split(',', id_list):
                    varname = id.strip()
                    # check id for `letter(letter_or_digit)*` syntax
                    if re.fullmatch(r'\w+', varname)  and  not re.fullmatch(r'\d\w*', varname):
                        self.var_type[varname] = directive[0]
                    else:
                        raise RuntimeError("<"+varname+"> should be an identifier")
            return True

    # Record the first and last line where the variable was used
    def seen_at(self, varname, linenum):
        if varname in self.var_type:
            self.first_line.setdefault(varname, linenum)
            self.last_line[varname] = linenum

    # Analyze lifetime of each variable and alloc the same registers to non-overlapping lifes
    def lifetime_analysis(self):
        # The current allocator suppose that a single ASM statement can't modify more than one register.
        # This allows us to alloc the same register for last use of var1 and first use of var2,
        # thus ALLOC > FREE below.

        # Variable lifetime records
        life = [];  ALLOC = 1;  FREE = 0   # should be ALLOC > FREE for correct order of alloc/free events
        for id in self.first_line.keys():
            life.append((self.first_line[id], ALLOC, id))   # first use of id -> alloc
            life.append((self.last_line[id], FREE, id))     # last use of id -> free

        # Assign registers to variables based on the lifetime analysis
        for (_,op,id) in sorted(life):
            if self.first_line[id] == self.last_line[id]:
                # This var appears only in a single statement, we should alloc a register and then free it immediately
                if op==ALLOC:
                    self.var_register[id] = self.alloc_reg(self.var_type[id])
                    self.free_reg(self.var_register[id])
            elif op==ALLOC:
                self.var_register[id] = self.alloc_reg(self.var_type[id])
            else:
                self.free_reg(self.var_register[id])

    # Replace a variable name with assigned register name, or return id unchanged
    def var2reg(self, id):
        return self.var_register.get(id, id)
