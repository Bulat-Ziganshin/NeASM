import sys, re, itertools
import registers

# Start from scratch
def clearall():
    # Here we keep all assembler statements issued by the program
    global cmd_lists
    cmd_lists = [[]]
    clear_regs()

# Add one more statement to the last command list
def asm(*args):
    global cmd_lists
    cmd_lists[-1].append(args)

# Print all accumulated ASM statements and clear the list
def flush():
    global cmd_lists
    for list in cmd_lists:
        for cmd in list:
            print(cmd[0], ','.join(cmd[1:]))
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


# Initialize the free registers list
def clear_regs():
    # Here we keep registers which aren't yet allocated
    global free_regs
    free_regs = registers.reg.copy()
    free_regs.remove("rcx")
    free_regs.remove("rsp")

# Allocate one register from the free list
def alloc_reg():
    global free_regs
    return free_regs.pop(0)

# Allocate n registers from the free list
def alloc_regs(n):
    global free_regs
    result = free_regs[0:n]
    free_regs = free_regs[n:]
    return result

# Return registers to the free list
def free_reg(*regs):
    global free_regs
    free_regs[0:0] = regs


clearall()
