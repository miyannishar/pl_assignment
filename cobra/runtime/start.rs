// Cobra Runtime — runtime/start.rs

use std::env;

#[link(name = "our_code")]
extern "C" {
    #[link_name = "\x01our_code_starts_here"]
    fn our_code_starts_here(input: i64) -> i64;
}

/// Called from generated assembly on runtime errors.
/// errcode 1 = invalid argument (type mismatch)
/// errcode 2 = overflow
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

/// Pretty-print a tagged Cobra value.
fn format_val(v: i64) -> String {
    // Booleans: LSB = 1
    if v == 3 {
        "true".to_string()
    } else if v == 1 {
        "false".to_string()
    } else if v & 1 == 0 {
        // Number: stored as (n << 1)
        (v >> 1).to_string()
    } else {
        format!("unknown({})", v)
    }
}

fn main() {
    // Parse optional command-line input (default 0 = false / number 0)
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
