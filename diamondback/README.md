# Diamondback Compiler

A compiler for the Diamondback language — an extension of Cobra with **function definitions and calls**.

## Language Features

- Numbers, booleans (`true`/`false`), `input`
- `let`, `if`, `block`, `loop`, `break`, `set!`
- Arithmetic & comparisons: `+ - * < > <= >= =`
- Unary: `add1 sub1 negate isnum isbool`
- **`print`** — prints a value and returns it
- **`(fun (name param*) body)`** — function definitions
- **`(name arg*)`** — function calls

## Calling Convention

This compiler uses a **callee-saves rbp** convention compatible with System V AMD64:

```
Higher addresses
───────────────
rbp+24  | arg 2       |   (3rd arg if present)
rbp+16  | arg 1       |   (1st arg always here)
rbp+8   | return addr |   (pushed by `call`)
rbp     | saved rbp   |   ← rbp points here after prologue
rbp-8   | local 1     |   (1st let binding inside function)
rbp-16  | local 2     |
Lower addresses
```

**Caller** (right-to-left push):
```asm
mov rax, <argN>   ; last arg
push rax
...
mov rax, <arg1>   ; first arg
push rax
call _fun_name
add rsp, N*8      ; caller cleans up
```

**Callee** (standard prologue/epilogue):
```asm
_fun_name:
  push rbp
  mov  rbp, rsp
  sub  rsp, 1024    ; room for locals
  ; ... body ...
  add  rsp, 1024
  pop  rbp
  ret
```

## Building

```bash
# Build the compiler
cargo build

# Compile a single .snek file to assembly
cargo run -- test/factorial.snek test/factorial.s

# Assemble and link into a runnable binary
nasm -f macho64 test/factorial.s -o runtime/our_code.o
ar rcs runtime/libour_code.a runtime/our_code.o
rustc --target x86_64-apple-darwin -L runtime/ runtime/start.rs -o test/factorial.run

# Run it
./test/factorial.run
```

## Running Tests

```bash
# Run all 27 passing tests
make test

# Run compile-error tests (compiler should reject these)
make test-errors

# Clean build artifacts
make clean
```

## Example Programs

### Factorial
```scheme
(fun (factorial n)
  (if (= n 1)
    1
    (* n (factorial (- n 1)))))
(factorial 5)      ; → 120
```

### Fibonacci
```scheme
(fun (fib n)
  (if (<= n 1)
    n
    (+ (fib (- n 1)) (fib (- n 2)))))
(fib 10)           ; → 55
```

### Mutual Recursion
```scheme
(fun (my_even n) (if (= n 0) true  (my_odd  (- n 1))))
(fun (my_odd  n) (if (= n 0) false (my_even (- n 1))))
(my_even 4)        ; → true
```

### Print
```scheme
(fun (double x) (+ x x))
(print (double 7)) ; prints 14, returns 14
```

## Error Handling

The compiler panics (exits non-zero) for:
- Calling an undefined function
- Wrong number of arguments
- Duplicate parameter names
- Unbound variables

Runtime type errors (e.g. adding a boolean) call `snek_error` which prints `invalid argument` and exits.

## Value Representation

| Value   | Encoding  |
|---------|-----------|
| Number n | `n << 1` (LSB = 0) |
| `true`  | `3` (0b11) |
| `false` | `1` (0b01) |

## What to Submit

- `src/main.rs` — the compiler
- `runtime/start.rs` — the runtime (with `snek_print`)
- `Makefile` — build and test automation
- `test/` — all `.snek` + `.expected` files (27 passing + 3 error tests)
- This `README.md`
