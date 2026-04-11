// Diamondback Runtime — runtime/start.rs

use std::env;

#[link(name = "our_code")]
extern "C" {
    fn our_code_starts_here(input: i64) -> i64;
}

/// Called from generated assembly on runtime errors.
/// errcode 1 = invalid argument (type mismatch)
#[no_mangle]
extern "C" fn snek_error(errcode: i64) {
    if errcode == 1 {
        eprintln!("invalid argument");
    } else if errcode == 2 {
        eprintln!("overflow");
    } else {
        eprintln!("unknown error {errcode}");
    }
    std::process::exit(1);
}

/// Built-in print function callable from Diamondback via (print expr).
/// Prints the value and returns it unchanged.
#[no_mangle]
extern "C" fn snek_print(val: i64) -> i64 {
    if val & 1 == 0 {
        // Number: stored as (n << 1)
        println!("{}", val >> 1);
    } else if val == 3 {
        println!("true");
    } else if val == 1 {
        println!("false");
    } else {
        println!("unknown({})", val);
    }
    val
}

/// Pretty-print a tagged Diamondback value.
fn format_val(v: i64) -> String {
    if v == 3 {
        "true".to_string()
    } else if v == 1 {
        "false".to_string()
    } else if v & 1 == 0 {
        (v >> 1).to_string()
    } else {
        format!("unknown({})", v)
    }
}

fn main() {
    let input: i64 = env::args().nth(1).map_or(Ok(0i64 << 1), |s| {
        if s == "true" {
            Ok(3i64)
        } else if s == "false" {
            Ok(1i64)
        } else {
            s.parse::<i64>().map(|n| n << 1)
        }
    }).unwrap_or_else(|_| {
        eprintln!("invalid input");
        std::process::exit(1);
    });

    let result: i64 = unsafe { our_code_starts_here(input) };
    println!("{}", format_val(result));
}
