# This is an example of using NeASM as Python library
import sys
sys.path.append('../neasm')

import neasm
from neasm import asm, alloc_reg, alloc_regs, free_reg
from registers import *


asm("add", rax, rbx)
asm("sub", rax, rbx)

asm("")
for n in range(4):
    asm("paddq", xmm[n+1], xmm[n])

asm("")
for n in range(8,10):
    neasm.start_new_stream()
    asm("mov", reg[n], "[ebp+"+str(n*8)+"]")
    asm("vmovdqu", ymm[n], "[r"+str(n)+"]")
    asm("vpcmpeqb", ymm[n], ymm0)
    asm("vpmovmskb", reg[n], ymm[n])
    asm("mov", "[ebp+"+str(n*8)+"]", reg[n])
neasm.interleave_streams()

asm("")
dict = alloc_reg()
pos = alloc_regs(12)
for n in range(8,12):
    neasm.start_new_stream()
    offset = pos[n]+"d"
    asm("mov", offset, "[ebp+"+str(n*4)+"]")
    asm("vmovdqu", ymm[n], "["+dict+"+"+offset+"*4]")
    asm("vpcmpeqb", ymm[n], ymm0)
    asm("vpmovmskb", offset, ymm[n])
    asm("mov", "[ebp+"+str(n*4)+"]", offset)
neasm.interleave_streams()
free_reg(*pos)

asm("")
neasm.equ("dict", "rax")
neasm.equ("pos", "rbx")
asm("mov rdx, [dict+pos]")

neasm.flush()
