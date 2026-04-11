// Diamondback Compiler — src/main.rs
//
// Tagged value representation (same as Cobra):
//   Numbers  → (n << 1)          LSB = 0
//   true     → 3  (0b11)         LSB = 1
//   false    → 1  (0b01)         LSB = 1
//
// New in Diamondback:
//   - Program struct:  zero-or-more function definitions + one main expression
//   - Definition struct: (fun (<name> <param>*) <body>)
//   - Expr::Call(name, args)
//   - Expr::Print(expr)  — built-in print op
//
// Calling convention (System V AMD64, simplified):
//   Caller pushes args right-to-left, then calls.
//   Callee: push rbp / mov rbp, rsp / sub rsp, N / … / add rsp, N / pop rbp / ret
//   1st arg at [rbp+16], 2nd at [rbp+24], …
//
// CRITICAL — all local temporaries are rbp-relative ([rbp - si*8]).
//   rbp is pinned to the frame top and never changes within a function body;
//   therefore push/call instructions cannot overwrite our saved intermediates.
//   If we used rsp-relative locals, every push/call would silently corrupt them.

use sexp::Atom::*;
use sexp::*;
use std::collections::{HashMap, HashSet};
use std::env;
use std::fs::File;
use std::io::prelude::*;

// ─────────────────────────── AST ─────────────────────────────────────────────

#[derive(Debug, Clone)]
enum UnOp {
    Add1,
    Sub1,
    Negate,
    IsNum,
    IsBool,
    Print,
}

#[derive(Debug, Clone)]
enum BinOp {
    Plus,
    Minus,
    Times,
    Less,
    Greater,
    LessEq,
    GreaterEq,
    Equal,
}

#[derive(Debug, Clone)]
enum Expr {
    Num(i64),
    Bool(bool),
    Input,
    Var(String),
    Let(Vec<(String, Expr)>, Box<Expr>),
    UnOp(UnOp, Box<Expr>),
    BinOp(BinOp, Box<Expr>, Box<Expr>),
    If(Box<Expr>, Box<Expr>, Box<Expr>),
    Block(Vec<Expr>),
    Loop(Box<Expr>),
    Break(Box<Expr>),
    Set(String, Box<Expr>),
    Call(String, Vec<Expr>),
}

#[derive(Debug, Clone)]
struct Definition {
    name: String,
    params: Vec<String>,
    body: Expr,
}

#[derive(Debug)]
struct Program {
    defns: Vec<Definition>,
    main: Expr,
}

// ─────────────────────────── Keyword / reserved helpers ──────────────────────

const RESERVED: &[&str] = &[
    "let", "if", "block", "loop", "break", "set!", "true", "false", "input",
    "add1", "sub1", "negate", "isnum", "isbool", "print",
    "+", "-", "*", "<", ">", "<=", ">=", "=",
    "fun",
];

fn is_reserved(s: &str) -> bool {
    RESERVED.contains(&s)
}

// ─────────────────────────── Parser ──────────────────────────────────────────

fn parse_bind(s: &Sexp) -> (String, Expr) {
    match s {
        Sexp::List(vec) => match &vec[..] {
            [Sexp::Atom(S(name)), e] => {
                if is_reserved(name) {
                    panic!("Invalid: reserved word used as binding name: {name}");
                }
                (name.clone(), parse_expr(e))
            }
            _ => panic!("Invalid binding form"),
        },
        _ => panic!("Invalid binding form"),
    }
}

fn parse_expr(s: &Sexp) -> Expr {
    match s {
        Sexp::Atom(I(n)) => Expr::Num(i64::try_from(*n).expect("Integer overflow in literal")),
        Sexp::Atom(S(name)) => match name.as_str() {
            "true"  => Expr::Bool(true),
            "false" => Expr::Bool(false),
            "input" => Expr::Input,
            other   => {
                if is_reserved(other) {
                    panic!("Invalid: reserved word used as identifier: {other}");
                }
                Expr::Var(other.to_string())
            }
        },

        Sexp::List(vec) => match &vec[..] {
            [Sexp::Atom(S(op)), e] if op == "add1"   => Expr::UnOp(UnOp::Add1,   Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "sub1"   => Expr::UnOp(UnOp::Sub1,   Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "negate" => Expr::UnOp(UnOp::Negate, Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "isnum"  => Expr::UnOp(UnOp::IsNum,  Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "isbool" => Expr::UnOp(UnOp::IsBool, Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "print"  => Expr::UnOp(UnOp::Print,  Box::new(parse_expr(e))),

            [Sexp::Atom(S(op)), e1, e2] if op == "+"  => Expr::BinOp(BinOp::Plus,      Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "-"  => Expr::BinOp(BinOp::Minus,     Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "*"  => Expr::BinOp(BinOp::Times,     Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "<"  => Expr::BinOp(BinOp::Less,      Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == ">"  => Expr::BinOp(BinOp::Greater,   Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "<=" => Expr::BinOp(BinOp::LessEq,    Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == ">=" => Expr::BinOp(BinOp::GreaterEq, Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "="  => Expr::BinOp(BinOp::Equal,     Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),

            [Sexp::Atom(S(op)), cond, then_e, else_e] if op == "if" =>
                Expr::If(Box::new(parse_expr(cond)), Box::new(parse_expr(then_e)), Box::new(parse_expr(else_e))),

            [Sexp::Atom(S(op)), rest @ ..] if op == "block" => {
                if rest.is_empty() { panic!("Invalid: block requires at least one expression"); }
                Expr::Block(rest.iter().map(parse_expr).collect())
            }

            [Sexp::Atom(S(op)), body] if op == "loop" => Expr::Loop(Box::new(parse_expr(body))),
            [Sexp::Atom(S(op)), e] if op == "break"   => Expr::Break(Box::new(parse_expr(e))),

            [Sexp::Atom(S(op)), Sexp::Atom(S(name)), e] if op == "set!" => {
                if is_reserved(name) {
                    panic!("Invalid: reserved word used as set! target: {name}");
                }
                Expr::Set(name.clone(), Box::new(parse_expr(e)))
            }

            [Sexp::Atom(S(op)), Sexp::List(bindings), body] if op == "let" => {
                if bindings.is_empty() {
                    panic!("Invalid: let requires at least one binding");
                }
                let mut seen = HashSet::new();
                let mut parsed = Vec::new();
                for b in bindings {
                    let (name, expr) = parse_bind(b);
                    if !seen.insert(name.clone()) {
                        panic!("Duplicate binding: {name}");
                    }
                    parsed.push((name, expr));
                }
                Expr::Let(parsed, Box::new(parse_expr(body)))
            }

            // Function call: (name arg*)
            [Sexp::Atom(S(name)), args @ ..] if !is_reserved(name) => {
                Expr::Call(name.clone(), args.iter().map(parse_expr).collect())
            }

            _ => panic!("Invalid expression: {s}"),
        },

        _ => panic!("Invalid expression: {s}"),
    }
}

fn try_parse_defn(s: &Sexp) -> Option<Definition> {
    match s {
        Sexp::List(vec) => match &vec[..] {
            [Sexp::Atom(S(kw)), Sexp::List(sig), body] if kw == "fun" => {
                match &sig[..] {
                    [Sexp::Atom(S(name)), params @ ..] => {
                        if is_reserved(name) {
                            panic!("Invalid function name (reserved): {name}");
                        }
                        let param_names: Vec<String> = params.iter().map(|p| match p {
                            Sexp::Atom(S(pname)) => {
                                if is_reserved(pname) {
                                    panic!("Invalid parameter name (reserved): {pname}");
                                }
                                pname.clone()
                            }
                            _ => panic!("Invalid parameter in function definition"),
                        }).collect();
                        let mut seen = HashSet::new();
                        for p in &param_names {
                            if !seen.insert(p.clone()) {
                                panic!("Duplicate parameter name: {p}");
                            }
                        }
                        Some(Definition {
                            name: name.clone(),
                            params: param_names,
                            body: parse_expr(body),
                        })
                    }
                    _ => panic!("Invalid function signature"),
                }
            }
            _ => None,
        },
        _ => None,
    }
}

fn parse_program(s: &Sexp) -> Program {
    let items: Vec<&Sexp> = match s {
        Sexp::List(v) => v.iter().collect(),
        _ => return Program { defns: vec![], main: parse_expr(s) },
    };

    let mut defns = vec![];
    let mut main_expr: Option<Expr> = None;

    for item in &items {
        if let Some(d) = try_parse_defn(item) {
            if main_expr.is_some() {
                panic!("Function definition after main expression");
            }
            defns.push(d);
        } else {
            if main_expr.is_some() {
                panic!("Multiple main expressions");
            }
            main_expr = Some(parse_expr(item));
        }
    }

    Program {
        defns,
        main: main_expr.expect("No main expression found"),
    }
}

// ─────────────────────────── Code Generation ─────────────────────────────────

fn new_label(ctr: &mut i32, prefix: &str) -> String {
    *ctr += 1;
    format!("{}_{}", prefix, ctr)
}

// ── rbp-relative type-check helpers ──────────────────────────────────────────
//
// All intermediate values are saved at [rbp - si*8].  rbp is pinned for the
// lifetime of a stack frame; push/call cannot disturb it.

/// Check rax is a number (LSB == 0); jump to err if not.
fn check_is_num(err: &str) -> Vec<String> {
    vec![
        "  mov rbx, rax".to_string(),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {err}"),
    ]
}

/// Check [rbp - saved_off] is a number.
fn check_saved_is_num(saved_off: i32, err: &str) -> Vec<String> {
    vec![
        format!("  mov rbx, [rbp - {saved_off}]"),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {err}"),
    ]
}

/// Check rax and [rbp - saved_off] have the same type tag.
fn check_same_type(saved_off: i32, err: &str) -> Vec<String> {
    vec![
        "  mov rbx, rax".to_string(),
        format!("  xor rbx, [rbp - {saved_off}]"),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {err}"),
    ]
}

// ── Variable location ─────────────────────────────────────────────────────────
//
//  Local(off): rbp-relative local slot — [rbp - off]   (off = si * 8 > 0)
//  Param(off): parameter passed by caller — [rbp + off] (off = 16 + i*8 > 0)
//
// rbp-relative locals are safe because rbp is pinned; push/call only move rsp.

#[derive(Debug, Clone)]
enum VarLoc {
    Local(i32), // address: rbp - off
    Param(i32), // address: rbp + off
}

type Env = HashMap<String, VarLoc>;

fn load_var(loc: &VarLoc) -> String {
    match loc {
        VarLoc::Local(off) => format!("  mov rax, [rbp - {off}]"),
        VarLoc::Param(off) => format!("  mov rax, [rbp + {off}]"),
    }
}

fn store_var(loc: &VarLoc) -> String {
    match loc {
        VarLoc::Local(off) => format!("  mov [rbp - {off}], rax"),
        VarLoc::Param(off) => format!("  mov [rbp + {off}], rax"),
    }
}

// ── Arity validation ──────────────────────────────────────────────────────────

fn validate_call(name: &str, args: &[Expr], defns: &[Definition]) {
    let defn = defns.iter().find(|d| d.name == name)
        .unwrap_or_else(|| panic!("Undefined function: {name}"));
    if args.len() != defn.params.len() {
        panic!(
            "Wrong number of arguments for '{}': expected {}, got {}",
            name, defn.params.len(), args.len()
        );
    }
}

// ─────────────────────────── compile_expr ────────────────────────────────────
//
// si  : next free local slot index (1-based, offset = si*8).
//        Locals live at [rbp - si*8].
// env : maps name → VarLoc.
// All binary intermediates and let bindings use rbp-relative slots.

fn compile_expr(
    e: &Expr,
    si: i32,
    env: &Env,
    label_ctr: &mut i32,
    break_target: &Option<String>,
    defns: &[Definition],
) -> Vec<String> {
    let err_label = "_throw_error";

    match e {
        // ── Literals ──────────────────────────────────────────────────────────
        Expr::Num(n)  => vec![format!("  mov rax, {}", n << 1)],
        Expr::Bool(b) => vec![format!("  mov rax, {}", if *b { 3i64 } else { 1i64 })],
        Expr::Input   => vec!["  mov rax, rdi".to_string()],

        // ── Variable access ───────────────────────────────────────────────────
        Expr::Var(name) => match env.get(name) {
            Some(loc) => vec![load_var(loc)],
            None      => panic!("Unbound variable: {name}"),
        },

        // ── Mutation ──────────────────────────────────────────────────────────
        Expr::Set(name, val) => {
            let loc = env.get(name)
                .unwrap_or_else(|| panic!("Unbound variable in set!: {name}"))
                .clone();
            let mut instrs = compile_expr(val, si, env, label_ctr, break_target, defns);
            instrs.push(store_var(&loc));
            instrs
        }

        // ── Unary ops ─────────────────────────────────────────────────────────
        Expr::UnOp(op, sub) => {
            let mut instrs = compile_expr(sub, si, env, label_ctr, break_target, defns);
            match op {
                UnOp::Add1   => { instrs.extend(check_is_num(err_label)); instrs.push("  add rax, 2".to_string()); }
                UnOp::Sub1   => { instrs.extend(check_is_num(err_label)); instrs.push("  sub rax, 2".to_string()); }
                UnOp::Negate => { instrs.extend(check_is_num(err_label)); instrs.push("  neg rax".to_string()); }
                UnOp::IsNum  => {
                    instrs.push("  and rax, 1".to_string());
                    instrs.push("  cmp rax, 0".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    instrs.push("  sete al".to_string());
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
                UnOp::IsBool => {
                    instrs.push("  and rax, 1".to_string());
                    instrs.push("  cmp rax, 1".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    instrs.push("  sete al".to_string());
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
                UnOp::Print => {
                    // snek_print(rdi) -> rax; System V ABI.
                    // sub/add rsp by 8 to maintain 16-byte alignment around the call.
                    instrs.push("  mov rdi, rax".to_string());
                    instrs.push("  sub rsp, 8".to_string());
                    instrs.push("  call _snek_print".to_string());
                    instrs.push("  add rsp, 8".to_string());
                }
            }
            instrs
        }

        // ── Binary ops ────────────────────────────────────────────────────────
        //
        // Intermediate (left operand) is saved at [rbp - saved_off].
        // rbp doesn't change, so push/call in the right-side evaluation
        // cannot overwrite this slot.
        Expr::BinOp(op, left, right) => {
            let saved_off = si * 8;                 // [rbp - saved_off]
            let mut instrs = compile_expr(left, si, env, label_ctr, break_target, defns);
            instrs.push(format!("  mov [rbp - {saved_off}], rax"));  // save left
            instrs.extend(compile_expr(right, si + 1, env, label_ctr, break_target, defns));
            // rax = right,  [rbp - saved_off] = left

            match op {
                BinOp::Plus | BinOp::Minus | BinOp::Times => {
                    instrs.extend(check_is_num(err_label));
                    instrs.extend(check_saved_is_num(saved_off, err_label));
                    match op {
                        BinOp::Plus  => {
                            instrs.push(format!("  add rax, [rbp - {saved_off}]"));
                        }
                        BinOp::Minus => {
                            // result = left - right
                            instrs.push("  mov rbx, rax".to_string());
                            instrs.push(format!("  mov rax, [rbp - {saved_off}]"));
                            instrs.push("  sub rax, rbx".to_string());
                        }
                        BinOp::Times => {
                            // (2n) * (2m) >> 1 = 2*(n*m) — tagged result
                            instrs.push("  sar rax, 1".to_string());
                            instrs.push(format!("  imul rax, [rbp - {saved_off}]"));
                        }
                        _ => unreachable!(),
                    }
                }

                BinOp::Less | BinOp::Greater | BinOp::LessEq | BinOp::GreaterEq => {
                    instrs.extend(check_is_num(err_label));
                    instrs.extend(check_saved_is_num(saved_off, err_label));
                    instrs.push("  mov rbx, rax".to_string());
                    instrs.push(format!("  mov rax, [rbp - {saved_off}]"));
                    instrs.push("  cmp rax, rbx".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    let setcc = match op {
                        BinOp::Less      => "setl",
                        BinOp::Greater   => "setg",
                        BinOp::LessEq    => "setle",
                        BinOp::GreaterEq => "setge",
                        _ => unreachable!(),
                    };
                    instrs.push(format!("  {setcc} al"));
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }

                BinOp::Equal => {
                    instrs.extend(check_same_type(saved_off, err_label));
                    instrs.push(format!("  cmp rax, [rbp - {saved_off}]"));
                    instrs.push("  mov rax, 0".to_string());
                    instrs.push("  sete al".to_string());
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
            }
            instrs
        }

        // ── Let ───────────────────────────────────────────────────────────────
        Expr::Let(bindings, body) => {
            let mut instrs = Vec::new();
            let mut env2 = env.clone();
            let mut cur_si = si;
            for (name, val_expr) in bindings {
                instrs.extend(compile_expr(val_expr, cur_si, &env2, label_ctr, break_target, defns));
                let off = cur_si * 8;
                instrs.push(format!("  mov [rbp - {off}], rax")); // rbp-relative save
                env2.insert(name.clone(), VarLoc::Local(off));
                cur_si += 1;
            }
            instrs.extend(compile_expr(body, cur_si, &env2, label_ctr, break_target, defns));
            instrs
        }

        // ── If ────────────────────────────────────────────────────────────────
        Expr::If(cond, then_e, else_e) => {
            let else_lbl = new_label(label_ctr, "if_else");
            let end_lbl  = new_label(label_ctr, "if_end");
            let mut instrs = compile_expr(cond, si, env, label_ctr, break_target, defns);
            instrs.push("  cmp rax, 1".to_string()); // false == 1
            instrs.push(format!("  je {else_lbl}"));
            instrs.extend(compile_expr(then_e, si, env, label_ctr, break_target, defns));
            instrs.push(format!("  jmp {end_lbl}"));
            instrs.push(format!("{else_lbl}:"));
            instrs.extend(compile_expr(else_e, si, env, label_ctr, break_target, defns));
            instrs.push(format!("{end_lbl}:"));
            instrs
        }

        // ── Block ─────────────────────────────────────────────────────────────
        Expr::Block(exprs) => {
            let mut instrs = Vec::new();
            for expr in exprs {
                instrs.extend(compile_expr(expr, si, env, label_ctr, break_target, defns));
            }
            instrs
        }

        // ── Loop / Break ──────────────────────────────────────────────────────
        Expr::Loop(body) => {
            let start = new_label(label_ctr, "loop_start");
            let end   = new_label(label_ctr, "loop_end");
            let mut instrs = vec![format!("{start}:")];
            instrs.extend(compile_expr(body, si, env, label_ctr, &Some(end.clone()), defns));
            instrs.push(format!("  jmp {start}"));
            instrs.push(format!("{end}:"));
            instrs
        }

        Expr::Break(val) => match break_target {
            Some(lbl) => {
                let mut instrs = compile_expr(val, si, env, label_ctr, break_target, defns);
                instrs.push(format!("  jmp {lbl}"));
                instrs
            }
            None => panic!("break used outside of a loop"),
        },

        // ── Function call ─────────────────────────────────────────────────────
        //
        // Caller convention: push args right-to-left, `call`, then clean up.
        //
        // Because we use rbp-relative locals, the push instructions that set
        // up arguments go BELOW rsp (which is already 1024 bytes below rbp)
        // and cannot overwrite any of our local slots.
        Expr::Call(name, args) => {
            validate_call(name, args, defns);
            let mut instrs = Vec::new();

            // Push arguments right-to-left.
            // Each arg eval uses the same `si` as the parent; its temporaries
            // go into [rbp - si*8], [rbp - (si+1)*8], …  These slots are
            // already "above" (higher address than) rsp, so the subsequent
            // push cannot corrupt them.
            for arg in args.iter().rev() {
                instrs.extend(compile_expr(arg, si, env, label_ctr, break_target, defns));
                instrs.push("  push rax".to_string());
            }

            instrs.push(format!("  call _fun_{name}"));

            if !args.is_empty() {
                instrs.push(format!("  add rsp, {}", args.len() * 8));
            }

            instrs
        }
    }
}

// ─────────────────────────── Function def compilation ────────────────────────

fn compile_defn(defn: &Definition, label_ctr: &mut i32, defns: &[Definition]) -> Vec<String> {
    // Build environment: params at [rbp + 16], [rbp + 24], …
    let mut env: Env = HashMap::new();
    for (i, param) in defn.params.iter().enumerate() {
        env.insert(param.clone(), VarLoc::Param(16 + (i as i32) * 8));
    }

    // Locals start at si=1 → [rbp - 8].
    let body = compile_expr(&defn.body, 1, &env, label_ctr, &None, defns);

    let mut out = Vec::new();
    out.push(format!("_fun_{}:", defn.name));
    // Prologue: pin rbp, reserve local area.
    out.push("  push rbp".to_string());
    out.push("  mov rbp, rsp".to_string());
    out.push("  sub rsp, 1024".to_string());
    out.extend(body);
    // Epilogue: restore stack and return.
    out.push("  add rsp, 1024".to_string());
    out.push("  pop rbp".to_string());
    out.push("  ret".to_string());
    out
}

// ─────────────────────────── Program compilation ─────────────────────────────

fn compile_program(prog: &Program) -> String {
    let mut label_ctr = 0i32;
    let mut lines: Vec<String> = Vec::new();

    lines.push("section .text".to_string());
    lines.push("extern _snek_error".to_string());
    lines.push("extern _snek_print".to_string());
    lines.push("global _our_code_starts_here".to_string());

    // Compile function definitions.
    for defn in &prog.defns {
        lines.push(String::new());
        lines.extend(compile_defn(defn, &mut label_ctr, &prog.defns));
    }

    // Main entry point — same prologue pattern as function defs so that
    // rbp-relative local addressing works everywhere.
    lines.push(String::new());
    lines.push("_our_code_starts_here:".to_string());
    lines.push("  push rbp".to_string());
    lines.push("  mov rbp, rsp".to_string());
    lines.push("  sub rsp, 1024".to_string());

    let main_body = compile_expr(
        &prog.main,
        1,
        &HashMap::new(),
        &mut label_ctr,
        &None,
        &prog.defns,
    );
    lines.extend(main_body);

    lines.push("  add rsp, 1024".to_string());
    lines.push("  pop rbp".to_string());
    lines.push("  ret".to_string());

    // Shared runtime-error trampoline.
    lines.push(String::new());
    lines.push("_throw_error:".to_string());
    lines.push("  mov rdi, 1".to_string());
    lines.push("  call _snek_error".to_string());
    lines.push("  ret".to_string());

    lines.join("\n")
}

// ─────────────────────────── Main ────────────────────────────────────────────

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: {} <input.snek> <output.s>", args[0]);
        std::process::exit(1);
    }

    let mut in_file = File::open(&args[1])?;
    let mut in_contents = String::new();
    in_file.read_to_string(&mut in_contents)?;

    // Wrap in a list so the sexp parser sees a single top-level expression
    // containing every definition and the main expression.
    let wrapped = format!("({})", in_contents.trim());
    let sexp = parse(&wrapped).expect("Invalid s-expression syntax");
    let prog = parse_program(&sexp);
    let asm  = compile_program(&prog);

    let mut out_file = File::create(&args[2])?;
    out_file.write_all(asm.as_bytes())?;
    Ok(())
}
