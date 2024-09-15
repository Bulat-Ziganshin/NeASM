import re, registers

# Allocates registers for variables from a common pool
class RegisterAllocator:
    def __init__(self, reserve = []):
        # Initialize the free registers list
        # Here we keep registers which aren't yet allocated
        self.free_regs = registers.reg.copy()
        for reg in reserve:
            self.free_regs.remove(reg)

        self.declared_vars = set()          # list of declared var names
        self.first_line = dict()            # first line where a var was used (id->linenum mapping)
        self.last_line = dict()             # last line where a var was used
        self.var = dict()

    # Allocate one register from the free list
    def alloc_reg(self):
        return self.free_regs.pop(0)

    # Allocate n registers from the free list
    def alloc_regs(self, n):
        result = self.free_regs[0:n]
        self.free_regs = self.free_regs[n:]
        return result

    # Return registers to the free list
    def free_reg(self, *regs):
        self.free_regs[0:0] = regs

    # Declare ids as variable names that will require register allocation
    def declare(self, *all_ids):
        for id_list in all_ids:
            # id_list is a list of ids, separated by commas
            for id in re.split(',', id_list):
                varname = id.strip()
                # check id for `letter(letter_or_digit)*` syntax
                if re.fullmatch(r'\w+', varname)  and  not re.fullmatch(r'\d\w*', varname):
                    self.declared_vars.add(varname)
                else:
                    raise RuntimeError("<"+varname+"> should be an identifier")

    # Record the first and last line where the id was used
    def seen_at(self, id, linenum):
        if id in self.declared_vars:
            self.first_line.setdefault(id, linenum)
            self.last_line[id] = linenum

    # Analyze lifetime of each variable and alloc the same registers to non-overlapping lifes
    def lifetime_analysis(self):
        # To do: the current allocator suppose that a single ASM statement can't modify more than one register.
        # This allows us to alloc the same register for last use of var1 and first use of var2.

        # Variable lifetime records
        life = [];  ALLOC = 1;  FREE = 0   # should be ALLOC > FREE for correct order of alloc/free events
        for id in self.first_line.keys():
            life.append((self.first_line[id], ALLOC, id))   # first use of id - alloc
            life.append((self.last_line[id], FREE, id))     # last use of id - free
        life.sort()

        # Assign registers to variables based on the lifetime analysis
        for (_,op,id) in life:
            if self.first_line[id] == self.last_line[id]:
                # A var used only in a single line, we should alloc a register and free it immediately
                if op==ALLOC:
                    self.var[id] = self.alloc_reg()
                    self.free_reg(self.var[id])
            elif op==ALLOC:
                self.var[id] = self.alloc_reg()
            else:
                self.free_reg(self.var[id])

    # Replace a variable name with assigned register name, or return id unchanged
    def var2reg(self, id):
        return self.var.get(id, id)
