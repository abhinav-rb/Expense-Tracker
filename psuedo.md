# Expense Tracker — Design Document

This file is the blueprint. Read it before coding, and come back to it whenever you forget *why* something is where it is.

---

## 1. What we're building

A command-line app that tracks expenses and saves them to a JSON file.

**Core requirements (build these first):**
- `add` an expense (description + amount). The ID and date are assigned automatically.
- `update` an expense (description, amount, or category) by ID
- `delete` an expense by ID
- `list` all expenses
- `summary` of all expenses (total amount)
- `summary --month N` for one month of the current year

**Optional (build after the core works):**
- Categories + filtering the list by category
- Monthly budget + a warning when you go over it
- Export to CSV

**Out of scope:** income and negative amounts. The spec only tracks expenses.

---

## 2. The big picture

The app is split into **layers**. Each layer has one job and only talks to the layer directly below it.

```
        You (typing in the terminal)
                    │
                    ▼
   ┌──────────────────────────────────┐
   │  CLI                             │  reads commands, prints results
   └──────────────────────────────────┘
                    │ calls methods on
                    ▼
   ┌──────────────────────────────────┐
   │  ExpenseTracker                  │  the rules: add, update, delete, totals
   └──────────────────────────────────┘
          │ creates / holds              │ asks to load & save
          ▼                              ▼
   ┌───────────────┐          ┌─────────────────────────┐
   │  Expense      │          │  ExpenseRepository      │──> expenses.json
   │  (just data)  │          │  (file reading/writing) │
   └───────────────┘          └─────────────────────────┘
```

**Arrows only point down.** `Expense` doesn't know the file exists, and `ExpenseRepository` doesn't know the terminal exists. That's what keeps each piece simple and replaceable.

---

## 3. Suggested file layout

```
Expense-Tracker/
├── main.py          # starting point: builds the objects and starts the CLI
├── expense.py       # class Expense
├── repository.py    # class ExpenseRepository
├── tracker.py       # class ExpenseTracker
├── cli.py           # class CLI
├── exceptions.py    # custom error classes
└── expenses.json    # created automatically on the first save (add it to .gitignore)
```

**Why one class per file?** When something breaks in saving, you know to open `repository.py`. Small files are easier to read, test and review.

---

## 4. The classes

### 4.1 `Expense` — one expense (file: `expense.py`)

**Job:** hold the data for a single expense. Nothing else.

| Attribute | Type | Meaning |
|---|---|---|
| `id` | `int` | Unique number used to find it later (`delete --id 2`). Assigned by the tracker, not typed by the user. |
| `description` | `str` | What it was, e.g. `"Lunch"` |
| `amount` | `float` | How much. Must be greater than 0. |
| `date` | `datetime.date` | The day it was added. Set automatically to today. |
| `category` | `str` | e.g. `"Food"`. Defaults to `"General"` if none is given. |

| Method | Input → Output | What it does |
|---|---|---|
| `__init__(...)` | the attributes above → new object | The constructor. It runs whenever you create an `Expense`. |
| `to_dict()` | nothing → `dict` | Turns the object into a plain dictionary so it can be written to JSON. JSON doesn't understand Python objects or dates, so convert the date to a string like `"2026-10-12"`. |
| `from_dict(data)` | `dict` → `Expense` | The reverse: rebuilds an `Expense` from a dictionary read out of JSON. Make it a `@classmethod`, because you call it *on the class* to create a new object: `Expense.from_dict(d)`. |

**Why it has no `add` or `save` method:** an expense is like a receipt. A receipt doesn't file itself; someone else does the filing. Keeping `Expense` "dumb" means you can create and test one without a file or terminal existing.

---

### 4.2 `ExpenseRepository` — the storage (file: `repository.py`)

**Job:** move expenses between the JSON file and Python. It has no business rules and does no printing.

| Attribute | Type | Meaning |
|---|---|---|
| `file_path` | `str` | Where the data lives, e.g. `"expenses.json"` |

| Method | Input → Output | What it does |
|---|---|---|
| `load()` | nothing → `list[Expense]` | Reads the file and uses `Expense.from_dict` on each entry. **If the file doesn't exist yet, return an empty list.** That's normal on the first run, not an error. If the file is corrupted (invalid JSON), raise a clear error. |
| `save(expenses)` | `list[Expense]` → nothing | Converts each expense with `to_dict()` and writes the whole list to the file. |

**Why it's separate:** this is the only class that knows the data is stored as JSON. To switch to CSV or a real database someday, you'd rewrite only this class, and nothing else would notice. This idea is called the **Repository pattern**.

---

### 4.3 `ExpenseTracker` — the brain (file: `tracker.py`)

**Job:** all the rules of the app. It manages the collection of expenses and decides what's allowed.

| Attribute | Type | Meaning |
|---|---|---|
| `repository` | `ExpenseRepository` | Passed in through the constructor, not created inside. (See "Composition" in section 6.) |
| `expenses` | `list[Expense]` | All current expenses, filled by calling `repository.load()` in `__init__`. |

| Method | Input → Output | What it does |
|---|---|---|
| `add_expense(description, amount, category="General")` | → `Expense` | Validates the amount, picks the next ID, creates the `Expense` with today's date, appends it, saves, and **returns the new expense** so the CLI can print its ID. |
| `update_expense(expense_id, description=None, amount=None, category=None)` | → `Expense` | Finds the expense and changes only the fields that aren't `None`. Validates the new amount if given, then saves. |
| `delete_expense(expense_id)` | → nothing | Finds the expense, removes it, and saves. |
| `list_expenses(category=None)` | → `list[Expense]` | Returns all expenses, or only those in one category if a category is given. |
| `total(month=None)` | → `float` | Sum of all amounts. If a month (1–12) is given, only counts expenses from that month **of the current year**. The total is calculated every time, never stored. |
| `_find_by_id(expense_id)` | → `Expense` | Helper. Loops through `expenses` and returns the match. If none is found, **raise `ExpenseNotFoundError`**. Used by update and delete so the search logic exists in one place. |
| `_next_id()` | → `int` | Helper. Returns the highest existing ID + 1, or 1 if the list is empty. |
| `_validate_amount(amount)` | → nothing | Helper. Raises `InvalidAmountError` if the amount is 0 or less. |

**The leading underscore** (`_find_by_id`) is a Python convention meaning "internal, don't call this from outside the class." The CLI should never need these helpers.

**Watch out for `_next_id`:** don't use `len(expenses) + 1`. If you have IDs 1, 2, 3 and delete 2, the length is 2, so the next ID would be 3, which is a duplicate. Using max + 1 gives 4.

**Why the tracker raises errors instead of printing them:** the tracker doesn't know a terminal exists. It reports a problem by raising an exception, and the CLI decides how to show it. If you added a web page later, the same tracker would work unchanged.

---

### 4.4 `CLI` — talking to the user (file: `cli.py`)

**Job:** turn what the user typed into method calls on the tracker, then print the results. No math and no file access.

| Attribute | Type | Meaning |
|---|---|---|
| `tracker` | `ExpenseTracker` | Passed in through the constructor |
| `parser` | `argparse.ArgumentParser` | Defines the commands (`add`, `list`, ...) and their flags (`--amount`, `--id`, ...). Build it in `__init__`. |

| Method | Input → Output | What it does |
|---|---|---|
| `run(argv=None)` | list of strings → nothing | Parses the arguments, calls the matching handler, and **catches the custom exceptions** to print a friendly message instead of a crash. |
| `_handle_add(args)` | parsed args → nothing | Calls `tracker.add_expense(...)` and prints `Expense added successfully (ID: 1)` |
| `_handle_update(args)` | → nothing | Calls `tracker.update_expense(...)`. Should complain if no field to change was given. |
| `_handle_delete(args)` | → nothing | Calls `tracker.delete_expense(...)` and prints the success message |
| `_handle_list(args)` | → nothing | Gets the list from the tracker and prints the table (ID, Date, Description, Amount) |
| `_handle_summary(args)` | → nothing | Calls `tracker.total(month)` and prints `Total expenses: $30` or `Total expenses for August: $20`. Rejects months outside 1–12. |

**Tip:** `argparse` "subparsers" are how you get `add`, `list`, etc. as separate commands, each with its own flags. Look them up in the Python docs.

---

### 4.5 Custom exceptions (file: `exceptions.py`)

| Class | Inherits from | Raised when |
|---|---|---|
| `ExpenseTrackerError` | `Exception` | Never raised directly. It's the parent of the two below. |
| `ExpenseNotFoundError` | `ExpenseTrackerError` | Update or delete is given an ID that doesn't exist |
| `InvalidAmountError` | `ExpenseTrackerError` | The amount is 0 or negative |

**This is your first use of inheritance.** Each class says "I am a kind of `ExpenseTrackerError`." The payoff is that the CLI can catch *every* app error with one `except ExpenseTrackerError` line, while each error still has a precise name that explains what went wrong. These classes can be almost empty; often the body is just `pass`.

(Non-numeric amounts like `"abc"` can be caught by `argparse` itself if you set `type=float` on the `--amount` flag.)

---

### 4.6 `main.py` — wiring it together

`main.py` builds the objects in order, from the bottom layer up, and hands each one to the next:

1. Create an `ExpenseRepository` with the file path.
2. Create an `ExpenseTracker`, giving it the repository.
3. Create a `CLI`, giving it the tracker.
4. Call the CLI's `run()`.

Put this inside an `if __name__ == "__main__":` block so it only runs when you execute `main.py` directly, not when another file imports it.

---

## 5. Build order (do one step at a time, test it, commit)

1. **`Expense`.** Create one in a scratch script, call `to_dict()`, then `from_dict()` on the result. Do you get the same data back?
2. **`ExpenseRepository`.** Save a list of two expenses, open `expenses.json` to look at it, then `load()` it back.
3. **`exceptions.py`.**
4. **`ExpenseTracker`.** Test add, then list, then delete, then total, then total by month.
5. **`CLI` + `main.py`.** Run the exact commands from the roadmap.sh page and compare the output.
6. **Commit after every working step** with a clear message, e.g. `git commit -m "Add Expense class with to_dict/from_dict"`.

**Later (optional features):**
- **Category filter:** already designed in (`category` attribute, `list_expenses(category)`). You just need a `--category` flag in the CLI.
- **Budget:** a `Budget` class that holds a limit per month. The tracker gives it the month's total, and it answers "over or not?" It doesn't read the file itself.
- **CSV export:** a `CsvExporter` class with an `export(expenses, path)` method. It's kept separate from the repository because exporting is a different job from storing.
- **Tests:** `pytest` tests for `ExpenseTracker`. These are easy to write because the tracker doesn't print or depend on the terminal.

---

## 6. OOP concepts used in this design

| Concept | Plain-English meaning | Where it shows up |
|---|---|---|
| **Class / object** | A class is a blueprint, and an object is one thing built from it | `Expense` is the blueprint, and each lunch or dinner is an object |
| **Encapsulation** | Keep data and the code that changes it together, and hide the internals | Only `ExpenseTracker` changes the `expenses` list. Helpers start with `_`. |
| **Abstraction** | Use something without knowing how it works inside | The tracker calls `repository.save()` without knowing it's JSON |
| **Composition ("has-a")** | An object is built from other objects | The tracker *has a* repository, and the CLI *has a* tracker |
| **Dependency injection** | Pass in the objects a class needs instead of creating them inside | `ExpenseTracker(repository)`. A test can pass in a fake repository. |
| **Inheritance ("is-a")** | A class reuses and specializes a parent class | `ExpenseNotFoundError` *is an* `ExpenseTrackerError` |
| **Single Responsibility** | Each class has one reason to change | Changing the storage format → only `ExpenseRepository` changes |

**Why so little inheritance?** Beginners often expect inheritance everywhere, but in real code **composition is used far more often**. Use inheritance only when the "is-a" sentence is truly correct. An `ExpenseTracker` *is not* a kind of `ExpenseRepository`; it *uses* one. A future upgrade where inheritance would fit: a `BaseRepository` parent with `JsonRepository` and `CsvRepository` children. The tracker could then use either one without changing, which is called **polymorphism**.

---

## 7. Why the system is designed this way

Each class has one job, so a change in one place (the storage format, the output text, a business rule) stays in one file instead of spreading everywhere. Dependencies only point downward (CLI → Tracker → Repository/Expense), so the core logic never depends on the terminal or the file format. That makes the logic easy to test, reuse and replace. Totals are always calculated rather than stored, so the data has a single source of truth and can never get out of sync.
