import sys, re, itertools
import registers


# Char used to start a comment in ASM code (either '#' or ';)
cmt_char = '#'

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
    linenum = 0

    # Replace a word with its definition stored in equ_dict
    def replace_equ(matchobj):
        id = matchobj.group(0)
        vars.seen_at(id, linenum)
        return equ_dict.get(id, id)

    for one_list in cmd_lists:
        for one_command in one_list:
            # Combine parts of the command into a single string and separate the non-comment part for further processing
            if len(one_command) > 1:
                full_line = one_command[0] + " " + (",".join(one_command[1:]))
            else:
                full_line = one_command[0]
            cmd,sep,comment = full_line.partition(cmt_char)

            # Execute DECLARE meta-command
            matchobj = re.fullmatch(r'([\S]+)\s+(.*?)\s*', cmd)
            if matchobj:
                op,param = matchobj.group(1,2)
                if op.lower() == 'declare':
                    vars.declare(param)
                    cmd = cmt_char + ' ' + cmd

            # Replace words with their EQU definitions
            cmd = re.sub(r'\w+', replace_equ, cmd)
            print(cmd + sep + comment)
            linenum += 1

    vars.lifeness_analysis()
    ###print(vars.alloc_before)
    ###print(vars.free_after)

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
        self.free_regs.remove("rcx")
        self.free_regs.remove("rsp")

        self.declared_vars = set()          # list of declared var names
        self.first_line = dict()            # first line where a var was used (id->linenum mapping)
        self.alloc_before = dict()          #   the same (linenum->list of ids mapping)
        self.last_line = dict()             # last line where a var was used
        self.free_after = dict()            #   the same (linenum->list of ids mapping)

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

    # Declare id as a variable name that will require a register allocation
    def declare(self, id):
        self.declared_vars.add(id)

    # Record the first and last line where the id was used
    def seen_at(self, id, linenum):
        if id in self.declared_vars:
            self.first_line.setdefault(id, linenum)
            self.last_line[id] = linenum

    def lifeness_analysis(self):
        for id in self.first_line.keys():
            first = self.first_line[id]
            last = self.last_line[id]
            self.alloc_before.setdefault(first,[]).append(id)
            self.free_after.setdefault(last,[]).append(id)
            ###print(id, self.first_line[id], '-', self.last_line[id])

def alloc_reg():
    return vars.alloc_reg()

def alloc_regs(n):
    return vars.alloc_regs(n)

def free_reg(*regs):
    vars.free_reg(*regs)


clearall()
