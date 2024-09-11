## Python-based High-Level Assembler

There are many ways to implement High-Level Assembler.
This project resembles
- [Perl ASM](https://github.com/openssl/openssl/blob/master/crypto/aes/asm/aesv8-armx.pl)
- [Mojo](https://www.modular.com/mojo)
- [Crystal](https://crystal-lang.org/reference/1.13/syntax_and_semantics/macros/)

Here, Python is used as a compile-time meta-language, employing its loops, subroutines, ifs, variables...
for dynamic generation of resulting assembler code.

Even the current minimalist implementation allows one to employ the full power of Python to generate assembler code:
1. Assign readable names to registers, constants, and memory locations
2. Use Python loops to write unrolled assembler loops
3. Use Python conditional statements to generate code for different environments
4. Use Python subroutines with parameters to generate parameterized code chunks

... but we all know that macro-assemblers provide similar features, even if with unusual syntax.
The real power of NeASM is that it's a regular Python application, that allows everyone
to extend it with new features.

The features that I currently plan to implement:
- [x] ASM code preprocessing
- [ ] virtual registers (a-la PTX)
- [ ] automatic code reordering (to interleave dependency chains)
- [ ] C-style syntax in assembler code, e.g. `ax += bx`
- [ ] formula translator, e.g. `ax = bx*cx + (dx << 5)`


# ASM code preprocessing

You can preprocess an ASM source file with `python.exe preprocessor.py example2.neasm >example2.asm`.

The preprocessor translates an ASM code into a Python program that generates
the same ASM code using calls to the "asm" function from NeASM.
But on top of that, lines starting with "%" are copied as Python statements,
and texts in braces `{expr}` are copied as Python expressions.

E.g., this code (see [example2.neasm](example2.neasm)):
```
%for n in range(4):
  paddq {xmm[n+1]}, {xmm[n]}
```

is auto-translated into Python code:
```python
for n in range(4):
  asm("paddq " + xmm[n+1] + ", " + xmm[n] + "")
```

and executed by Python to generate the final assembler code (see [example2.asm](example2.asm)):
```asm
paddq xmm1, xmm0
paddq xmm2, xmm1
paddq xmm3, xmm2
paddq xmm4, xmm3
```

This means that eventually, we will be able to write the usual assembler code,
extended with Python as a meta-language to generate repetitive code,
auto-alloc registers, and perform user-defined code transformations.
