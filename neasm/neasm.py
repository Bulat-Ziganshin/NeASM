import sys, re, itertools
import registers


# Char used to start a comment in ASM code (either '#' or ';)
cmt_char = '#'

# Registers that shouldn't be used by our register allocator.
# CL is reserved for occasional shifts,
# and we suppose that RBP is available since stack vars are addressed via RSP
reserve_registers = ["rcx", "rsp"]


# Do smth on errors :)
def error(*msg):
    print("ERROR:", *msg)

# Start from scratch
def clearall():
    global cmd_lists, equ_dict, vars
    # Here we keep all assembler statements issued by the program
    cmd_lists = [[]]
    # Here we keep all EQU definitions
    equ_dict = dict()
    # Here we keep the variable->register mapping
    vars = RegisterAllocator()

# Add one more statement to the last command list
def asm(*args):
    global cmd_lists
    cmd_lists[-1].append(args)

# Add definition to the EQU list
def equ(word, replacement):
    global equ_dict
    equ_dict[word] = str(replacement)

# Print all accumulated ASM statements and clear the list
def flush():
    program = []
    linenum = 0

    # The first pass over the program, only executing directives
    for one_list in cmd_lists:
        for one_command in one_list:
            # Combine parts of the command into a single string and separate the non-comment part for further processing
            if len(one_command) > 1:
                full_line = one_command[0] + " " + (",".join(one_command[1:]))
            else:
                full_line = one_command[0]
            cmd,sep,comment = full_line.partition(cmt_char)

            # Execute REGISTER directive
            matchobj = re.fullmatch(r'([\S]+)\s+(.*?)\s*', cmd)
            if matchobj:
                op,param = matchobj.group(1,2)
                if op.upper() == 'REGISTER':
                    vars.declare(param)
                    sep = cmt_char + ' ' + cmd + sep
                    cmd = ""

            # Record lines where an identifier was seen
            for matchobj in re.finditer(r'\w+', cmd):
                id = matchobj.group(0)
                vars.seen_at(id, linenum)

            program.append(cmd + sep + comment)
            linenum += 1

    vars.lifetime_analysis()

    # Replace an identifier with its EQU definition or register name
    def replace_ids(matchobj):
        id = matchobj.group(0)
        return vars.var2reg(equ_dict.get(id, id))

    # The second pass over the program, replacing identifiers with their EQU/REGISTER definitions
    for full_line in program:
        cmd,sep,comment = full_line.partition(cmt_char)
        if cmd=="":
            print("".ljust(40) + sep + comment)
        else:
            new_cmd = re.sub(r'\w+', replace_ids, cmd)
            print(new_cmd.ljust(35) + '     ' + cmt_char + ' ' + cmd + sep + comment)

    clearall()


# Start a new command stream
def start_new_stream():
    cmd_lists.append([])

# Interleave commands in extra command streams, and add them to the main stream
def interleave_streams():
    global cmd_lists
    res = list(map(list, itertools.zip_longest(*cmd_lists[1:])))
    for lst in res:
        for cmd in lst:
            if cmd:
                cmd_lists[0].append(cmd)
    cmd_lists = cmd_lists[0:1]


# Allocates registers for variables from a common pool
class RegisterAllocator:
    def __init__(self):
        # Initialize the free registers list
        # Here we keep registers which aren't yet allocated
        self.free_regs = registers.reg.copy()
        for reg in reserve_registers:
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
                    error("<"+varname+"> should be an identifier")

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
                    self.var[id] = alloc_reg()
                    free_reg(self.var[id])
            elif op==ALLOC:
                self.var[id] = alloc_reg()
            else:
                free_reg(self.var[id])

    # Replace a variable name with assigned register name, or return id unchanged
    def var2reg(self, id):
        return self.var.get(id, id)


def alloc_reg():
    return vars.alloc_reg()

def alloc_regs(n):
    return vars.alloc_regs(n)

def free_reg(*regs):
    vars.free_reg(*regs)


clearall()
