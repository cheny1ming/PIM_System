# PIM System

A command-line personal information manager for notes, tasks, events, and contacts. You can add, edit, list, delete, and search records, then save them to a `.pim` file.

## Getting started

Use Python 3.10 or later. The project uses only the Python standard library.

From the project root, run:

```bash
python main.py
```

Enter commands at the `pim>` prompt. Type `help` for the in-app manual.

```text
add note text="Lecture notes"
add task description="Finish assignment" deadline="2026-11-20 20:00"
add event description="Group meeting" start="2026-11-01 14:00" alarm="2026-11-01 13:45"
add contact name="Alex Chan" address="Hong Kong" mobile="91234567"
list
update 2 description="Finish project and video"
show 2
save "my records.pim"
quit
```

Quote values and filenames containing spaces. Enter dates and times in local time as `YYYY-MM-DD HH:MM`.

## Command reference

| Command | Description |
| --- | --- |
| `add TYPE field=value ...` | Create a `note`, `task`, `event`, or `contact`. |
| `update ID field=value ...` | Change the specified fields of a record. |
| `show ID` | Display one record. |
| `list` | Display all records. |
| `delete ID` | Delete a record and renumber subsequent records. |
| `find EXPRESSION` | Search using an expression. |
| `criteria NAME EXPRESSION` | Define or replace a named search criterion. |
| `search NAME` | Run a named criterion. |
| `save FILENAME` | Save all records to a `.pim` file, overwriting an existing file at that path. |
| `load FILENAME` | Replace the current records with the file contents and display them. |
| `help` | Show command descriptions and examples. |
| `quit` | Exit. Use `save` first to keep your changes. |

## Searching

```text
find type = task && deadline < "2026-11-20 20:00"
find (text contains "Lecture" || name contains "Alex") && !(type = event)
criteria urgent type = task && deadline < "2026-11-20 20:00"
search urgent
```

- `type` supports `=` with `note`, `task`, `event`, or `contact`.
- Text fields (`text`, `description`, `name`, `address`, and `mobile`) support case-sensitive `contains`.
- Time fields (`deadline`, `start`, and `alarm`) support `<`, `>`, and `=`.
- Operators are evaluated in the order `!`, `&&`, then `||`. Use parentheses to group conditions. A comparison against an absent field is false, and `!` negates that result.

## Saving and loading

Use `save` explicitly before quitting. Files use the same record layout as `list`, with a blank line between records.

```text
[1] NOTE
  text: Lecture notes

[2] TASK
  description: Finish project and video
  deadline: 2026-11-20 20:00
```

Use `load "my records.pim"` to reopen a file. Loading replaces the in-memory records. Older `.pim` files containing JSON arrays can also be loaded. Named criteria are available for the current session and are not saved in `.pim` files.

## Project structure

- `main.py` handles interactive commands and parses search expressions.
- `model/records/` defines the four record types.
- `model/pim_manager.py` manages records and formats them for display.
- `model/search.py` evaluates search criteria.
- `model/storage.py` reads and writes `.pim` files.
- `tests/` contains unit tests for records, the manager, search, and storage.

## Running tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```
