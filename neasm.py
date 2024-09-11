import sys, re, itertools

# Here we keep all assembler statements issued by the program
cmd_lists = [[]]

# Add one more statement to the last command list
def asm(*args):
    cmd_lists[-1].append(args)

# Print all accumulated ASM statements and clear the list
def finish():
    global cmd_lists
    for list in cmd_lists:
        for cmd in list:
            print(cmd[0], ','.join(cmd[1:]))
    cmd_lists = [[]]

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
