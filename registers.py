### Register names ##############################

reg = []
reg32 = []
reg16 = []
reg8 = []
xmm = []
ymm = []
zmm = []

for n in range(16):
    r_n = "r" + str(n)
    e_n = r_n + "d"
    w_n = r_n + "w"
    b_n = r_n + "b"
    xmm_n = "xmm" + str(n)
    ymm_n = "ymm" + str(n)
    zmm_n = "zmm" + str(n)

    reg.append(r_n)
    reg32.append(e_n)
    reg16.append(w_n)
    reg8.append(b_n)
    xmm.append(xmm_n)
    ymm.append(ymm_n)
    zmm.append(zmm_n)

reg[0:8] = ["rax", "rcx", "rdx", "rbx", "rsi", "rdi", "rbp", "rsp"]
reg64 = reg
reg32[0:8] = ["eax", "ecx", "edx", "ebx", "esi", "edi", "ebp", "esp"]
reg16[0:8] = ["ax", "cx", "dx", "bx", "si", "di", "bp", "sp"]
reg8[0:8] = ["al", "cl", "dl", "bl", "sil", "dil", "bpl", "spl"]
ah = "ah";  bh = "bh";  ch = "ch";  dh = "dh";


# Auto-generated code
rax = reg[0];  r0 = reg[0];  eax = reg32[0];  r0d = reg32[0];  ax = reg16[0];  r0w = reg16[0];  al = reg8[0];  r0b = reg8[0];  xmm0 = xmm[0];  ymm0 = ymm[0];  zmm0 = zmm[0]
rcx = reg[1];  r1 = reg[1];  ecx = reg32[1];  r1d = reg32[1];  cx = reg16[1];  r1w = reg16[1];  cl = reg8[1];  r1b = reg8[1];  xmm1 = xmm[1];  ymm1 = ymm[1];  zmm1 = zmm[1]
rdx = reg[2];  r2 = reg[2];  edx = reg32[2];  r2d = reg32[2];  dx = reg16[2];  r2w = reg16[2];  dl = reg8[2];  r2b = reg8[2];  xmm2 = xmm[2];  ymm2 = ymm[2];  zmm2 = zmm[2]
rbx = reg[3];  r3 = reg[3];  ebx = reg32[3];  r3d = reg32[3];  bx = reg16[3];  r3w = reg16[3];  bl = reg8[3];  r3b = reg8[3];  xmm3 = xmm[3];  ymm3 = ymm[3];  zmm3 = zmm[3]
rsi = reg[4];  r4 = reg[4];  esi = reg32[4];  r4d = reg32[4];  si = reg16[4];  r4w = reg16[4];  sil = reg8[4];  r4b = reg8[4];  xmm4 = xmm[4];  ymm4 = ymm[4];  zmm4 = zmm[4]
rdi = reg[5];  r5 = reg[5];  edi = reg32[5];  r5d = reg32[5];  di = reg16[5];  r5w = reg16[5];  dil = reg8[5];  r5b = reg8[5];  xmm5 = xmm[5];  ymm5 = ymm[5];  zmm5 = zmm[5]
rbp = reg[6];  r6 = reg[6];  ebp = reg32[6];  r6d = reg32[6];  bp = reg16[6];  r6w = reg16[6];  bpl = reg8[6];  r6b = reg8[6];  xmm6 = xmm[6];  ymm6 = ymm[6];  zmm6 = zmm[6]
rsp = reg[7];  r7 = reg[7];  esp = reg32[7];  r7d = reg32[7];  sp = reg16[7];  r7w = reg16[7];  spl = reg8[7];  r7b = reg8[7];  xmm7 = xmm[7];  ymm7 = ymm[7];  zmm7 = zmm[7]
r8 = reg[8];  r8 = reg[8];  r8d = reg32[8];  r8d = reg32[8];  r8w = reg16[8];  r8w = reg16[8];  r8b = reg8[8];  r8b = reg8[8];  xmm8 = xmm[8];  ymm8 = ymm[8];  zmm8 = zmm[8]
r9 = reg[9];  r9 = reg[9];  r9d = reg32[9];  r9d = reg32[9];  r9w = reg16[9];  r9w = reg16[9];  r9b = reg8[9];  r9b = reg8[9];  xmm9 = xmm[9];  ymm9 = ymm[9];  zmm9 = zmm[9]
r10 = reg[10];  r10 = reg[10];  r10d = reg32[10];  r10d = reg32[10];  r10w = reg16[10];  r10w = reg16[10];  r10b = reg8[10];  r10b = reg8[10];  xmm10 = xmm[10];  ymm10 = ymm[10];  zmm10 = zmm[10]
r11 = reg[11];  r11 = reg[11];  r11d = reg32[11];  r11d = reg32[11];  r11w = reg16[11];  r11w = reg16[11];  r11b = reg8[11];  r11b = reg8[11];  xmm11 = xmm[11];  ymm11 = ymm[11];  zmm11 = zmm[11]
r12 = reg[12];  r12 = reg[12];  r12d = reg32[12];  r12d = reg32[12];  r12w = reg16[12];  r12w = reg16[12];  r12b = reg8[12];  r12b = reg8[12];  xmm12 = xmm[12];  ymm12 = ymm[12];  zmm12 = zmm[12]
r13 = reg[13];  r13 = reg[13];  r13d = reg32[13];  r13d = reg32[13];  r13w = reg16[13];  r13w = reg16[13];  r13b = reg8[13];  r13b = reg8[13];  xmm13 = xmm[13];  ymm13 = ymm[13];  zmm13 = zmm[13]
r14 = reg[14];  r14 = reg[14];  r14d = reg32[14];  r14d = reg32[14];  r14w = reg16[14];  r14w = reg16[14];  r14b = reg8[14];  r14b = reg8[14];  xmm14 = xmm[14];  ymm14 = ymm[14];  zmm14 = zmm[14]
r15 = reg[15];  r15 = reg[15];  r15d = reg32[15];  r15d = reg32[15];  r15w = reg16[15];  r15w = reg16[15];  r15b = reg8[15];  r15b = reg8[15];  xmm15 = xmm[15];  ymm15 = ymm[15];  zmm15 = zmm[15]


if __name__ == "__main__":
    for n in range(16):
        r_n = "r" + str(n)
        e_n = r_n + "d"
        w_n = r_n + "w"
        b_n = r_n + "b"
        xmm_n = "xmm" + str(n)
        ymm_n = "ymm" + str(n)
        zmm_n = "zmm" + str(n)

        print(reg[n]   + " = reg[" + str(n) + "];  "
            + r_n      + " = reg[" + str(n) + "];  "
            + reg32[n] + " = reg32[" + str(n) + "];  "
            + e_n      + " = reg32[" + str(n) + "];  "
            + reg16[n] + " = reg16[" + str(n) + "];  "
            + w_n      + " = reg16[" + str(n) + "];  "
            + reg8[n]  + " = reg8[" + str(n) + "];  "
            + b_n      + " = reg8[" + str(n) + "];  "
            + xmm_n    + " = xmm[" + str(n) + "];  "
            + ymm_n    + " = ymm[" + str(n) + "];  "
            + zmm_n    + " = zmm[" + str(n) + "]")
