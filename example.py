from neasm import *

asm("add", rax, rbx)
asm("sub", rax, rbx)

for n in range(4):
    asm("padd", xmm[n+1], xmm[n])


asm_finish()
