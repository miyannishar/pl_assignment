# -*- coding: utf-8 -*-
"""
06_data_abstraction.py
======================
Demonstrates data abstraction in Jython:

  - Encapsulation (private attributes via name-mangling)
  - Properties (@property getter/setter)
  - Abstract base classes (Python abc module)
  - Implementing Java interfaces as Python classes
  - Immutable value objects
  - Data classes (manual, Jython 2.7 compatible)

Run:  jython 06_data_abstraction.py
"""

from java.util import ArrayList, Collections
from java.util import Comparator
from java.lang import Comparable

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Encapsulation — private attributes
# ─────────────────────────────────────────────────────
section("1. Encapsulation — private attributes")

class BankAccount(object):
    """
    Demonstrates encapsulation: balance is private and only
    accessible through controlled public methods.
    """

    def __init__(self, owner, initial_balance=0.0):
        self.owner = owner
        self.__balance = float(initial_balance)   # name-mangled: __balance
        self.__transactions = ArrayList()          # Java ArrayList for history

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive, got: {}".format(amount))
        self.__balance += amount
        self.__transactions.add("+{:.2f}".format(amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.__balance:
            raise ValueError("Insufficient funds (balance={:.2f})".format(self.__balance))
        self.__balance -= amount
        self.__transactions.add("-{:.2f}".format(amount))

    def get_balance(self):
        return self.__balance

    def get_history(self):
        return list(self.__transactions)           # safe copy

    def __str__(self):
        return "BankAccount({}, balance={:.2f})".format(self.owner, self.__balance)

acct = BankAccount("Alice", 1000.00)
acct.deposit(250.00)
acct.withdraw(75.50)

print("  Account  :", acct)
print("  Balance  :", acct.get_balance())
print("  History  :", acct.get_history())

# Trying to access private attribute directly fails
try:
    _ = acct.__balance         # AttributeError — name-mangled
except AttributeError as e:
    print("  Direct __balance access raises AttributeError (encapsulation works)")


# ─────────────────────────────────────────────────────
# 2. Properties — controlled attribute access
# ─────────────────────────────────────────────────────
section("2. Properties — @property getter / setter")

class Temperature(object):
    """Stores temperature internally in Celsius; exposes Fahrenheit via property."""

    def __init__(self, celsius=0.0):
        self._celsius = celsius          # single underscore: "protected by convention"

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Computed property — no setter needed."""
        return self._celsius * 9.0 / 5.0 + 32

    @property
    def kelvin(self):
        return self._celsius + 273.15

    def __str__(self):
        return "{:.2f} C  /  {:.2f} F  /  {:.2f} K".format(
            self._celsius, self.fahrenheit, self.kelvin)

t = Temperature(100)
print("  Boiling  :", t)

t.celsius = -40
print("  -40 C    :", t)   # -40 is the same in both scales

try:
    t.celsius = -300        # below absolute zero
except ValueError as e:
    print("  ValueError caught:", e)


# ─────────────────────────────────────────────────────
# 3. Abstract base class (Python abc)
# ─────────────────────────────────────────────────────
section("3. Abstract base class (python abc module)")

# Jython 2.7 compatible ABC using ABCMeta
from abc import ABCMeta, abstractmethod

class Shape(object):
    __metaclass__ = ABCMeta   # Jython 2.7 metaclass syntax

    @abstractmethod
    def area(self):
        """Return the area of the shape."""
        pass

    @abstractmethod
    def perimeter(self):
        """Return the perimeter of the shape."""
        pass

    def describe(self):
        """Concrete method shared by all subclasses."""
        return "{}: area={:.2f}, perimeter={:.2f}".format(
            type(self).__name__, self.area(), self.perimeter())


class Circle(Shape):
    from java.lang import Math as JMath

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return Circle.JMath.PI * self.radius ** 2

    def perimeter(self):
        return 2 * Circle.JMath.PI * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width  = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):
        s = self.perimeter() / 2.0
        return (s * (s-self.a) * (s-self.b) * (s-self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c

shapes = ArrayList()
shapes.add(Circle(5))
shapes.add(Rectangle(4, 6))
shapes.add(Triangle(3, 4, 5))

for shape in shapes:
    print(" ", shape.describe())


# ─────────────────────────────────────────────────────
# 4. Implementing Java Comparable in Python
# ─────────────────────────────────────────────────────
section("4. Python class implementing Java Comparable interface")

class Student(Comparable):
    """
    A Python class that implements java.lang.Comparable,
    allowing Java's Collections.sort() to sort Student objects.
    """

    def __init__(self, name, gpa):
        self.name = name
        self.gpa  = gpa

    def compareTo(self, other):
        """Java Comparable method — sort by GPA descending."""
        if self.gpa > other.gpa:
            return -1
        elif self.gpa < other.gpa:
            return 1
        return 0

    def toString(self):
        # Java proxy calls toString() when printing from Java collections
        return "Student({}, GPA={:.1f})".format(self.name, self.gpa)

    def __str__(self):
        return self.toString()

roster = ArrayList()
for name, gpa in [("Alice",3.8), ("Bob",3.2), ("Carol",3.9), ("Dave",3.5)]:
    roster.add(Student(name, gpa))

print("  Before sort:")
for s in roster: print("   ", s)

Collections.sort(roster)   # uses Student.compareTo() — Java calling Python!

print("  After sort (GPA desc):")
for s in roster: print("   ", s)


# ─────────────────────────────────────────────────────
# 5. Immutable value object
# ─────────────────────────────────────────────────────
section("5. Immutable value object")

class Point(object):
    """Immutable 2D point — __setattr__ raises after construction."""

    def __init__(self, x, y):
        # Use object.__setattr__ to bypass our override during init
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    @property
    def x(self): return self._x

    @property
    def y(self): return self._y

    def __setattr__(self, name, value):
        raise AttributeError("Point is immutable - cannot set '{}'".format(name))

    def translate(self, dx, dy):
        """Returns a NEW Point rather than mutating self."""
        return Point(self._x + dx, self._y + dy)

    def distance_to(self, other):
        return ((self._x - other._x)**2 + (self._y - other._y)**2) ** 0.5

    def __repr__(self):
        return "Point({}, {})".format(self._x, self._y)

    def __eq__(self, other):
        return isinstance(other, Point) and self._x == other._x and self._y == other._y

p1 = Point(3, 4)
p2 = p1.translate(1, -1)

print("  p1           :", p1)
print("  p2 (moved)   :", p2)
print("  distance     :", p1.distance_to(Point(0, 0)))
print("  p1 unchanged :", p1)

try:
    p1.x = 999
except AttributeError as e:
    print("  Mutation blocked:", e)


# ─────────────────────────────────────────────────────
# 6. Data class pattern (Jython 2.7 compatible)
# ─────────────────────────────────────────────────────
section("6. Data class pattern — __repr__, __eq__, __hash__")

class Color(object):
    """A value-semantic RGB color."""

    def __init__(self, r, g, b):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))

    def blend(self, other):
        return Color((self.r+other.r)//2, (self.g+other.g)//2, (self.b+other.b)//2)

    def hex(self):
        return "#{:02X}{:02X}{:02X}".format(self.r, self.g, self.b)

    def __repr__(self):
        return "Color(r={}, g={}, b={})".format(self.r, self.g, self.b)

    def __eq__(self, other):
        return isinstance(other, Color) and (self.r, self.g, self.b) == (other.r, other.g, other.b)

    def __hash__(self):
        return hash((self.r, self.g, self.b))

red   = Color(255, 0,   0)
blue  = Color(0,   0, 255)
blend = red.blend(blue)

print("  red          :", red,   "->", red.hex())
print("  blue         :", blue,  "->", blue.hex())
print("  blend        :", blend, "->", blend.hex())
print("  red == red   :", red == Color(255, 0, 0))
print("  red == blue  :", red == blue)

# Store Color objects in a Java ArrayList
palette = ArrayList()
palette.add(red)
palette.add(blue)
palette.add(blend)
print("  palette size :", palette.size())
for c in palette:
    print("   ", c.hex())

print("\n[06_data_abstraction.py complete]")
