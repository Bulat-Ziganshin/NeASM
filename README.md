```
A boy writes in C++.
A man writes in assembler.
A real man writes his very own assembler.
A woman goes into the grocery and buys a faster computer.
```

## Python-based High-Level Assembler

There are many ways to implement High-Level Assembler.
This project resembles [PL/I preprocessor], [Crystal], [MetaLua], [Perl ASM], and [Mojo].

Here, Python is used as a compile-time meta-language, employing its loops, subroutines, ifs, variables...
for dynamic generation of resulting assembler code.

Even the current minimalist implementation allows one to employ the full power of Python to generate assembler code:
- assign readable names to registers, constants, and memory locations
- use Python loops to unroll assembler loops
- use Python conditional statements for conditional compilation
- use Python subroutines with parameters as macro/template/generics facility

... but we all know that macro-assemblers provide similar features, even if with unusual syntax.
The real power of NeASM comes from the fact that it's a small Python application (< 1000 LOC),
so everyone can extend it with new features.
See e.g. [primitive code reordering ](#primitive-code-reordering)
that was [implemented][reordering implementation] in 10 LOC (!!!).

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

E.g., this code (see [example2.neasm]):

```
%for n in range(4):
  paddq xmm{n+1}, xmm{n}
```

is auto-translated into this Python [code][example2.intermediate]:

```python
for n in range(4):
  asm("paddq xmm" + str(n+1) + ", xmm" + str(n) + "")
```

and executed by Python to generate this final assembler code (see [example2.asm]):
```asm
paddq xmm1, xmm0
paddq xmm2, xmm1
paddq xmm3, xmm2
paddq xmm4, xmm3
```

This means that eventually, we will be able to write the usual assembler code,
extended with Python as a meta-language to generate repetitive code,
auto-alloc registers, and perform user-defined code transformations.

---

You can also switch between asm and Python modes using `%asm` and `%python` pseudo-commands
(and then use '%' to invert the mode for a single line) - see [example][asm-python-pseudo-commands].

You can use `neasm.equ(id, replacement)` library call
or equivalent `id EQU replacement` asm pseudo-command
to define textual replacements that doesn't need braces around:
```
%equ('offs', 42)
addr equ EBX
value EQU EAX
mov [addr+offs], value
```

translated into `mov [EBX+42], EAX`.

Note the difference - while `{v}` is replaced by the current contents of Python variable `v`,
EQU-defined replacements are kept in the special dictionary used only to preprocess
asm code lines. This dictionary is cleared by the `neasm.flush()` call.



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
But [the implementation][reordering implementation] took only 10 LOC (!!!),
while providing a feature that isn't supported by any
macro assembler (masm, gas, [nasm], [fasm]) I know.


### Register auto-allocation

The single most important difference between [HLL] and any [HLA]
is the automatic allocation of registers for variables.
It should take into account the lifetime of each variable,
that needs more complex program analysis than any existing [HLA] implements.

NeASM implements simple automatic register allocation,
with a variable lifetime measured as a range of source code lines,
rather than using the complete lifetime analysis.
This means that for variables, whose values persist between loop iterations,
you may need to add artificial variable references before and after the loop body.

The allocator also relies on the following "common sense" rules:
- One asm operation can't write more than one register of the same class (i.e. GPR/SIMD/mask).
- On the first variable use, we don't try to use its previous (garbage) contents.
- Together, this means that in the first line where a new variable is used,
we unconditionally write to it, while only reading any other same-class variables mentioned on this line.
Thus, we can use the same register for two variables - last-used on some line, and first-used on the same line.

Variables are declared using the following directives:
```
registers var1, var2   # these variables will be placed into 64-bit general-purpose registers
XMM_register src       # src will be placed into XMM register
YMM_register match     # match will be placed into YMM register
ZMM_register result    # result will be placed into ZMM register
```

Directive names are case-insensitive, and you can use single or plural form ("register" or "registers").
One directive can declare multiple variables, comma-separated.

Now, I'm ready to provide [code sample][var-alloc.neasm]:
```
%UNROLL = 4
REGISTERS ptr, counter, sum
mov ptr, [rsp+40]
mov counter, 16 - {UNROLL}

start:
%for n in range(UNROLL):
  %start_new_stream()
  register sum{n}
  mov sum{n}, [ptr + counter*8 + {n}*8]
  %if n==0:
    add sum{n}, counter
  %else:
    lea sum{n}, [sum{n} + counter + {n}]
  mov [ptr + counter*8 + {n}*8], sum{n}
%interleave_streams()
sub counter, {UNROLL}
jae start

# Artificially extend variables' lifetime
mov counter, counter
mov ptr, ptr
```

which [translated into][var-alloc.asm]:
```asm
mov rax, [rsp+40]
mov rdx, 16 - 4

start:
mov rbx, [rax + rdx*8 + 0*8]
mov rsi, [rax + rdx*8 + 1*8]
mov rdi, [rax + rdx*8 + 2*8]
mov rbp, [rax + rdx*8 + 3*8]
add rbx, rdx
lea rsi, [rsi + rdx + 1]
lea rdi, [rdi + rdx + 2]
lea rbp, [rbp + rdx + 3]
mov [rax + rdx*8 + 0*8], rbx
mov [rax + rdx*8 + 1*8], rsi
mov [rax + rdx*8 + 2*8], rdi
mov [rax + rdx*8 + 3*8], rbp
sub rdx, 4
jae start

mov rdx, rdx
mov rax, rax
```






[PL/I preprocessor]: https://en.wikipedia.org/wiki/PL/I_preprocessor
[Crystal]: https://crystal-lang.org/reference/1.13/syntax_and_semantics/macros/
[MetaLua]: http://lua-users.org/wiki/MetaLua
[Perl ASM]: https://github.com/openssl/openssl/blob/master/crypto/aes/asm/aesv8-armx.pl
[Mojo]: https://www.modular.com/mojo
[pyexpander]: https://pyexpander.sourceforge.io/reference-expander.html

[HLA]: https://en.wikipedia.org/wiki/High-level_assembler
[HLL]: https://en.wikipedia.org/wiki/High-level_programming_language

[nasm]: https://www.nasm.us/xdoc/2.16.03/html/nasmdoc4.html
[fasm]: https://flatassembler.net/docs.php?article=manual

[example2.neasm]: https://github.com/Bulat-Ziganshin/NeASM/blob/e242efbd308e9cbd8f0831b3386ee86dfcc1bbdc/example2.neasm#L5-L6
[example2.intermediate]: https://github.com/Bulat-Ziganshin/NeASM/blob/e242efbd308e9cbd8f0831b3386ee86dfcc1bbdc/example2.asm#L9-L10
[example2.asm]: https://github.com/Bulat-Ziganshin/NeASM/blob/e242efbd308e9cbd8f0831b3386ee86dfcc1bbdc/example2.asm#L21-L24
[asm-python-pseudo-commands]: https://github.com/Bulat-Ziganshin/NeASM/blob/967e87ab97fa1429f9262e83f36d6913b4fc4759/example2.neasm#L17-L26
[reordering implementation]: https://github.com/Bulat-Ziganshin/NeASM/commit/e242efbd308e9cbd8f0831b3386ee86dfcc1bbdc#diff-3d0faa46eb38ecc83a9d626adb745b0fb06c0d74a2a6119b88b6403670254341R18-R30

[var-alloc.neasm]: https://github.com/Bulat-Ziganshin/NeASM/blob/670d8efa8b320359bbff1bc58da09ea35bc143c5/example2.neasm#L33-L54
[var-alloc.asm]: https://github.com/Bulat-Ziganshin/NeASM/blob/670d8efa8b320359bbff1bc58da09ea35bc143c5/example2.asm#L98-L117
