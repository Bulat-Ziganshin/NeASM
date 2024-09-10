## Python-based High-Level Assembler

There are many ways to implement High-Level Assembler.
This project resembles [Perl ASM](https://github.com/openssl/openssl/blob/master/crypto/aes/asm/aesv8-armx.pl) and Mojo.

Here, Python is used as a compile-time meta-language, employing its loops, subroutines, ifs, variables...
for dynamic generation of resulting assembler code.

We plan to add virtual registers (a-la PTX), automatic code reordering,
and asm-like syntax.

With asm-like syntax, one could write e.g.:
```
%for n in range(4):
  paddq {xmm[n+1]}, {xmm[n]}
```

that will be auto-translated into code:
```python
for n in range(4):
  asm("paddq", xmm[n+1], xmm[n])
```

and executed by Python to generate the final assembler code.

This means that eventually, we will be able to write the usual assembler code,
extended with Python as a meta-language to generate repetitive code,
auto-alloc registers, and perform user-defined code transformations.

---

Even the current minimalist implementation allows one
to employ the full power of Python to generate assembler code:
1. Assign readable names to registers, constants and memory locations
2. Use Python loops to write unrolled assembler loops
3. Use Python conditional statements to generate code for different environments
4. Use Python subroutines with parameters to generate parameterized code chunks
