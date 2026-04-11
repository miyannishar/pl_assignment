# Jython Demo Suite — Presentation Guide

> **Run everything at once:** `jython run_all.py`  
> **Run one file:** `jython 01_control_flow.py`

---

## Files Overview

| File | Topic | Key Concepts |
|---|---|---|
| `01_control_flow.py` | Control Flow | if/elif/else, ternary, short-circuit, try/except/else/finally, chained comparisons |
| `02_iteration.py` | Iteration | for/while, Java collections, break/continue, for/else, enumerate/zip, list comprehensions, Java Iterator |
| `03_data_types.py` | Data Types | Python primitives, Java wrappers, ArrayList/HashMap/TreeMap, String methods, BigDecimal, java.lang.Math |
| `04_subroutines.py` | Subroutines | Functions, defaults, *args/**kwargs, multiple returns, first-class functions, lambdas, map/filter, recursion |
| `05_control_abstraction.py` | Control Abstraction | Generators, decorators, context managers, closures, Java Thread callbacks, function pipelines |
| `06_data_abstraction.py` | Data Abstraction | Encapsulation, @property, abstract base classes, Java Comparable, immutable objects |
| `07_oop.py` | OOP | Single/multiple inheritance, MRO, mixins, class/static methods, magic methods, Java interfaces, polymorphism |

---

## Setup

```bash
# Install
brew install jython   # macOS

# Verify
jython --version      # Jython 2.7.x

# Test Java import
jython -c "from java.util import ArrayList; print('OK')"
```

---

## Running

```bash
cd pl_assignment/jython

# Run all (with summary)
jython run_all.py

# Run individual files
jython 01_control_flow.py
jython 02_iteration.py
jython 03_data_types.py
jython 04_subroutines.py
jython 05_control_abstraction.py
jython 06_data_abstraction.py
jython 07_oop.py
```

---

## Key Lines to Highlight (per file)

### 01 — Control Flow
```python
from java.util import ArrayList, HashMap
from java.lang import Integer

if self.tasks.isEmpty():    # Java method in Python if
if score >= 90:             # standard Python if/elif/else
label = "hot" if temp >= 30 else "cool"        # ternary
b != 0 and a / b           # short-circuit
except IOError as e:        # Python exception hierarchy
```

### 02 — Iteration
```python
from java.util import ArrayList, HashMap, LinkedList, HashSet, TreeSet
for fruit in fruits:        # Python for over Java ArrayList
for entry in capitals.entrySet():   # iterating Java HashMap entries
it = data.iterator()        # explicit Java Iterator
while it.hasNext(): it.next()       # Java protocol in Python while
for n in numbers if n % 2 == 0     # list comprehension over Java list
```

### 03 — Data Types
```python
from java.util import ArrayList, HashMap, TreeMap, Collections
from java.lang import Integer, Double, Math
from java.math import BigDecimal

al.get(0)          # Java index access
al.set(2, 999)     # Java mutation
hm.getOrDefault()  # Java 8 method from Python
BigDecimal("0.1").add(BigDecimal("0.2"))   # precise arithmetic
```

### 04 — Subroutines
```python
def total(*nums):       # variable args
def build_record(**fields):  # keyword args
lo, hi, avg = stats(data)    # multiple return / unpack
apply(square, nums)          # function as argument
lambda x: int(x) ** 2       # lambda
class LengthComparator(Comparator):  # Python class -> Java interface
```

### 05 — Control Abstraction
```python
yield current               # generator
@trace                      # decorator
def __enter__ / __exit__:   # context manager
count = [start]             # closure over mutable container
class PythonRunnable(Runnable): def run(self): callback()  # Java thread
pipeline(clean, lower, words, unique)   # function composition
```

### 06 — Data Abstraction
```python
self.__balance = ...        # name-mangled private attribute
@property / @celsius.setter # controlled access
__metaclass__ = ABCMeta     # abstract base class (Jython 2.7)
@abstractmethod             # forces subclasses to implement
class Student(Comparable): def compareTo(self, other):  # Java interface
object.__setattr__(self, "_x", x)   # immutable init bypass
```

### 07 — OOP
```python
super(Dog, self).__init__()     # explicit super() call (Jython 2.7)
[cls.__name__ for cls in Duck.__mro__]  # MRO inspection
class JsonMixin / LoggableMixin         # mixin pattern
def __add__ / __mul__ / __rmul__:      # operator overloading
class Score(Comparable): def compareTo # Java interface from Python
Collections.sort(scores)               # Java sorting Python objects
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `command not found: jython` | `brew install jython` or `export PATH="/jython/bin:$PATH"` |
| `ImportError: No module named java.util` | You ran `python`, use `jython` |
| `SyntaxError` on f-strings | Use `.format()` — Jython is Python 2.7 |
| `TypeError` on `cmp()` | Only available in Jython 2.7 (not CPython 3) |
| `AttributeError: __metaclass__` | Normal in CPython 3 — Jython 2.7 metaclass syntax |

---

## Quick Reference

```
Install:      brew install jython
Version:      jython --version
Run all:      jython run_all.py
Run one:      jython 01_control_flow.py
REPL:         jython
Java test:    jython -c "from java.util import ArrayList; print('OK')"
```
