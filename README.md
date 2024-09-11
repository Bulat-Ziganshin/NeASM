## Python-based High-Level Assembler

There are many ways to implement High-Level Assembler.
This project resembles
[PL/I preprocessor](https://en.wikipedia.org/wiki/PL/I_preprocessor),
[Crystal](https://crystal-lang.org/reference/1.13/syntax_and_semantics/macros/),
[Perl ASM](https://github.com/openssl/openssl/blob/master/crypto/aes/asm/aesv8-armx.pl), and
[Mojo](https://www.modular.com/mojo).

Here, Python is used as a compile-time meta-language, employing its loops, subroutines, ifs, variables...
for dynamic generation of resulting assembler code.

Even the current minimalist implementation allows one to employ the full power of Python to generate assembler code:
1. Assign readable names to registers, constants, and memory locations
2. Use Python loops to unroll assembler loops
3. Use Python conditional statements for conditional compilation
4. Use Python subroutines with parameters as macro/template/generics facility

... but we all know that macro-assemblers provide similar features, even if with unusual syntax.
The real power of NeASM comes from the fact that it's a tiny Python application (< 100 LOC!),
so everyone can extend it with new features.
See e.g. [primitive code reordering ](#primitive-code-reordering)
that was implemented in 10 LOC (!!!).

The features that I currently plan to implement:
- [x] ASM code preprocessing
- [ ] virtual registers (a-la PTX)
- [ ] automatic code reordering (to interleave dependency chains)
- [ ] C-style syntax in assembler code, e.g. `ax += bx`
- [ ] formula translator, e.g. `ax = bx*cx + (dx << 5)`


### ASM code preprocessing

You can preprocess an ASM source file with `nepp.py example2.neasm >example2.asm`.

The preprocessor translates an ASM code into a Python program that generates
the same ASM code using calls to the "asm" function from NeASM.
But on top of that, lines starting with "%" are copied as Python statements,
and texts in braces `{expr}` are copied as Python expressions.

E.g., this code (see [example2.neasm](example2.neasm)):
```
%for n in range(4):
  paddq xmm{n+1}, xmm{n}
```

is auto-translated into this Python code:
```python
for n in range(4):
  asm("paddq xmm" + str(n+1) + ", xmm" + str(n) + "")
```

and executed by Python to generate this final assembler code (see [example2.asm](example2.asm)):
```asm
paddq xmm1, xmm0
paddq xmm2, xmm1
paddq xmm3, xmm2
paddq xmm4, xmm3
```

This means that eventually, we will be able to write the usual assembler code,
extended with Python as a meta-language to generate repetitive code,
auto-alloc registers, and perform user-defined code transformations.



### Primitive code reordering

We have a primitive implementation of automatic code reordering.
It just interleaves commands from multiple command streams that you created.

Let's look at an example. This NeASM code:
```
%for n in range(8,10):
  mov r{n}, [ebp+{n*8}]
  vmovdqu ymm{n}, [r{n}]
```

isn't reordered and generates the following asm code:
```asm
mov r8, [ebp+64]
vmovdqu ymm8, [r8]
mov r9, [ebp+72]
vmovdqu ymm9, [r9]
```

By adding two extra calls:
```
%for n in range(8,10):
  %start_new_stream()
  mov r{n}, [ebp+{n*8}]
  vmovdqu ymm{n}, [r{n}]
%interleave_streams()
```

we get commands from different loop iterations interleaved:
```asm
mov r8, [ebp+64]
mov r9, [ebp+72]
vmovdqu ymm8, [r8]
vmovdqu ymm9, [r9]
```

Each start_new_stream() call starts a new command stream, so this loop
creates two extra command streams. On the interleave_streams() call,
commands from all extra streams are interleaved and added to the main
command stream.

Of course, the code reordering implemented here is very primitive,
and we hardwired its support into the NeASM core.
But the implementation took only 10 LOC (!!!),
while providing a feature that isn't supported by any
macro assembler (masm, gas, fasm, nasm) I know.
