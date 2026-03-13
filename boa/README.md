# Boa — Binary Operators And Variables

A compiler for the Boa language targeting x86-64 assembly. Extends the Adder compiler with `let` bindings, variable lookup, and binary arithmetic operators.

## Language

```
<expr> :=
  | <number>
  | <identifier>
  | (let ((<identifier> <expr>)+) <expr>)
  | (add1 <expr>)
  | (sub1 <expr>)
  | (+ <expr> <expr>)
  | (- <expr> <expr>)
  | (* <expr> <expr>)
```

Reserved words: `let`, `add1`, `sub1`

### Examples

| Program | Result |
|---------|--------|
| `42` | 42 |
| `(add1 (add1 (add1 3)))` | 6 |
| `(+ (* 2 3) 3)` | 9 |
| `(let ((x 5)) (+ x x))` | 10 |
| `(let ((x 5) (y 6)) (+ x y))` | 11 |
| `(let ((x 2) (y 3)) (let ((z (+ x y))) (* z z)))` | 25 |

Bindings in a `let` are sequential — each name is visible in subsequent bindings and the body. Shadowing across nested `let`s is allowed; duplicate names within a single `let` is an error.

## Building

```bash
cargo build
```

## Usage

```bash
cargo run -- <input.snek> <output.s>      # compile a Boa program to assembly
make test/<name>.run                       # assemble + link a single test
make test                                  # build and run all tests
```

## Project Structure

```
boa/
├── src/main.rs        # compiler: parser + code generator
├── runtime/start.rs   # Rust runtime that calls our_code_starts_here and prints the result
├── test/              # .snek source files
└── Makefile
```

## Implementation Notes

**Stack layout** — variables are stored at negative offsets from `RSP`:

```
[rsp - 16]  first binding  (si = 2)
[rsp - 24]  second binding (si = 3)
...
```

Slot 1 (`[rsp - 8]`) is reserved for future use.

**Binary operations** — the left operand is spilled to the stack before evaluating the right, so nested expressions don't clobber each other. Subtraction reloads the left operand into `RAX` via `RBX` to correctly compute `left - right`.

**Environment** — uses `im::HashMap` (immutable persistent map). `env.update(name, offset)` returns a new map, so nested scopes never mutate the outer environment.

## Error Messages

| Condition | Message |
|-----------|---------|
| Duplicate name in one `let` | `Duplicate binding` |
| Reference to unbound variable | `Unbound variable identifier <name>` |
| Invalid syntax | `Invalid` |
