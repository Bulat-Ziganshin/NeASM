import sys, re, itertools
import registers


# Char used to start a comment in ASM code (either '#' or ';)
cmt_char = '#'

# Start from scratch
def clearall():
    global cmd_lists, equ_dict, regalloc
    # Here we keep all assembler statements issued by the program
    cmd_lists = [[]]
    # Here we keep all EQU definitions
    equ_dict = dict()
    regalloc = RegisterAllocator()

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
    # Replace a word with its definition stored in equ_dict
    def replace_equ(matchobj):
        word = matchobj.group(0)
        return equ_dict.get(word, word)

    for one_list in cmd_lists:
        for one_command in one_list:
            # Combine parts of the command into a single string and separate the non-comment part for further processing
            full_line = one_command[0] + " " + (",".join(one_command[1:]))
            cmd,sep,comment = full_line.partition(cmt_char)

            # Replace words with their EQU definitions
            re_word = r'\w[\w\d]*'
            cmd = re.sub(re_word, replace_equ, cmd)
            print(cmd + sep + comment)

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

def alloc_reg():
    return regalloc.alloc_reg()

def alloc_regs(n):
    return regalloc.alloc_regs(n)

def free_reg(*regs):
    regalloc.free_reg(*regs)


clearall()
