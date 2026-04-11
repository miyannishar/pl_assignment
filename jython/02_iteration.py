# -*- coding: utf-8 -*-
"""
02_iteration.py
===============
Demonstrates every iteration pattern Jython supports, mixing
Python syntax with Java collection types.

  - for over Python list / range
  - for over Java ArrayList, HashMap, LinkedList, HashSet
  - while loop
  - break / continue / else on loops
  - enumerate / zip
  - List comprehensions over Java collections
  - Java Iterator protocol
  - Nested loops with labels-via-flags

Run:  jython 02_iteration.py
"""

import sys
from java.util import ArrayList, HashMap, LinkedList, HashSet, TreeSet
from java.util import Iterator        # Java Iterator interface
from java.lang import Integer

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. for over range (pure Python)
# ─────────────────────────────────────────────────────
section("1. for over range")

sys.stdout.write("  Squares: ")
for i in range(1, 8):
    sys.stdout.write(str(i * i) + "  ")
print("")


# ─────────────────────────────────────────────────────
# 2. for over a Java ArrayList
# ─────────────────────────────────────────────────────
section("2. for over Java ArrayList")

fruits = ArrayList()
for f in ["mango", "papaya", "lychee", "guava", "starfruit"]:
    fruits.add(f)

for fruit in fruits:                # Python for-loop, Java collection
    print("  Fruit:", fruit)


# ─────────────────────────────────────────────────────
# 3. for over a Java LinkedList
# ─────────────────────────────────────────────────────
section("3. for over Java LinkedList (queue-style)")

queue = LinkedList()
for task in ["compile", "test", "deploy", "notify"]:
    queue.offer(task)               # Java LinkedList queue method

print("  Processing tasks from LinkedList:")
for task in queue:
    print("    ->", task)


# ─────────────────────────────────────────────────────
# 4. for over a Java HashMap
# ─────────────────────────────────────────────────────
section("4. for over Java HashMap (keys, values, entries)")

capitals = HashMap()
for country, city in [("France","Paris"), ("Japan","Tokyo"),
                      ("Brazil","Brasilia"), ("India","Delhi")]:
    capitals.put(country, city)

# Iterate keys (Java .keySet() -> Python for)
print("  Keys:")
for country in capitals.keySet():
    print("    ", country)

# Iterate values
print("  Values:")
for city in capitals.values():
    print("    ", city)

# Iterate entries
print("  Entries:")
for entry in capitals.entrySet():
    print("    {} -> {}".format(entry.getKey(), entry.getValue()))


# ─────────────────────────────────────────────────────
# 5. for over a Java HashSet and TreeSet
# ─────────────────────────────────────────────────────
section("5. for over Java HashSet / TreeSet")

nums = HashSet()
for n in [5, 3, 8, 1, 9, 2, 7]:
    nums.add(n)
print("  HashSet (unordered):", list(nums))

sorted_nums = TreeSet(nums)         # TreeSet sorts automatically
print("  TreeSet (sorted):   ", list(sorted_nums))


# ─────────────────────────────────────────────────────
# 6. while loop
# ─────────────────────────────────────────────────────
section("6. while loop")

stack = ArrayList()
for v in [10, 20, 30, 40, 50]:
    stack.add(v)

print("  Popping from Java ArrayList as a stack:")
while not stack.isEmpty():          # Java .isEmpty() in Python while
    last = stack.remove(stack.size() - 1)   # Java .remove(index)
    print("    popped:", last)


# ─────────────────────────────────────────────────────
# 7. break / continue
# ─────────────────────────────────────────────────────
section("7. break / continue")

numbers = ArrayList()
for n in range(1, 16):
    numbers.add(n)

print("  Even numbers (continue skips odds):")
evens = []
for n in numbers:
    if n % 2 != 0:
        continue                    # skip odd
    evens.append(int(n))
print("   ", evens)

print("  First number divisible by 7 (break):")
for n in numbers:
    if n % 7 == 0:
        print("   ", int(n))
        break


# ─────────────────────────────────────────────────────
# 8. for...else (Python-only construct)
# ─────────────────────────────────────────────────────
section("8. for/else — Python-unique construct")

primes_to_check = [11, 15, 17, 20, 23]

for candidate in primes_to_check:
    for divisor in range(2, candidate):
        if candidate % divisor == 0:
            print("  {} is NOT prime (divisible by {})".format(candidate, divisor))
            break
    else:
        # else block runs only if loop completed without break
        print("  {} IS prime".format(candidate))


# ─────────────────────────────────────────────────────
# 9. enumerate and zip
# ─────────────────────────────────────────────────────
section("9. enumerate and zip over Java collections")

languages = ArrayList()
for lang in ["Python", "Java", "Scala", "Kotlin", "Groovy"]:
    languages.add(lang)

paradigms = ArrayList()
for p in ["multi-paradigm", "OOP", "functional+OOP", "pragmatic", "dynamic"]:
    paradigms.add(p)

print("  enumerate:")
for idx, lang in enumerate(languages):
    print("    [{:>2}] {}".format(idx, lang))

print("  zip:")
for lang, paradigm in zip(languages, paradigms):
    print("    {:10s}  ->  {}".format(lang, paradigm))


# ─────────────────────────────────────────────────────
# 10. List comprehensions over Java collections
# ─────────────────────────────────────────────────────
section("10. List comprehensions over Java collections")

java_ints = ArrayList()
for v in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    java_ints.add(Integer(v))

# Comprehension filtering even numbers and squaring them
result = [int(x) ** 2 for x in java_ints if int(x) % 2 == 0]
print("  Even squares:", result)

# Comprehension over HashMap keys
capitals2 = HashMap()
capitals2.put("USA", "Washington")
capitals2.put("Germany", "Berlin")
capitals2.put("Australia", "Canberra")
long_countries = [k for k in capitals2.keySet() if len(k) > 5]
print("  Countries with name > 5 chars:", sorted(long_countries))


# ─────────────────────────────────────────────────────
# 11. Java Iterator protocol manually
# ─────────────────────────────────────────────────────
section("11. Java Iterator used explicitly")

data = ArrayList()
for v in ["alpha", "beta", "gamma", "delta"]:
    data.add(v)

it = data.iterator()                # Java Iterator object
print("  Manual iterator:")
while it.hasNext():                 # Java hasNext()
    item = it.next()                # Java next()
    print("    ->", item)


# ─────────────────────────────────────────────────────
# 12. Nested loops — simulating matrix traversal
# ─────────────────────────────────────────────────────
section("12. Nested loops — 3x3 multiplication table")

matrix = ArrayList()
for row_idx in range(1, 4):
    row = ArrayList()
    for col_idx in range(1, 4):
        row.add(row_idx * col_idx)
    matrix.add(row)

for row in matrix:
    sys.stdout.write("  ")
    for cell in row:
        sys.stdout.write("{:>4}".format(int(cell)))
    print("")

print("\n[02_iteration.py complete]")
