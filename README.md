# Expense-Tracker
Expense Tracker project challenge - provided by roadMap.sh
A simple command-line application written in Python for tracking personal expenses.  
The tool lets you add, update, delete, list, and summarize expenses stored in a local data file.



Features

Core

•  Run from the command line as expense-tracker
•  Add a new expense:
◦  Description
◦  Amount
◦  Auto-assigned ID
◦  Auto-set date (current date)
•  Update an existing expense (description, amount, category)
•  Delete an expense by ID
•  View all expenses in a table
•  View a summary of all expenses (total amount)
•  View a summary of expenses for a specific month of the current year

Optional / Extended

•  Categories
◦  Add a category to each expense (e.g., Food, Transport)
◦  Filter listed expenses by category
•  Monthly budgets
◦  Set a monthly budget (e.g., for August)
◦  Show current spending vs. budget
◦  Show a warning when spending exceeds the budget
•  CSV export
◦  Export all expenses to a CSV file for use in spreadsheets or backups



Installation & Setup

Prerequisites

•  Python 3.11+ installed and available on your PATH

Clone the repository
bash
Create and activate a virtual environment (recommended)
bash
Install dependencies

(Once you add a requirements.txt or pyproject.toml)
bash


Running the Application

During development, you can run the CLI via the module entry point:
bash
If you later package the project and configure a console script entry point (e.g., via setuptools), you’ll be able to run:
bash


Command Overview

General structure:
bash
Planned commands:

•  add – Add a new expense
•  update – Update an existing expense
•  delete – Delete an expense by ID
•  list – List all expenses (with optional filters)
•  summary – Show total expenses (overall or by month)
•  budget – Set/show monthly budgets (optional feature)
•  export – Export expenses to CSV (optional feature)



Usage Examples
bash


Commands in Detail

add

Add a new expense.
bash
•  Required:
◦  --description – Short text describing the expense
◦  --amount – Positive number (e.g., 20, 15.50)
•  Optional:
◦  --category – Category label (e.g., Food, Transport)

update

Update an existing expense by ID.
bash
•  At least one of --description, --amount, or --category must be provided.

delete

Delete an expense by ID.
bash
list

List all expenses, optionally filtered by category.
bash
Example output:
text
summary

Show total expenses overall or for a specific month (current year).
bash
Examples:
bash
budget (optional)

Manage monthly budgets.
bash
Example:
bash
export (optional)

Export all expenses to a CSV file.
bash


Data Storage

The application uses a simple local file, so no database is required.

•  Default file (example): expenses.json
•  Format: JSON list of expense objects, for example:
json
Monthly budgets can be stored in the same file or in a separate file such as budgets.json.



Implementation Notes

•  Language: Python 3.11+
•  Recommended standard libraries:
◦  argparse (or click) for command-line parsing
◦  json for persistence
◦  datetime for dates and month-based summaries
◦  csv for exports

Suggested structure:
text


Error Handling

The application should handle common errors with clear messages:

•  Negative or zero amounts
•  Non-numeric amounts
•  Missing required arguments (e.g., no description or amount on add)
•  Non-existent expense IDs on update / delete
•  Invalid month values (--month must be 1–12)
•  Missing/corrupted data files (start from an empty state or show a helpful error)



Testing

Once tests are added (e.g., with pytest):
bash
Tests should cover:

•  Adding, updating, deleting expenses
•  Listing and summarizing expenses
•  Month-specific summaries
•  Category filtering
•  Budget warnings
•  CSV export behavior



Roadmap

•  Implement core CLI (add, list, delete, summary)
•  Add month-specific summary for the current year
•  Add categories and category-based filtering
•  Implement monthly budgets and warnings
•  Add CSV export
•  Add automated tests and continuous integration
•  Improve CLI output formatting (alignment, colors)
