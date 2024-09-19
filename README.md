```
A boy writes in C++.
A man writes in assembler.
A real man writes his very own assembler.
A woman goes into the grocery and buys a faster computer.
```

## Python-based High-Level Assembler

In the past, I already had an idea of making my own [High-Level Assembler][magus].
But when I started to work on (a secret project), my frustration
with modern C++ compilers went to the moon. Do you know that there is no
100% guaranteed way to ask His Majesty to generate CMOV instead of Jxx?
Or that C++ compilers don't automatically interleave commands from
different dependency chains?

Frustrated by the lack of control over generated assembler code,
I returned to the HLA idea, this time with a different approach.
Since my code is already AVX2-heavy, now I don't mind about the C incompatibility.

What I want now is a good old assembler, plus these features:
- [x] the usual macro assembler tools: conditional/looped compilation, macroses, EQUs
- [x] automatic allocation of registers for variables, a la Nvidia PTX or any HLL
- [x] the ability to interleave commands from different dependency chains
- [ ] C-style syntax, like `ax = bx; ax += bx; ax = bx+cx; ax = pmovmskb xmm1`
(in addition to the usual asm syntax)
- [ ] expression translator for things like `ax = bx*cx + (dx << 5)`,
with automatic allocation of registers for temporaries
- [ ] high-level asm operations, like proc/call, if/while

---

This project resembles [PL/I preprocessor], [Crystal], [MetaLua], [Perl ASM], and [Mojo].

We use Python as a compile-time meta-language, employing its loops, subroutines, ifs, variables...
for dynamic generation of resulting assembler code.
Even the current minimalist implementation allows one to employ the full power of Python to generate assembler code:
- assign readable names to registers, constants, and memory locations
- use Python loops to unroll assembler loops
- use Python conditional statements for conditional compilation
- use Python subroutines with parameters as macro/template/generics facility

... but we all know that macro-assemblers provide similar features, even if with unusual syntax.
The real power of NeASM comes from the fact that it's a tiny Python application (200 LOC as of now),
so everyone can extend it with new features.
See e.g. our simple [code reordering](#code-reordering)
that is [implemented][reordering implementation] in 20 LOC (!!!).



### NeASM: Python library

Recommended imports:
```python
import neasm
from registers import *
```

`neasm.asm(str1...)` call adds one ASM line to the program.
The ASM command can be passed as a single string, or as `asm(cmd,arg1,arg2...)`
in which case the ASM command is constructed as `cmd arg1, arg2...`.
All asm() arguments are auto-converted to strings via str().

`neasm.equ(id,text)` defines textual replacement and is described in the next section.

`registers` module provides variables with handy register names
to use in asm() calls, e.g. `asm("pmovmskb", eax, xmm[1])`.

Automatic register allocation:
- `myreg = neasm.alloc_reg(typ = 'r')` returns the name of a free register and marks it as used
- `myreg_list = neasm.alloc_regs(n, typ = 'r')` allocates `n` registers of the same type
- `neasm.free_reg(myreg1, myreg2...)` returns registers back to the free pool

Use typ=x/y/z to allocate an xmm/ymm/zmm register. Note that all SIMD registers are allocated from
the single pool, while all GPR registers are allocated from another pool.

Call `alloc_reg` immediately before the first use of a variable, and `free_reg` immediately
after the last use, so that the same register can be reused for other vars with non-overlapped lifetime.
When a variable value should be kept between loop iterations, you need to call `alloc_reg` before
the loop start, and `free_reg` after the loop end, to mark the variable as used
during the entire loop body. That's because the register allocator reserves a register
for the span of assembler code lines between `alloc_reg` and `free_reg` calls
and lacks any code flow analysis.

Note that the automatic register allocation via `REGISTER*` [directives](#automatic-register-allocation)
operates from the same register pool and thus can't be (easily) used in the same code section as `alloc_reg` operations.

`neasm.flush()` call prints the program assembled so far and clears all the internal
structures - you may need to execute it between code sections, in particular to clear up
the allocated registers list.



### NePP: ASM code preprocessor

You can preprocess an ASM source file with `nepp.py example2.neasm >example2.asm`.

The preprocessor translates an ASM code into a Python program that generates
the same ASM code using calls to `neasm.asm(...)`.
But on top of that, lines starting with "%" are copied as Python statements,
and texts in braces `{expr}` are evaluated as Python expressions.

E.g., this code (see [example2.neasm]):
```
%for n in range(4):
  paddq xmm{n+1}, xmm{n}
```

is auto-translated into this Python code:
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
or equivalent `id EQU replacement` NeASM directive
to define textual replacements that don't need braces around:
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



### Code reordering

We have a quick-and-dirty implementation of automatic code reordering.
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

---

Command prefix `[n]` tells the interleaver how many CPU cycles the command is executed.
For example, "[4] mov ax,[bx]" means that the delay between this and the next command
in the same stream is 4 cycles (default value is 1).
This allows the interleaver to put after a high-latency command more commands
from other streams.

This also allows more precise, semi-manual control of the interleaving.
In particular, one can use the `[0]` prefix to ensure that commands
will be issued back-to-back (and thus immediately free all registers
occupied by variables used only inside these commands).

You can find creative use of this feature in [lz_match_finder.neasm](examples/lz_match_finder.neasm),
where in the one set of streams we wrote:
```
[0] mov match_addr{n}, [hash_table + hash_row0 + {n}*8]
[9] vpcmpeqb mask_eq_bytes{n}, src_data, [dict + match_addr{n}]
```

to ensure that MOV+VPCMPEQB are placed back-to-back,
thus freeing precious GPRs allocated for `match_addr{n}`.

At the same time, we used `[9]` here to create a large 'hole' for commands
from another stream once VPCMPEQB is issued. And then we used a combination
of `[5]` and `[0]` prefixes in another stream to clamp all its commands into this 'hole':
```
[5] # Make sure that all the prefetching will take place between VPCMPEQB and the next command
%for n in range(i, i+LINE):
    [0] REGISTER prefetch_addr{n}
    [0] mov prefetch_addr{n}, [hash_table + hash_row1 + {n}*8]
    [0] prefetch [dict + prefetch_addr{n}]
    [0] prefetch [dict + prefetch_addr{n} + 31]
```

Of course, the code reordering implemented so far is primitive,
and we hardwired its support into the NeASM core.
But [the implementation][reordering implementation] took only 20 LOC (!!!),
while providing a feature that isn't supported by any
macro assembler ([masm], [gas], [nasm], [fasm]) I know.



### Automatic register allocation

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

Directive names are case-insensitive, and you can use single or plural forms ("register" or "registers").
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



### Larger examples

Browse [example3.neasm](examples/example3.neasm) (and [generated code](examples/example3.asm))
and [lz_match_finder.neasm](examples/lz_match_finder.neasm) (and [generated code](examples/lz_match_finder.asm))
for larger examples using all the NeASM features - Python-based metaprogramming,
automatic register allocation, and sophisticated code reordering.

Note that these examples have similar source code,
but the subtle difference in control directives (in particular, "[n]" command prefixes)
results in a dramatically different command order in the generated code.







[magus]: https://github.com/Bulat-Ziganshin/magus

[PL/I preprocessor]: https://en.wikipedia.org/wiki/PL/I_preprocessor
[Crystal]: https://crystal-lang.org/reference/1.13/syntax_and_semantics/macros/
[MetaLua]: http://lua-users.org/wiki/MetaLua
[Perl ASM]: https://github.com/openssl/openssl/blob/master/crypto/aes/asm/aesv8-armx.pl
[Mojo]: https://www.modular.com/mojo
[pyexpander]: https://pyexpander.sourceforge.io/reference-expander.html

[HLA]: https://en.wikipedia.org/wiki/High-level_assembler
[HLL]: https://en.wikipedia.org/wiki/High-level_programming_language

[masm]: https://learn.microsoft.com/en-us/cpp/assembler/masm/directives-reference
[gas]:  https://sourceware.org/binutils/docs/as/Pseudo-Ops.html
[nasm]: https://www.nasm.us/xdoc/2.16.03/html/nasmdoc4.html
[fasm]: https://flatassembler.net/docs.php?article=manual

[example2.neasm]: https://github.com/Bulat-Ziganshin/NeASM/blob/15a5e881342e1044b712d768c689f9a7e05740ef/example2.neasm
[example2.asm]: https://github.com/Bulat-Ziganshin/NeASM/blob/15a5e881342e1044b712d768c689f9a7e05740ef/example2.asm
[asm-python-pseudo-commands]: https://github.com/Bulat-Ziganshin/NeASM/blob/967e87ab97fa1429f9262e83f36d6913b4fc4759/example2.neasm#L17-L26
[reordering implementation]: https://github.com/Bulat-Ziganshin/NeASM/blob/fb4d781492d1f5b49a3cbae045ae802e28db7e98/neasm/neasm.py#L90-L122

[var-alloc.neasm]: https://github.com/Bulat-Ziganshin/NeASM/blob/5aa007a73d21d2c9c58cfffd00c234e2ff0fc571/examples/example2.neasm#L33-L55
[var-alloc.asm]: https://github.com/Bulat-Ziganshin/NeASM/blob/5aa007a73d21d2c9c58cfffd00c234e2ff0fc571/examples/example2.asm#L99-L126
