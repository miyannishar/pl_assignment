# -*- coding: utf-8 -*-
"""
04_subroutines.py
=================
Demonstrates subroutines (functions) in Jython — Python syntax
operating on Java objects.

  - Basic function definitions
  - Default parameters
  - Positional *args and keyword **kwargs
  - Return multiple values (tuple unpacking)
  - First-class functions (passed as arguments)
  - Lambda expressions
  - Higher-order functions: map, filter, sorted with key
  - Recursive functions
  - Java Callable / Comparator via Python lambda

Run:  jython 04_subroutines.py
"""

from java.util import ArrayList, Collections, Comparator, HashMap
from java.lang import Integer, Math

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Basic function definitions
# ─────────────────────────────────────────────────────
section("1. Basic function definitions")

def greet(name):
    """Return a greeting string."""
    return "Hello, {}!".format(name)

def add(a, b):
    """Add two numbers (works with Python ints or Java Integers)."""
    return a + b

print("  greet('Jython')     =", greet("Jython"))
print("  add(3, 4)           =", add(3, 4))
print("  add(Integer(3), 4)  =", add(Integer(3).intValue(), 4))   # .intValue() unboxes in Jython 2.7


# ─────────────────────────────────────────────────────
# 2. Default parameters
# ─────────────────────────────────────────────────────
section("2. Default parameters")

def make_list(size=5, fill=0):
    """Return a Java ArrayList of `size` elements filled with `fill`."""
    result = ArrayList()
    for _ in range(size):
        result.add(fill)
    return result

print("  make_list()          =", list(make_list()))
print("  make_list(3)         =", list(make_list(3)))
print("  make_list(4, 99)     =", list(make_list(4, 99)))
print("  make_list(fill='x')  =", list(make_list(fill="x")))


# ─────────────────────────────────────────────────────
# 3. *args — variable positional arguments
# ─────────────────────────────────────────────────────
section("3. *args — variable positional arguments")

def total(*nums):
    """Sum any number of arguments (each can be Python or Java numeric)."""
    running = 0
    for n in nums:
        # .intValue() unboxes Java Integer; plain Python ints don't have it
        running += n.intValue() if hasattr(n, "intValue") else n
    return running

def join_words(*args, **kwargs):
    """Join words with a separator (Jython 2.7: no keyword-only args after *args)."""
    separator = kwargs.get("separator", " ")
    return separator.join(args)

print("  total(1,2,3)              =", total(1, 2, 3))
print("  total(10,20,Integer(30))  =", total(10, 20, Integer(30)))
print("  join_words('a','b','c')   =", join_words("a", "b", "c"))
print("  join with '-'             =", join_words("a", "b", "c", separator="-"))


# ─────────────────────────────────────────────────────
# 4. **kwargs — variable keyword arguments
# ─────────────────────────────────────────────────────
section("4. **kwargs — variable keyword arguments")

def build_record(**fields):
    """Build a Java HashMap from keyword arguments."""
    record = HashMap()
    for key, val in fields.items():
        record.put(key, val)
    return record

r1 = build_record(name="Ada", role="engineer", level=3)
r2 = build_record(language="Jython", version="2.7")

for entry in r1.entrySet():
    print("  r1: {:10s} = {}".format(entry.getKey(), entry.getValue()))
for entry in r2.entrySet():
    print("  r2: {:10s} = {}".format(entry.getKey(), entry.getValue()))


# ─────────────────────────────────────────────────────
# 5. Multiple return values (tuple unpacking)
# ─────────────────────────────────────────────────────
section("5. Multiple return values (tuple unpacking)")

def stats(java_list):
    """Return (min, max, mean) of a Java ArrayList of numbers."""
    values = [int(x) for x in java_list]
    return min(values), max(values), sum(values) / float(len(values))

data = ArrayList()
for v in [4, 7, 2, 9, 5, 1, 8, 3, 6]:
    data.add(v)

lo, hi, avg = stats(data)
print("  data  :", list(data))
print("  min   :", lo)
print("  max   :", hi)
print("  mean  :", avg)


# ─────────────────────────────────────────────────────
# 6. First-class functions (functions as arguments)
# ─────────────────────────────────────────────────────
section("6. First-class functions (passed as arguments)")

def apply(func, java_list):
    """Apply func to every element and return a new Java ArrayList."""
    result = ArrayList()
    for item in java_list:
        result.add(func(item))
    return result

def square(x):   return int(x) ** 2
def cube(x):     return int(x) ** 3
def negate(x):   return -int(x)

nums = ArrayList()
for v in [1, 2, 3, 4, 5]:
    nums.add(v)

print("  original :", list(nums))
print("  squared  :", list(apply(square, nums)))
print("  cubed    :", list(apply(cube, nums)))
print("  negated  :", list(apply(negate, nums)))


# ─────────────────────────────────────────────────────
# 7. Lambda expressions
# ─────────────────────────────────────────────────────
section("7. Lambda expressions")

double  = lambda x: int(x) * 2
is_even = lambda x: int(x) % 2 == 0
clamp   = lambda x, lo, hi: max(lo, min(hi, int(x)))

print("  double(7)          =", double(7))
print("  is_even(4)         =", is_even(4))
print("  is_even(7)         =", is_even(7))
print("  clamp(15, 0, 10)   =", clamp(15, 0, 10))
print("  clamp(-3, 0, 10)   =", clamp(-3, 0, 10))


# ─────────────────────────────────────────────────────
# 8. map / filter / sorted with key=
# ─────────────────────────────────────────────────────
section("8. map / filter / sorted with lambda key=")

words_java = ArrayList()
for w in ["banana", "apple", "fig", "cherry", "date", "elderberry"]:
    words_java.add(w)

# map: convert to uppercase Python strings
uppercased = list(map(lambda w: str(w).upper(), words_java))
print("  map(upper)     :", uppercased)

# filter: keep only words longer than 4 chars
long_words = list(filter(lambda w: len(str(w)) > 4, words_java))
print("  filter(len>4)  :", long_words)

# sorted with key (over Java ArrayList)
by_length  = sorted(words_java, key=lambda w: len(str(w)))
by_alpha   = sorted(words_java, key=lambda w: str(w))
print("  sorted by len  :", by_length)
print("  sorted alpha   :", by_alpha)


# ─────────────────────────────────────────────────────
# 9. Recursive functions
# ─────────────────────────────────────────────────────
section("9. Recursive functions")

def factorial(n):
    """Classic recursive factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """Recursive Fibonacci (memoised via default-arg dict trick)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print("  factorial(0..7):", [factorial(i) for i in range(8)])
print("  fibonacci(0..9):", [fibonacci(i) for i in range(10)])


# ─────────────────────────────────────────────────────
# 10. Java Comparator implemented as a Python lambda
# ─────────────────────────────────────────────────────
section("10. Java Comparator via Python class (Java interface impl)")

class LengthComparator(Comparator):
    """Sort strings by length, then alphabetically — implements java.util.Comparator."""
    def compare(self, a, b):
        diff = len(str(a)) - len(str(b))
        if diff != 0:
            return diff
        return cmp(str(a), str(b))      # cmp() is Python 2 / Jython 2.7 built-in

animals = ArrayList()
for a in ["elephant", "cat", "bear", "ox", "flamingo", "gnu"]:
    animals.add(a)

print("  Before sort:", list(animals))
Collections.sort(animals, LengthComparator())   # pass Python class to Java method
print("  By length  :", list(animals))

print("\n[04_subroutines.py complete]")
