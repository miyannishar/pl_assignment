# -*- coding: utf-8 -*-
"""
01_control_flow.py
==================
Demonstrates Jython control flow using Java data types.

  - if / elif / else
  - Nested conditionals
  - Ternary (conditional expression)
  - Short-circuit evaluation (and / or)
  - Exception-based control flow (try / except / else / finally)
  - Pass, continue, break placeholders

Run:  jython 01_control_flow.py
"""

from java.util import ArrayList, HashMap
from java.lang import Integer, String as JString

SEP = "-" * 52


def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Basic if / elif / else
# ─────────────────────────────────────────────────────
section("1. if / elif / else")

scores = ArrayList()
for v in [45, 72, 88, 95, 30]:
    scores.add(Integer(v))          # Java Integer objects in a Java list

for score in scores:
    # Python if/elif/else — score is a Java Integer, comparison works naturally
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    print("Score {:>3}  ->  Grade {}".format(int(score), grade))


# ─────────────────────────────────────────────────────
# 2. Nested conditionals
# ─────────────────────────────────────────────────────
section("2. Nested conditionals")

inventory = HashMap()
inventory.put("apples",  10)
inventory.put("bananas", 0)
inventory.put("cherries", 5)

items = ["apples", "bananas", "cherries", "grapes"]

for item in items:
    if inventory.containsKey(item):           # Java HashMap method
        qty = inventory.get(item)
        if qty > 0:
            if qty > 7:
                status = "well-stocked"
            else:
                status = "low stock"
        else:
            status = "OUT OF STOCK"
    else:
        status = "not in inventory"
    print("  {:10s} -> {}".format(item, status))


# ─────────────────────────────────────────────────────
# 3. Ternary (conditional) expression
# ─────────────────────────────────────────────────────
section("3. Ternary expression")

temperatures = ArrayList()
for t in [15, 22, 35, 8, 28]:
    temperatures.add(t)

for temp in temperatures:
    label = "hot" if temp >= 30 else ("warm" if temp >= 20 else "cool")
    print("  {} deg C  ->  {}".format(temp, label))


# ─────────────────────────────────────────────────────
# 4. Short-circuit evaluation
# ─────────────────────────────────────────────────────
section("4. Short-circuit evaluation (and / or)")

def safe_divide(a, b):
    # 'b != 0' is checked first; division only happens if True
    return b != 0 and a / b

def default_name(name):
    # returns name if truthy, otherwise the fallback string
    return name or "Anonymous"

print("  safe_divide(10, 2)  =", safe_divide(10, 2))
print("  safe_divide(10, 0)  =", safe_divide(10, 0))  # returns False, no ZeroDivisionError
print("  default_name('')    =", default_name(""))
print("  default_name('Ada') =", default_name("Ada"))


# ─────────────────────────────────────────────────────
# 5. try / except / else / finally
# ─────────────────────────────────────────────────────
section("5. try / except / else / finally")

def parse_int(value):
    try:
        result = int(value)
    except ValueError:
        print("  [except]  '{}' is not a valid integer".format(value))
        return None
    else:
        # runs ONLY when no exception was raised
        print("  [else]    parsed '{}' -> {}".format(value, result))
        return result
    finally:
        # always runs
        print("  [finally] done processing '{}'".format(value))

parse_int("42")
print()
parse_int("oops")


# ─────────────────────────────────────────────────────
# 6. Chained comparisons
# ─────────────────────────────────────────────────────
section("6. Chained comparisons")

values = [3, 7, 10, 15, 20]
for v in values:
    if 5 <= v <= 15:        # Python chained comparison — not valid Java syntax
        print("  {} is in range [5, 15]".format(v))
    else:
        print("  {} is outside [5, 15]".format(v))


# ─────────────────────────────────────────────────────
# 7. Truthiness of Java objects
# ─────────────────────────────────────────────────────
section("7. Truthiness of Java objects in Python if-statements")

empty_list = ArrayList()
full_list  = ArrayList()
full_list.add("item")

# Java objects evaluated in a Python boolean context
if empty_list:
    print("  empty ArrayList is truthy")
else:
    print("  empty ArrayList is falsy  (Java isEmpty -> Python False)")

if full_list:
    print("  full  ArrayList is truthy (has elements)")

java_zero = Integer(0)
java_one  = Integer(1)
print("  Integer(0) is falsy:", not java_zero)
print("  Integer(1) is truthy:", bool(java_one))

print("\n[01_control_flow.py complete]")
