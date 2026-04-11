# -*- coding: utf-8 -*-
"""
03_data_types.py
================
Demonstrates data type access and interoperability between
Python built-in types and Java types in Jython.

  - Python primitives (int, float, str, bool, None)
  - Python collections (list, tuple, dict, set)
  - Java primitives via java.lang wrappers
  - Java collections: ArrayList, HashMap, LinkedList, HashSet, TreeMap
  - Java String methods called on Python strings (and vice-versa)
  - Type checking: isinstance, type(), Java .getClass()
  - Automatic coercion between Python and Java types

Run:  jython 03_data_types.py
"""

from java.util import ArrayList, HashMap, LinkedList, HashSet, TreeMap, Collections
from java.lang import Integer, Double, Boolean, String as JString, Math
from java.math import BigDecimal, BigInteger

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Python primitive types
# ─────────────────────────────────────────────────────
section("1. Python primitive types")

py_int   = 42
py_float = 3.14159
py_str   = "Jython"
py_bool  = True
py_none  = None

for name, val in [("int", py_int), ("float", py_float),
                  ("str", py_str), ("bool", py_bool), ("None", py_none)]:
    print("  {:8s}  value={!r:10}  type={}".format(name, val, type(val).__name__))


# ─────────────────────────────────────────────────────
# 2. Java wrapper types
# ─────────────────────────────────────────────────────
section("2. Java wrapper types (java.lang)")

java_int  = Integer(100)
java_dbl  = Double(2.718)
java_bool = Boolean(True)
java_str  = JString("Hello from Java String")
java_big  = BigInteger("123456789012345678901234567890")

print("  Integer   :", java_int,  "->", java_int.getClass().getName())
print("  Double    :", java_dbl,  "->", java_dbl.getClass().getName())
print("  Boolean   :", java_bool, "->", java_bool.getClass().getName())
print("  JString   :", java_str,  "->", java_str.getClass().getName())
print("  BigInteger:", java_big)

# Arithmetic: use .intValue() to extract the primitive from a Java Integer
print("\n  Python int + Java Integer:", py_int + java_int.intValue())


# ─────────────────────────────────────────────────────
# 3. Python collections
# ─────────────────────────────────────────────────────
section("3. Python built-in collections")

py_list  = [1, 2, 3, 4, 5]
py_tuple = (10, 20, 30)
py_dict  = {"name": "Ada", "role": "engineer"}
py_set   = {4, 8, 15, 16, 23, 42}

print("  list   :", py_list,  "-> index 2:", py_list[2])
print("  tuple  :", py_tuple, "-> slice [1:]:", py_tuple[1:])
print("  dict   :", py_dict,  "-> key 'name':", py_dict["name"])
print("  set    :", sorted(py_set))


# ─────────────────────────────────────────────────────
# 4. Java ArrayList — access patterns
# ─────────────────────────────────────────────────────
section("4. Java ArrayList — access patterns")

al = ArrayList()
for v in [10, 20, 30, 40, 50]:
    al.add(v)

print("  ArrayList:", list(al))
print("  .get(0)  :", al.get(0))          # Java index access
print("  .get(-1) :", al.get(al.size()-1)) # no negative indexing in Java — calc manually
print("  size()   :", al.size())
print("  Python slice (via list conversion):", list(al)[1:3])

# Modify
al.set(2, 999)                             # Java .set(index, value)
print("  After .set(2, 999):", list(al))

# In Jython 2.7 al.set() stores the raw Python int 999, not Integer(999)
# Use index-based remove (by position) to remove element at position 2
al.remove(2)                               # remove by index
print("  After .remove(index 2):", list(al))


# ─────────────────────────────────────────────────────
# 5. Java HashMap — access patterns
# ─────────────────────────────────────────────────────
section("5. Java HashMap — access patterns")

hm = HashMap()
hm.put("alpha", 1)
hm.put("beta",  2)
hm.put("gamma", 3)

print("  .get('alpha')       :", hm.get("alpha"))
print("  .getOrDefault('z',0):", hm.getOrDefault("z", 0))   # Java 8 method
print("  .containsKey('beta'):", hm.containsKey("beta"))
print("  .containsValue(3)   :", hm.containsValue(3))
print("  .size()             :", hm.size())

# Update
hm.put("alpha", 100)
if not hm.containsKey("delta"):     # putIfAbsent equivalent (Java 8 not in Jython 2.7)
    hm.put("delta", 4)
print("  After updates:", dict(hm))  # convert to Python dict for clean print


# ─────────────────────────────────────────────────────
# 6. Java TreeMap — sorted key access
# ─────────────────────────────────────────────────────
section("6. Java TreeMap — sorted key order")

tm = TreeMap()
for k, v in [("zebra",3), ("ant",1), ("monkey",2), ("bear",4)]:
    tm.put(k, v)

print("  Insertion order (unsorted): zebra, ant, monkey, bear")
print("  TreeMap (sorted by key):")
for entry in tm.entrySet():
    print("    {:8s} -> {}".format(entry.getKey(), entry.getValue()))

print("  firstKey():", tm.firstKey())
print("  lastKey() :", tm.lastKey())


# ─────────────────────────────────────────────────────
# 7. Java String methods vs Python str methods
# ─────────────────────────────────────────────────────
section("7. String methods — Python str vs Java String")

py_s  = "  Hello, Jython World!  "
java_s = JString("  Hello, Jython World!  ")

print("  Python  .strip()   :", py_s.strip())
print("  Java    .trim()    :", java_s.trim())
print("  Python  .upper()   :", py_s.strip().upper())
# In Jython 2.7 JString.trim() returns Python unicode — re-wrap to call Java methods
print("  Java    .toUpperCase():", JString(java_s.trim()).toUpperCase())
print("  Python  .split(','):", py_s.strip().split(","))
print("  Java    .split(','):", list(JString(java_s.trim()).split(",")))
print("  Python  len()      :", len(py_s))
print("  Java    .length()  :", java_s.length())
print("  Python  .startswith:", py_s.strip().startswith("Hello"))
print("  Java    .startsWith:", JString(java_s.trim()).startsWith("Hello"))


# ─────────────────────────────────────────────────────
# 8. Type checking — isinstance and Java .getClass()
# ─────────────────────────────────────────────────────
section("8. Type checking")

values = [42, 3.14, "hello", True, ArrayList(), Integer(7)]

for v in values:
    py_type   = type(v).__name__
    java_type = v.getClass().getSimpleName() if hasattr(v, "getClass") else "N/A"
    is_num    = isinstance(v, (int, float)) or isinstance(v, Integer)
    print("  value={:<18s} py_type={:<12} java_type={:<12} is_number={}".format(
        repr(v)[:18], py_type, java_type, is_num))


# ─────────────────────────────────────────────────────
# 9. BigDecimal — precise arithmetic
# ─────────────────────────────────────────────────────
section("9. Java BigDecimal — precise decimal arithmetic")

a = BigDecimal("0.1")
b = BigDecimal("0.2")
total = a.add(b)

print("  Python float:  0.1 + 0.2 =", 0.1 + 0.2)   # classic float imprecision
print("  BigDecimal:    0.1 + 0.2 =", total)          # exact


# ─────────────────────────────────────────────────────
# 10. java.lang.Math
# ─────────────────────────────────────────────────────
section("10. java.lang.Math methods")

print("  Math.sqrt(144)  =", Math.sqrt(144))
print("  Math.pow(2, 10) =", Math.pow(2, 10))
print("  Math.abs(-42)   =", Math.abs(-42))
print("  Math.PI         =", Math.PI)
print("  Math.E          =", Math.E)


# ─────────────────────────────────────────────────────
# 11. Java Collections utility
# ─────────────────────────────────────────────────────
section("11. java.util.Collections utilities")

nums = ArrayList()
for v in [5, 2, 8, 1, 9, 3]:
    nums.add(v)

print("  Before sort :", list(nums))
Collections.sort(nums)
print("  After sort  :", list(nums))
print("  Max         :", Collections.max(nums))
print("  Min         :", Collections.min(nums))
Collections.reverse(nums)
print("  Reversed    :", list(nums))

print("\n[03_data_types.py complete]")
