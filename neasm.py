import sys, re

asmx = []

def asm(*args):
    asmx.append(args)

def finish():
    for cmd in asmx:
        print(cmd[0], ','.join(cmd[1:]))
