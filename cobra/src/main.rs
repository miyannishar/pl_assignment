// Cobra Compiler — src/main.rs
//
// Tagged value representation:
//   Numbers  → (n << 1)         LSB = 0
//   true     → 3  (0b11)        LSB = 1
//   false    → 1  (0b01)        LSB = 1
//
// Error codes passed to snek_error:
//   1 = invalid argument (type mismatch)
//   2 = overflow            (not used in base impl but wired up)

use sexp::Atom::*;
use sexp::*;
use std::env;
use std::fs::File;
use std::io::prelude::*;
use im::HashMap;

// ─────────────────────────── AST ────────────────────────────────────────────

#[derive(Debug, Clone)]
enum UnOp {
    Add1,
    Sub1,
    Negate,
    IsNum,
    IsBool,
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
    Num(i32),
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
}

// ─────────────────────────── Parser ─────────────────────────────────────────

const RESERVED: &[&str] = &[
    "let", "if", "block", "loop", "break", "set!", "true", "false", "input",
    "add1", "sub1", "negate", "isnum", "isbool",
    "+", "-", "*", "<", ">", "<=", ">=", "=",
];

fn is_reserved(s: &str) -> bool {
    RESERVED.contains(&s)
}

fn parse_bind(s: &Sexp) -> (String, Expr) {
    match s {
        Sexp::List(vec) => match &vec[..] {
            [Sexp::Atom(S(name)), e] => {
                if is_reserved(name) {
                    panic!("Invalid: reserved word used as identifier: {name}");
                }
                (name.clone(), parse_expr(e))
            }
            _ => panic!("Invalid binding"),
        },
        _ => panic!("Invalid binding"),
    }
}

fn parse_expr(s: &Sexp) -> Expr {
    match s {
        // Literals
        Sexp::Atom(I(n)) => Expr::Num(i32::try_from(*n).expect("Integer overflow in literal")),
        Sexp::Atom(S(name)) => match name.as_str() {
            "true"  => Expr::Bool(true),
            "false" => Expr::Bool(false),
            "input" => Expr::Input,
            other => {
                if is_reserved(other) {
                    panic!("Invalid: reserved word used as expression: {other}");
                }
                Expr::Var(other.to_string())
            }
        },

        Sexp::List(vec) => match &vec[..] {
            // Unary ops
            [Sexp::Atom(S(op)), e] if op == "add1"   => Expr::UnOp(UnOp::Add1,   Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "sub1"   => Expr::UnOp(UnOp::Sub1,   Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "negate" => Expr::UnOp(UnOp::Negate, Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "isnum"  => Expr::UnOp(UnOp::IsNum,  Box::new(parse_expr(e))),
            [Sexp::Atom(S(op)), e] if op == "isbool" => Expr::UnOp(UnOp::IsBool, Box::new(parse_expr(e))),

            // Binary ops
            [Sexp::Atom(S(op)), e1, e2] if op == "+"  => Expr::BinOp(BinOp::Plus,     Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "-"  => Expr::BinOp(BinOp::Minus,    Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "*"  => Expr::BinOp(BinOp::Times,    Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "<"  => Expr::BinOp(BinOp::Less,     Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == ">"  => Expr::BinOp(BinOp::Greater,  Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "<=" => Expr::BinOp(BinOp::LessEq,   Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == ">=" => Expr::BinOp(BinOp::GreaterEq,Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),
            [Sexp::Atom(S(op)), e1, e2] if op == "="  => Expr::BinOp(BinOp::Equal,    Box::new(parse_expr(e1)), Box::new(parse_expr(e2))),

            // If
            [Sexp::Atom(S(op)), cond, then_e, else_e] if op == "if" =>
                Expr::If(Box::new(parse_expr(cond)), Box::new(parse_expr(then_e)), Box::new(parse_expr(else_e))),

            // Block
            [Sexp::Atom(S(op)), rest @ ..] if op == "block" => {
                if rest.is_empty() { panic!("Invalid: block requires at least one expression"); }
                Expr::Block(rest.iter().map(parse_expr).collect())
            }

            // Loop
            [Sexp::Atom(S(op)), body] if op == "loop" => Expr::Loop(Box::new(parse_expr(body))),

            // Break
            [Sexp::Atom(S(op)), e] if op == "break" => Expr::Break(Box::new(parse_expr(e))),

            // Set!
            [Sexp::Atom(S(op)), Sexp::Atom(S(name)), e] if op == "set!" => {
                if is_reserved(name) {
                    panic!("Invalid: reserved word used as set! target: {name}");
                }
                Expr::Set(name.clone(), Box::new(parse_expr(e)))
            }

            // Let
            [Sexp::Atom(S(op)), Sexp::List(bindings), body] if op == "let" => {
                if bindings.is_empty() {
                    panic!("Invalid: let requires at least one binding");
                }
                let mut seen = std::collections::HashSet::new();
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

            _ => panic!("Invalid expression: {s}"),
        },

        _ => panic!("Invalid expression: {s}"),
    }
}

// ─────────────────────────── Code Generation ────────────────────────────────

fn new_label(ctr: &mut i32, prefix: &str) -> String {
    *ctr += 1;
    format!("{}_{}", prefix, ctr)
}

/// Emit instructions that check rax is a number (LSB == 0).
/// Calls snek_error(1) if not.
fn check_is_num(label_err: &str) -> Vec<String> {
    vec![
        "  mov rbx, rax".to_string(),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {label_err}"),
    ]
}

/// Emit instructions that check the value in [rsp-saved_offset] is a number.
fn check_saved_is_num(saved_offset: i32, label_err: &str) -> Vec<String> {
    vec![
        format!("  mov rbx, [rsp - {saved_offset}]"),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {label_err}"),
    ]
}

/// Emit instructions that verify rax and [rsp-saved_offset] have the same tag.
/// Used for equality comparisons (= requires same type).
fn check_same_type(saved_offset: i32, label_err: &str) -> Vec<String> {
    vec![
        "  mov rbx, rax".to_string(),
        format!("  xor rbx, [rsp - {saved_offset}]"),
        "  and rbx, 1".to_string(),
        "  cmp rbx, 0".to_string(),
        format!("  jne {label_err}"),
    ]
}

/// Core compilation function.
///
/// Parameters:
///   e            – expression to compile
///   si           – next free stack index (1-based; offset = si*8)
///   env          – maps variable name → byte offset from RSP
///   label_ctr    – counter for generating unique labels
///   break_target – label to jump to on `break`, None if not inside a loop
fn compile_expr(
    e: &Expr,
    si: i32,
    env: &HashMap<String, i32>,
    label_ctr: &mut i32,
    break_target: &Option<String>,
) -> Vec<String> {
    // We emit a single shared error handler per function call; we append it at
    // the end of our_code_starts_here (see main).  All type checks jump to the
    // global label `throw_error` which is defined once in the asm preamble.
    let err_label = "_throw_error";

    match e {
        // ── Literals ──────────────────────────────────────────────────────
        Expr::Num(n) => {
            let tagged = (*n as i64) << 1;
            vec![format!("  mov rax, {tagged}")]
        }

        Expr::Bool(b) => {
            let val = if *b { 3i64 } else { 1i64 };
            vec![format!("  mov rax, {val}")]
        }

        Expr::Input => {
            // The runtime passes input as first argument (rdi) by our calling
            // convention: our_code_starts_here(input: i64) -> i64
            vec!["  mov rax, rdi".to_string()]
        }

        // ── Variable access ───────────────────────────────────────────────
        Expr::Var(name) => match env.get(name) {
            Some(off) => vec![format!("  mov rax, [rsp - {off}]")],
            None => panic!("Unbound variable identifier {name}"),
        },

        // ── Mutation ──────────────────────────────────────────────────────
        Expr::Set(name, val_expr) => {
            let off = *env.get(name).unwrap_or_else(|| panic!("Unbound variable in set!: {name}"));
            let mut instrs = compile_expr(val_expr, si, env, label_ctr, break_target);
            instrs.push(format!("  mov [rsp - {off}], rax"));
            instrs
        }

        // ── Unary operations ─────────────────────────────────────────────
        Expr::UnOp(op, sub) => {
            let mut instrs = compile_expr(sub, si, env, label_ctr, break_target);
            match op {
                UnOp::Add1 => {
                    // Check operand is number
                    instrs.extend(check_is_num(err_label));
                    instrs.push("  add rax, 2".to_string()); // +1 in tagged space = +2
                }
                UnOp::Sub1 => {
                    instrs.extend(check_is_num(err_label));
                    instrs.push("  sub rax, 2".to_string());
                }
                UnOp::Negate => {
                    instrs.extend(check_is_num(err_label));
                    instrs.push("  neg rax".to_string());
                }
                UnOp::IsNum => {
                    // Result: true(3) if LSB==0, else false(1)
                    instrs.push("  and rax, 1".to_string());
                    instrs.push("  cmp rax, 0".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    // sete sets AL to 1 if ZF, 0 otherwise
                    instrs.push("  sete al".to_string());
                    // Now rax is 1 (is num) or 0 (not num)
                    // Map: 1 → 3 (true), 0 → 1 (false)
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
                UnOp::IsBool => {
                    // Result: true(3) if LSB==1, else false(1)
                    instrs.push("  and rax, 1".to_string());
                    instrs.push("  cmp rax, 1".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    instrs.push("  sete al".to_string());
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
            }
            instrs
        }

        // ── Binary operations ─────────────────────────────────────────────
        Expr::BinOp(op, left, right) => {
            let saved_off = si * 8;
            let mut instrs = compile_expr(left, si, env, label_ctr, break_target);
            // Save left result
            instrs.push(format!("  mov [rsp - {saved_off}], rax"));
            instrs.extend(compile_expr(right, si + 1, env, label_ctr, break_target));
            // rax = right, [rsp-saved_off] = left

            match op {
                BinOp::Plus | BinOp::Minus | BinOp::Times => {
                    // Both must be numbers
                    instrs.extend(check_is_num(err_label));
                    instrs.extend(check_saved_is_num(saved_off, err_label));
                    match op {
                        BinOp::Plus  => instrs.push(format!("  add rax, [rsp - {saved_off}]")),
                        BinOp::Minus => {
                            // result = left - right
                            // rax=right; we need left - right
                            instrs.push("  mov rbx, rax".to_string());
                            instrs.push(format!("  mov rax, [rsp - {saved_off}]"));
                            instrs.push("  sub rax, rbx".to_string());
                        }
                        BinOp::Times => {
                            // Both are tagged as (n<<1). Product would be (n*m<<2).
                            // We need (n*m<<1), so shift one operand right first.
                            // Unshift rax (right) before multiply.
                            instrs.push("  sar rax, 1".to_string());
                            instrs.push(format!("  imul rax, [rsp - {saved_off}]"));
                        }
                        _ => unreachable!(),
                    }
                }

                BinOp::Less | BinOp::Greater | BinOp::LessEq | BinOp::GreaterEq => {
                    // Both must be numbers
                    instrs.extend(check_is_num(err_label));
                    instrs.extend(check_saved_is_num(saved_off, err_label));
                    // rax=right (tagged), [rsp-saved_off]=left (tagged)
                    // Compare tagged values directly (works for integers because tag bit is always 0)
                    instrs.push("  mov rbx, rax".to_string());      // rbx = right
                    instrs.push(format!("  mov rax, [rsp - {saved_off}]")); // rax = left
                    instrs.push("  cmp rax, rbx".to_string());
                    instrs.push("  mov rax, 0".to_string());
                    let set_instr = match op {
                        BinOp::Less     => "setl",
                        BinOp::Greater  => "setg",
                        BinOp::LessEq   => "setle",
                        BinOp::GreaterEq=> "setge",
                        _ => unreachable!(),
                    };
                    instrs.push(format!("  {set_instr} al"));
                    // 1 → true(3), 0 → false(1)
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }

                BinOp::Equal => {
                    // Both must have same type tag
                    instrs.extend(check_same_type(saved_off, err_label));
                    instrs.push("  cmp rax, [rsp - {}]".replace("{}", &saved_off.to_string()));
                    instrs.push("  mov rax, 0".to_string());
                    instrs.push("  sete al".to_string());
                    instrs.push("  imul rax, 2".to_string());
                    instrs.push("  add rax, 1".to_string());
                }
            }
            instrs
        }

        // ── Let ───────────────────────────────────────────────────────────
        Expr::Let(bindings, body) => {
            let mut instrs = Vec::new();
            let mut env2 = env.clone();
            let mut cur_si = si;
            for (name, val_expr) in bindings {
                instrs.extend(compile_expr(val_expr, cur_si, &env2, label_ctr, break_target));
                let off = cur_si * 8;
                instrs.push(format!("  mov [rsp - {off}], rax"));
                env2 = env2.update(name.clone(), off);
                cur_si += 1;
            }
            instrs.extend(compile_expr(body, cur_si, &env2, label_ctr, break_target));
            instrs
        }

        // ── If ────────────────────────────────────────────────────────────
        Expr::If(cond, then_e, else_e) => {
            let else_lbl = new_label(label_ctr, "if_else");
            let end_lbl  = new_label(label_ctr, "if_end");

            let mut instrs = compile_expr(cond, si, env, label_ctr, break_target);
            // false = 1 (0b01); anything else is truthy
            instrs.push("  cmp rax, 1".to_string());
            instrs.push(format!("  je {else_lbl}"));
            instrs.extend(compile_expr(then_e, si, env, label_ctr, break_target));
            instrs.push(format!("  jmp {end_lbl}"));
            instrs.push(format!("{else_lbl}:"));
            instrs.extend(compile_expr(else_e, si, env, label_ctr, break_target));
            instrs.push(format!("{end_lbl}:"));
            instrs
        }

        // ── Block ─────────────────────────────────────────────────────────
        Expr::Block(exprs) => {
            let mut instrs = Vec::new();
            for expr in exprs {
                instrs.extend(compile_expr(expr, si, env, label_ctr, break_target));
            }
            instrs
        }

        // ── Loop ──────────────────────────────────────────────────────────
        Expr::Loop(body) => {
            let start_lbl = new_label(label_ctr, "loop_start");
            let end_lbl   = new_label(label_ctr, "loop_end");

            let mut instrs = vec![format!("{start_lbl}:")];
            instrs.extend(compile_expr(body, si, env, label_ctr, &Some(end_lbl.clone())));
            instrs.push(format!("  jmp {start_lbl}"));
            instrs.push(format!("{end_lbl}:"));
            instrs
        }

        // ── Break ─────────────────────────────────────────────────────────
        Expr::Break(val_expr) => {
            match break_target {
                Some(lbl) => {
                    let mut instrs = compile_expr(val_expr, si, env, label_ctr, break_target);
                    instrs.push(format!("  jmp {lbl}"));
                    instrs
                }
                None => panic!("break used outside of a loop"),
            }
        }
    }
}

// ─────────────────────────── Top-level compilation ──────────────────────────

fn compile(e: &Expr) -> String {
    let mut label_ctr = 0i32;
    // si starts at 2 to leave room for alignment / saved registers.
    let body_instrs = compile_expr(e, 2, &HashMap::new(), &mut label_ctr, &None);

    let body = body_instrs.join("\n");

    // The calling convention we use:
    //   our_code_starts_here(input: i64 in rdi) -> i64 in rax
    // We need a 16-byte-aligned stack. We sub/add a fixed amount so that 
    // the deepest stack usage stays aligned; 1024 bytes gives us plenty of room.
    format!(
        "section .text
extern _snek_error
global _our_code_starts_here
_our_code_starts_here:
  sub rsp, 1024
{body}
  add rsp, 1024
  ret
_throw_error:
  mov rdi, 1
  call _snek_error
  ret
"
    )
}

// ─────────────────────────── Main ───────────────────────────────────────────

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: {} <input.snek> <output.s>", args[0]);
        std::process::exit(1);
    }

    let in_name  = &args[1];
    let out_name = &args[2];

    let mut in_file = File::open(in_name)?;
    let mut in_contents = String::new();
    in_file.read_to_string(&mut in_contents)?;

    let sexp = parse(&in_contents).expect("Invalid s-expression syntax");
    let expr = parse_expr(&sexp);
    let asm  = compile(&expr);

    let mut out_file = File::create(out_name)?;
    out_file.write_all(asm.as_bytes())?;

    Ok(())
}
