import sys, re, itertools
import registers, regalloc


# Char used to start a comment in ASM code (either '#' or ';)
cmt_char = '#'

# Registers that shouldn't be used by our register allocator:
#   CL is reserved for occasional shifts,
#   and we suppose that RBP is available since stack vars are addressed via RSP
reserve_registers = ["rcx", "rsp"]


# Start from scratch
def clearall():
    global cmd_lists, equ_dict, vars
    # Here we keep all assembler statements issued by the program
    cmd_lists = [[]]
    # Here we keep all EQU definitions
    equ_dict = dict()
    # Here we keep the variable->register mapping
    vars = regalloc.RegisterAllocator(reserve = reserve_registers)

# Add one more statement to the current command list
def asm(*args):
    global cmd_lists
    # Combine parts of the command into a single string
    if len(args) > 1:
        original_line = args[0] + " " + (",".join(args[1:]))
    elif len(args) == 1:
        original_line = args[0]
    else:
        original_line = ""

    # Replace an identifier with its EQU definition
    def replace_equs(matchobj):
        id = matchobj.group(0)
        return equ_dict.get(id, id)

    # Save both the full original line (for listing)
    #   and the active command part after EQU substitutions
    cmd,_,_ = original_line.partition(cmt_char)
    cmd = re.sub(r'\w+', replace_equs, cmd)
    cmd_lists[-1].append((cmd.strip(), original_line))

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
        for cmd,original_line in one_list:
            # Execute REGISTER directive
            matchobj = re.fullmatch(r'([\S]+)\s+(.*?)', cmd)
            if matchobj:
                directive,param = matchobj.group(1,2)
                directive = directive.lower()
                if vars.try_process_directive(directive,param):
                    cmd = ""

            # Record lines where an identifier was seen
            for matchobj in re.finditer(r'\w+', cmd):
                id = matchobj.group(0)
                vars.seen_at(id, linenum)

            program.append((cmd,original_line))
            linenum += 1

    vars.lifetime_analysis()

    # Replace an identifier with its register name
    def replace_varnames(matchobj):
        id = matchobj.group(0)
        return vars.var2reg(id)

    # The second pass over the program, replacing varnames with registers allocated to the vars
    for cmd,original_line in program:
        cmd = re.sub(r'\w+', replace_varnames, cmd)
        print(cmd.ljust(35) + '     ' + cmt_char + ' ' + original_line)

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


def alloc_reg(*args):
    return vars.alloc_reg(*args)

def alloc_regs(*args):
    return vars.alloc_regs(*args)

def free_reg(*regs):
    vars.free_reg(*regs)


clearall()
