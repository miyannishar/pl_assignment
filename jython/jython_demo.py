# -*- coding: utf-8 -*-
"""
jython_demo.py - Task Manager Application
==========================================
Demonstrates Jython's ability to blend Python syntax with Java libraries.

Run with:  jython jython_demo.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# KEY DEMO LINE: importing a Java standard-library class directly in Python code
# ─────────────────────────────────────────────────────────────────────────────
from java.util import ArrayList   # Java import inside Python!


# ─────────────────────────────────────────────────────────────────────────────
# OOP: Plain Python class (works identically in CPython and Jython)
# ─────────────────────────────────────────────────────────────────────────────
class Task:
    """Represents a single task with a title, description, and completion flag."""

    def __init__(self, task_id, title, description=""):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.completed = False

    def complete(self):
        self.completed = True

    def __str__(self):
        status = "✓" if self.completed else "○"
        return "[{}] #{} - {} : {}".format(status, self.task_id, self.title, self.description)


# ─────────────────────────────────────────────────────────────────────────────
# OOP: TaskManager uses a Java ArrayList instead of a Python list
# ─────────────────────────────────────────────────────────────────────────────
class TaskManager:
    """Manages a collection of Task objects stored in a Java ArrayList."""

    def __init__(self):
        # Java ArrayList used here – demonstrates Java/Python interop
        self.tasks = ArrayList()
        self._next_id = 1

    def add_task(self, title, description=""):
        task = Task(self._next_id, title, description)
        self.tasks.add(task)          # Java ArrayList's .add() method
        self._next_id += 1
        print("Added task: {}".format(task.title))
        return task

    def complete_task(self, task_id):
        # Python for-loop over a Java ArrayList – seamless iteration
        for task in self.tasks:
            if task.task_id == task_id:
                task.complete()
                print("Completed task #{}: {}".format(task_id, task.title))
                return True
        print("Task #{} not found.".format(task_id))
        return False

    def list_tasks(self):
        if self.tasks.isEmpty():          # Java ArrayList method
            print("No tasks found.")
            return
        print("\n--- Task List ({} total) ---".format(self.tasks.size()))
        for task in self.tasks:
            print("  " + str(task))
        print("----------------------------\n")

    def pending_count(self):
        return sum(1 for t in self.tasks if not t.completed)

    def save_to_file(self, filename):
        """File I/O – note explicit close() for demo clarity."""
        f = open(filename, "w")          # explicit open/close (no with-statement)
        try:
            f.write("# Task Manager Export\n")
            for task in self.tasks:
                status = "DONE" if task.completed else "PENDING"
                line = "{}|{}|{}|{}\n".format(
                    task.task_id, task.title, task.description, status
                )
                f.write(line)
            print("Tasks saved to '{}'.".format(filename))
        finally:
            f.close()                    # KEY LINE: explicit close() – highlight this

    def load_from_file(self, filename):
        """File I/O with exception handling."""
        try:
            f = open(filename, "r")
            try:
                lines = f.readlines()
            finally:
                f.close()                # explicit close even on read

            loaded = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) != 4:
                    continue
                task_id, title, description, status = parts
                task = Task(int(task_id), title, description)
                if status == "DONE":
                    task.complete()
                self.tasks.add(task)
                self._next_id = max(self._next_id, int(task_id) + 1)
                loaded += 1
            print("Loaded {} task(s) from '{}'.".format(loaded, filename))

        # ─────────────────────────────────────────────────────────────────────
        # EXCEPTION HANDLING: catching specific Java/Python exceptions
        # ─────────────────────────────────────────────────────────────────────
        except IOError as e:
            print("IOError – file '{}' not found: {}".format(filename, e))
        except ValueError as e:
            print("ValueError – bad data in file: {}".format(e))
        except Exception as e:
            print("Unexpected error: {}".format(e))


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL FLOW: if/else + loops
# ─────────────────────────────────────────────────────────────────────────────
def run_demo():
    print("=" * 50)
    print("  Jython Task Manager Demo")
    print("  (Python syntax + Java libraries)")
    print("=" * 50 + "\n")

    manager = TaskManager()

    # --- Add tasks ---
    manager.add_task("Buy groceries", "Milk, eggs, bread")
    manager.add_task("Write report", "Q1 summary for team")
    manager.add_task("Exercise", "30-minute run")
    manager.add_task("Read book", "Chapter 5 of Clean Code")

    # --- List all tasks ---
    manager.list_tasks()

    # --- Complete some tasks (if/else control flow) ---
    for task_id in [1, 3]:
        success = manager.complete_task(task_id)
        if success:
            print("  -> Task {} marked complete.".format(task_id))
        else:
            print("  -> Could not mark task {}.".format(task_id))

    print()

    # --- Summary using a while-style idiom ---
    pending = manager.pending_count()
    total   = manager.tasks.size()
    print("Progress: {}/{} tasks completed ({} pending)".format(
        total - pending, total, pending
    ))

    # --- File operations ---
    print()
    filename = "tasks_output.txt"
    manager.save_to_file(filename)

    # Load from a non-existent file to demo exception handling
    print("\n--- Testing exception handling ---")
    manager2 = TaskManager()
    manager2.load_from_file("does_not_exist.txt")   # triggers IOError path

    # Load from the file we just saved
    print()
    manager3 = TaskManager()
    manager3.load_from_file(filename)
    manager3.list_tasks()

    print("Demo complete!")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_demo()
