
asmx = []

def asm(*args):
    asmx.append(args)

def asm_finish():
    for cmd in asmx:
        print(cmd[0], ','.join(cmd[1:]))
