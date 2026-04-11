# -*- coding: utf-8 -*-
"""
05_control_abstraction.py
=========================
Demonstrates control abstraction in Jython:

  - Generators (lazy sequences)
  - Decorators (wrapping functions)
  - Context managers (with statement / __enter__ / __exit__)
  - Closures
  - Callbacks and event-driven patterns
  - Separating WHAT from HOW

Run:  jython 05_control_abstraction.py
"""

from java.util import ArrayList
from java.lang import Thread, Runnable, System

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Generators — lazy sequence production
# ─────────────────────────────────────────────────────
section("1. Generators — lazy sequences")

def count_up(start, stop, step=1):
    """Yields integers from start to stop (exclusive)."""
    current = start
    while current < stop:
        yield current
        current += step

def fibonacci_gen():
    """Infinite Fibonacci generator."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def take(n, gen):
    """Consume the first n items from a generator."""
    result = []
    for _ in range(n):
        result.append(next(gen))
    return result

print("  count_up(0,10,2):", list(count_up(0, 10, 2)))
print("  fibonacci(15)   :", take(15, fibonacci_gen()))

# Generator stored in a Java ArrayList
primes_gen = (n for n in range(2, 50)
              if all(n % d != 0 for d in range(2, int(n**0.5)+1)))
prime_list = ArrayList()
for p in primes_gen:
    prime_list.add(p)
print("  primes < 50 (Java ArrayList):", list(prime_list))


# ─────────────────────────────────────────────────────
# 2. Decorators — wrapping / augmenting functions
# ─────────────────────────────────────────────────────
section("2. Decorators — wrapping functions")

def trace(func):
    """Decorator that prints call info before and after the function."""
    def wrapper(*args, **kwargs):
        arg_str = ", ".join(repr(a) for a in args)
        print("  >> calling {}({})".format(func.__name__, arg_str))
        result = func(*args, **kwargs)
        print("  << {} returned {!r}".format(func.__name__, result))
        return result
    wrapper.__name__ = func.__name__
    return wrapper

def memoize(func):
    """Decorator that caches results."""
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.__name__ = func.__name__
    return wrapper

@trace
def multiply(a, b):
    return a * b

@memoize
def slow_square(n):
    # simulates expensive computation
    return n * n

multiply(6, 7)
print()
print("  slow_square(5):", slow_square(5))
print("  slow_square(5):", slow_square(5))   # cache hit
print("  slow_square(9):", slow_square(9))


# ─────────────────────────────────────────────────────
# 3. Stacked decorators
# ─────────────────────────────────────────────────────
section("3. Stacked decorators")

def uppercase_result(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return str(result).upper()
    return wrapper

def add_exclamation(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result + "!"
    return wrapper

@add_exclamation
@uppercase_result
def say(word):
    return word

print("  say('jython'):", say("jython"))     # uppercase then exclamation added


# ─────────────────────────────────────────────────────
# 4. Context managers (__enter__ / __exit__)
# ─────────────────────────────────────────────────────
section("4. Context managers — __enter__ / __exit__")

class ManagedFile:
    """A context manager that wraps file open/close, logging lifecycle."""
    def __init__(self, filename, mode="r"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        print("  [context] Opening '{}'".format(self.filename))
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
            print("  [context] Closed '{}'".format(self.filename))
        if exc_type:
            print("  [context] Exception suppressed: {}".format(exc_val))
            return True       # suppress exception
        return False

# Write a temp file then read it back using context manager
with ManagedFile("_ctx_test.txt", "w") as f:
    f.write("line one\nline two\nline three\n")

with ManagedFile("_ctx_test.txt", "r") as f:
    for line in f:
        print("  read:", line.rstrip())

# Context manager suppressing an exception
class Suppressor:
    def __init__(self, *exc_types):
        self.exc_types = exc_types
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in self.exc_types:
            print("  [Suppressor] caught and suppressed:", exc_val)
            return True

print()
with Suppressor(ZeroDivisionError):
    result = 10 / 0       # would normally crash
    print("  this line is never reached")
print("  execution continues after suppressed exception")


# ─────────────────────────────────────────────────────
# 5. Closures — functions capturing their environment
# ─────────────────────────────────────────────────────
section("5. Closures")

def make_counter(start=0, step=1):
    """Returns a counter function that closes over state."""
    count = [start]    # mutable container trick for Jython 2.7 (no nonlocal)
    def counter():
        val = count[0]
        count[0] += step
        return val
    return counter

def make_multiplier(factor):
    """Returns a function that multiplies by factor."""
    return lambda x: x * factor

counter_by_1  = make_counter()
counter_by_10 = make_counter(100, 10)
triple        = make_multiplier(3)

print("  counter_by_1  :", [counter_by_1()  for _ in range(5)])
print("  counter_by_10 :", [counter_by_10() for _ in range(5)])
print("  triple(7)     :", triple(7))


# ─────────────────────────────────────────────────────
# 6. Callbacks — control abstraction over Java threads
# ─────────────────────────────────────────────────────
section("6. Callbacks — Python function as Java Runnable")

class PythonRunnable(Runnable):
    """Wraps a Python callable as a Java Runnable interface."""
    def __init__(self, callback):
        self.callback = callback

    def run(self):
        self.callback()

results = ArrayList()

def task_a():
    results.add("Task A done")

def task_b():
    results.add("Task B done")

# Run both tasks in Java threads using Python callbacks
threads = [Thread(PythonRunnable(task_a)), Thread(PythonRunnable(task_b))]
for t in threads:
    t.start()
for t in threads:
    t.join()

for r in results:
    print("  Thread result:", r)


# ─────────────────────────────────────────────────────
# 7. Pipeline abstraction — composing functions
# ─────────────────────────────────────────────────────
section("7. Pipeline — composing functions (control abstraction)")

def pipeline(*steps):
    """Returns a function that passes its argument through each step in sequence."""
    def run(value):
        for step in steps:
            value = step(value)
        return value
    return run

# Build a text-processing pipeline
clean  = lambda s: str(s).strip()
lower  = lambda s: s.lower()
words  = lambda s: s.split()
unique = lambda lst: list(dict.fromkeys(lst))   # preserve order, deduplicate

process = pipeline(clean, lower, words, unique)

raw = ArrayList()
raw.add("  Hello World Hello Jython  ")
raw.add("  python JAVA jython PYTHON  ")

for text in raw:
    result = process(text)
    print("  Input : {!r}".format(str(text).strip()))
    print("  Output:", result)
    print()

print("[05_control_abstraction.py complete]")
