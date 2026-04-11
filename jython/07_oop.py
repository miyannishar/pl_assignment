# -*- coding: utf-8 -*-
"""
07_oop.py
=========
Demonstrates full OOP in Jython — Python class syntax running on the JVM.

  - Single inheritance
  - Multiple inheritance (Python MRO)
  - Method overriding and super()
  - Polymorphism (duck typing + formal hierarchy)
  - Class methods and static methods
  - __dunder__ / magic methods
  - Mixin pattern
  - Implementing a Java interface in Python
  - Passing Python objects into Java generic collections

Run:  jython 07_oop.py
"""

from java.util import ArrayList, HashMap
from java.io import Serializable
from java.lang import Comparable, Cloneable

SEP = "-" * 52

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ─────────────────────────────────────────────────────
# 1. Single inheritance
# ─────────────────────────────────────────────────────
section("1. Single inheritance")

class Animal(object):
    def __init__(self, name, species):
        self.name    = name
        self.species = species

    def speak(self):
        return "{} says ...".format(self.name)

    def describe(self):
        return "{} ({})".format(self.name, self.species)

    def __repr__(self):
        return "{}(name={!r})".format(type(self).__name__, self.name)


class Dog(Animal):
    def __init__(self, name, breed):
        super(Dog, self).__init__(name, "Canis lupus familiaris")
        self.breed = breed

    def speak(self):                          # override
        return "{} says: Woof!".format(self.name)

    def fetch(self, item):
        return "{} fetches the {}!".format(self.name, item)


class Cat(Animal):
    def __init__(self, name, indoor=True):
        super(Cat, self).__init__(name, "Felis catus")
        self.indoor = indoor

    def speak(self):                          # override
        return "{} says: Meow.".format(self.name)


dog = Dog("Rex", "Labrador")
cat = Cat("Whiskers")

print("  dog.describe():", dog.describe())
print("  dog.speak()   :", dog.speak())
print("  dog.fetch()   :", dog.fetch("ball"))
print("  cat.describe():", cat.describe())
print("  cat.speak()   :", cat.speak())


# ─────────────────────────────────────────────────────
# 2. Polymorphism — uniform interface over mixed types
# ─────────────────────────────────────────────────────
section("2. Polymorphism — uniform interface, different behaviour")

class Parrot(Animal):
    def __init__(self, name, phrase):
        super(Parrot, self).__init__(name, "Psittaciformes")
        self.phrase = phrase

    def speak(self):
        return '{} says: "{}"'.format(self.name, self.phrase)

animals = ArrayList()         # Java ArrayList holding Python objects
animals.add(Dog("Rex", "Lab"))
animals.add(Cat("Mochi"))
animals.add(Parrot("Polly", "Pretty bird!"))
animals.add(Animal("Unknown", "???"))

print("  All animals speak (polymorphism):")
for animal in animals:
    print("   ", animal.speak())     # speaks() dispatched to correct subclass


# ─────────────────────────────────────────────────────
# 3. Multiple inheritance and MRO
# ─────────────────────────────────────────────────────
section("3. Multiple inheritance and Python MRO")

class Flyable(object):
    def move(self):
        return "flying"
    def describe_movement(self):
        return "{} is {}".format(type(self).__name__, self.move())

class Swimmable(object):
    def move(self):
        return "swimming"
    def describe_movement(self):
        return "{} is {}".format(type(self).__name__, self.move())

class Duck(Animal, Flyable, Swimmable):
    """Duck inherits from Animal, Flyable, Swimmable."""
    def __init__(self, name):
        super(Duck, self).__init__(name, "Anas platyrhynchos")

    def speak(self):
        return "{} says: Quack!".format(self.name)

    def move(self):         # override disambiguates MRO conflict
        return "waddling (can also fly and swim)"

duck = Duck("Donald")
print("  MRO:", [cls.__name__ for cls in Duck.__mro__])
print("  duck.speak()              :", duck.speak())
print("  duck.describe_movement()  :", duck.describe_movement())
print("  isinstance(duck, Flyable) :", isinstance(duck, Flyable))
print("  isinstance(duck, Animal)  :", isinstance(duck, Animal))


# ─────────────────────────────────────────────────────
# 4. Mixin pattern
# ─────────────────────────────────────────────────────
section("4. Mixin pattern")

class JsonMixin(object):
    """Mixin that adds .to_json() to any class with a __dict__."""
    def to_json(self):
        pairs = []
        for k, v in sorted(self.__dict__.items()):
            if not k.startswith("_"):
                pairs.append('"{k}": "{v}"'.format(k=k, v=v))
        return "{" + ", ".join(pairs) + "}"

class LoggableMixin(object):
    """Mixin that adds .log() method."""
    def log(self, message):
        print("  [LOG] [{}] {}".format(type(self).__name__, message))

class Product(JsonMixin, LoggableMixin):
    def __init__(self, sku, name, price):
        self.name  = name
        self.price = price
        self.sku   = sku

p = Product("SKU-001", "Jython Book", 49.99)
p.log("Product created")
print("  to_json:", p.to_json())


# ─────────────────────────────────────────────────────
# 5. Class methods and static methods
# ─────────────────────────────────────────────────────
section("5. Class methods and static methods")

class Counter(object):
    _count = 0        # class variable

    def __init__(self, label):
        self.label = label
        Counter._count += 1

    @classmethod
    def get_count(cls):
        """Class method — receives the class, not an instance."""
        return cls._count

    @classmethod
    def reset(cls):
        cls._count = 0

    @staticmethod
    def describe():
        """Static method — no implicit first argument."""
        return "Counter tracks how many instances have been created."

    def __repr__(self):
        return "Counter({!r})".format(self.label)

c1 = Counter("alpha")
c2 = Counter("beta")
c3 = Counter("gamma")

print("  Instances created  :", Counter.get_count())
print("  Counter.describe() :", Counter.describe())
Counter.reset()
print("  After reset        :", Counter.get_count())


# ─────────────────────────────────────────────────────
# 6. Magic / dunder methods
# ─────────────────────────────────────────────────────
section("6. Magic methods (__dunder__)")

class Vector(object):
    """2D vector with operator overloading."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):  return "Vector({}, {})".format(self.x, self.y)
    def __str__(self):   return "({}, {})".format(self.x, self.y)
    def __add__(self, o):  return Vector(self.x + o.x, self.y + o.y)
    def __sub__(self, o):  return Vector(self.x - o.x, self.y - o.y)
    def __mul__(self, s):  return Vector(self.x * s,   self.y * s)
    def __rmul__(self, s): return self.__mul__(s)
    def __neg__(self):     return Vector(-self.x, -self.y)
    def __eq__(self, o):   return isinstance(o, Vector) and (self.x,self.y)==(o.x,o.y)
    def __len__(self):     return 2
    def __getitem__(self, i):
        if i == 0: return self.x
        if i == 1: return self.y
        raise IndexError("Vector index out of range")

    @property
    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print("  v1            :", v1)
print("  v2            :", v2)
print("  v1 + v2       :", v1 + v2)
print("  v1 - v2       :", v1 - v2)
print("  v1 * 3        :", v1 * 3)
print("  3 * v2        :", 3 * v2)
print("  -v1           :", -v1)
print("  v1 == v1      :", v1 == v1)
print("  v1[0], v1[1]  :", v1[0], v1[1])
print("  |v1|          :", v1.magnitude)
print("  len(v1)       :", len(v1))

# Store Vectors in Java ArrayList
vecs = ArrayList()
for dx, dy in [(1,0),(0,1),(1,1),(2,3)]:
    vecs.add(Vector(dx, dy))

print("  Magnitudes:", ["{:.2f}".format(v.magnitude) for v in vecs])


# ─────────────────────────────────────────────────────
# 7. Implementing Java interfaces in Python
# ─────────────────────────────────────────────────────
section("7. Python class implementing Java Comparable + Cloneable")

class Score(Comparable):
    """
    Represents a game score.
    Implements java.lang.Comparable so Java's Collections.sort() works.
    """

    def __init__(self, player, points):
        self.player = player
        self.points = points

    def compareTo(self, other):
        # Descending order (higher score first)
        return other.points - self.points

    def toString(self):
        # When stored in Java collections, Java calls toString() not __str__
        return "{}: {:,}".format(self.player, self.points)

    def __str__(self):
        return self.toString()

from java.util import Collections

scores = ArrayList()
for player, pts in [("Alice",15000), ("Bob",23000), ("Carol",8900), ("Dave",23000)]:
    scores.add(Score(player, pts))

print("  Before sort:")
for s in scores: print("   ", s)

Collections.sort(scores)    # Java sort calling Python compareTo

print("  After sort (high score first):")
for s in scores: print("   ", s)


# ─────────────────────────────────────────────────────
# 8. Full mini-application tying it all together
# ─────────────────────────────────────────────────────
section("8. Mini application — Library catalog")

class LibraryItem(object):

    def __init__(self, item_id, title):
        self._id    = item_id
        self._title = title
        self._checked_out = False

    @property
    def title(self): return self._title

    @property
    def is_available(self): return not self._checked_out

    def check_out(self):
        if not self._checked_out:
            self._checked_out = True
            return True
        return False

    def return_item(self):
        self._checked_out = False

    def __repr__(self):
        avail = "available" if self.is_available else "checked out"
        return "[{}] '{}' ({})".format(self._id, self._title, avail)


class Book(LibraryItem):
    def __init__(self, item_id, title, author, pages):
        super(Book, self).__init__(item_id, title)
        self.author = author
        self.pages  = pages

    def __repr__(self):
        return "Book({}, {!r}, by {}, {} pp)".format(
            self._id, self._title, self.author, self.pages)

class DVD(LibraryItem):
    def __init__(self, item_id, title, director, runtime_min):
        super(DVD, self).__init__(item_id, title)
        self.director   = director
        self.runtime    = runtime_min

    def __repr__(self):
        return "DVD({}, {!r}, dir. {}, {}min)".format(
            self._id, self._title, self.director, self.runtime)

class Library(object):
    def __init__(self, name):
        self.name    = name
        self._catalog = ArrayList()   # Java ArrayList of mixed Python objects

    def add(self, item):
        self._catalog.add(item)

    def search(self, keyword):
        keyword = keyword.lower()
        results = ArrayList()
        for item in self._catalog:
            if keyword in item.title.lower():
                results.add(item)
        return results

    def available(self):
        return [item for item in self._catalog if item.is_available]

    def stats(self):
        total     = self._catalog.size()
        books     = sum(1 for i in self._catalog if isinstance(i, Book))
        dvds      = sum(1 for i in self._catalog if isinstance(i, DVD))
        out       = sum(1 for i in self._catalog if not i.is_available)
        return {"total": total, "books": books, "dvds": dvds, "checked_out": out}

lib = Library("Jython Public Library")
lib.add(Book(1,  "Clean Code",         "Robert Martin",  464))
lib.add(Book(2,  "The Pragmatic Programmer", "Hunt & Thomas", 352))
lib.add(DVD(3,   "Inception",           "Christopher Nolan", 148))
lib.add(Book(4,  "Code Complete",       "Steve McConnell", 914))
lib.add(DVD(5,   "The Matrix",          "The Wachowskis",  136))

# Check out some items
lib._catalog.get(0).check_out()
lib._catalog.get(2).check_out()

print("  {} catalog:".format(lib.name))
for item in lib._catalog:
    print("   ", item)

print("\n  Search 'code':")
for item in lib.search("code"):
    print("   ", item)

print("\n  Available items:")
for item in lib.available():
    print("   ", item)

print("\n  Stats:", lib.stats())

print("\n[07_oop.py complete]")
