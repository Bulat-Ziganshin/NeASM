# This is an example of using NeASM as Python library

import neasm
from neasm import asm
from registers import *

asm("add", rax, rbx)
asm("sub", rax, rbx)

asm("")
for n in range(4):
    asm("paddq", xmm[n+1], xmm[n])

asm("")
for n in range(8,12):
    neasm.start_new_stream()
    asm("mov", reg[n], "[ebp+"+str(n*8)+"]")
    asm("vmovdqu", ymm[n], "[r"+str(n)+"]")
    asm("vpcmpeqb", ymm[n], ymm0)
    asm("vpmovmskb", reg[n], ymm[n])
    asm("mov", "[ebp+"+str(n*8)+"]", reg[n])
neasm.interleave_streams()

neasm.finish()
