# This is an example of using NeASM as Python library

import neasm
from neasm import asm
from registers import *

asm("add", rax, rbx)
asm("sub", rax, rbx)

for n in range(4):
    asm("paddq", xmm[n+1], xmm[n])


neasm.finish()
