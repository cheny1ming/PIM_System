import re
import shlex
from datetime import datetime

from model import PIMManager
from model.search import TIME_FIELDS, search_records
from model.storage import load_records, save_records


HELP = """Commands:
  add TYPE field=value ...        Create a note, task, event, or contact.
  update ID field=value ...       Modify selected fields of an existing PIR.
  show ID                         Print detailed information about one PIR.
  list                            Print detailed information about all PIRs.
  delete ID                       Delete a PIR and renumber subsequent PIRs.
  find EXPRESSION                 Search PIRs using a condition expression.
  criteria NAME EXPRESSION        Define or replace a named search criterion.
  search NAME                     Search PIRs using a named criterion.
  save FILENAME                   Save all PIRs as JSON in a .pim file; overwrite if it exists.
  load FILENAME                   Replace current PIRs with those from a .pim file.
  help                            Display this user manual.
  quit                            Exit the system without automatically saving changes.

Add examples:
  add note text="Lecture notes"
  add task description="Finish assignment" deadline="2026-11-20 20:00"
  add event description="Group meeting" start="2026-11-01 14:00" alarm="2026-11-01 13:45"
  add contact name="Alex Chan" address="Hong Kong" mobile="91234567"

Update examples:
  update 1 text="Updated lecture notes"
  update 2 description="Finish project and video" deadline="2026-11-19 18:00"

Show and list examples:
  show 2
  list

Delete examples:
  delete 2

Search examples:
  find type = task && deadline < "2026-11-20 20:00"
  find (text contains "lecture" || name contains "Alex") && !(type = event)
  find start > "2026-11-01 14:00"
  find alarm = "2026-11-01 13:45"

Named criterion examples:
  criteria urgent type = task && deadline < "2026-11-20 20:00"
  search urgent

Save and load examples:
  save "my records.pim"
  load "my records.pim"

Help and quit examples:
  help
  quit

Usage notes:
  Quote values and filenames containing spaces.
  Fields: type, text, description, deadline, start, alarm, name, address, mobile.
  Text fields support contains; matching is case-sensitive.
  Type supports =; time fields support <, >, and =.
  Times use YYYY-MM-DD HH:MM (local time).
  Precedence: ! then && then ||; parentheses override precedence.
  A comparison on an absent field is false; ! negates that result.
  Changes must be saved explicitly. Named criteria are not stored in .pim files.
"""


def parse_time(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", value):
        raise ValueError("Times must use YYYY-MM-DD HH:MM")
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def parse_expression(expression):
    """Recursive descent: or -> and -> unary -> comparison."""
    tokens = []
    scanner = re.compile(r'''\s+|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|&&|\|\||[()!<>=]|[^\s()!<>=&|\"']+''')
    offset = 0
    while offset < len(expression):
        match = scanner.match(expression, offset)
        if match is None:
            raise ValueError(f"Invalid expression near: {expression[offset:]}")
        token = match.group()
        offset = match.end()
        if not token.isspace():
            tokens.append(shlex.split(token)[0] if token[0] in "\"'" else token)
    position = 0

    def take():
        nonlocal position
        if position >= len(tokens):
            raise ValueError("Incomplete search expression")
        token = tokens[position]
        position += 1
        return token

    def peek():
        return tokens[position] if position < len(tokens) else None

    def unary():
        if peek() == "!":
            take()
            return {"!": unary()}
        if peek() == "(":
            take()
            result = logical_or()
            if take() != ")":
                raise ValueError("Expected closing parenthesis")
            return result
        field, operator, value = take(), take(), take()
        if field == "type":
            if operator != "=":
                raise ValueError("Type comparisons require '='")
            return {"type": value}
        if field in TIME_FIELDS:
            value = parse_time(value)
        return {"field": field, "operator": operator, "value": value}

    def logical_and():
        result = unary()
        while peek() == "&&":
            take()
            result = {"&&": [result, unary()]}
        return result

    def logical_or():
        result = logical_and()
        while peek() == "||":
            take()
            result = {"||": [result, logical_and()]}
        return result

    result = logical_or()
    if position != len(tokens):
        raise ValueError(f"Unexpected token: {tokens[position]}")
    search_records({}, result)  # Validate every leaf before execution.
    return result


def parse_fields(arguments):
    if not arguments:
        raise ValueError("Provide at least one field=value")
    fields = {}
    for argument in arguments:
        field, separator, value = argument.partition("=")
        if not separator or not field:
            raise ValueError("Expected field=value; quote values containing spaces")
        if field in fields:
            raise ValueError(f"Duplicate field: {field}")
        fields[field] = parse_time(value) if field in TIME_FIELDS else value
    return fields


def display_results(manager, records):
    if not records:
        print("No records found.")
    for record_id in records:
        manager.print_records(record_id)


def execute_command(line, manager, criteria):
    """Execute one command; return False only for quit."""
    parts = line.strip().split(maxsplit=1)
    if not parts:
        return True
    command = parts[0]
    remainder = parts[1] if len(parts) == 2 else ""
    if command == "find":
        display_results(manager, search_records(manager._records, parse_expression(remainder)))
        return True
    if command == "criteria":
        # Read a possibly quoted name without stripping quotes from the expression.
        lexer = shlex.shlex(remainder, posix=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        name = lexer.get_token()
        expression = lexer.instream.read()
        if not name or not expression.strip():
            raise ValueError("Usage: criteria NAME EXPRESSION")
        criteria[name] = parse_expression(expression)
        print(f"Criterion saved: {name}")
        return True

    args = shlex.split(remainder)
    if command in {"help", "quit", "list"}:
        if args:
            raise ValueError(f"{command} takes no arguments")
        if command == "quit":
            return False
        if command == "help":
            print(HELP)
        else:
            manager.print_records()
    elif command == "add":
        if len(args) < 2:
            raise ValueError("Usage: add TYPE field=value ...")
        record = manager.add_record(args[0], **parse_fields(args[1:]))
        print(f"Added [{record.id}] {record.type.upper()}")
    elif command == "update":
        if len(args) < 2:
            raise ValueError("Usage: update ID field=value ...")
        record = manager.update(int(args[0]), **parse_fields(args[1:]))
        manager.print_records(record.id)
    elif command in {"show", "delete", "save", "load", "search"}:
        if len(args) != 1:
            raise ValueError(f"{command} requires exactly one argument")
        if command == "show":
            manager.print_records(int(args[0]))
        elif command == "delete":
            record = manager.delete(int(args[0]))
            print(f"Deleted [{record.id}]")
        elif command == "save":
            print(f"Saved to {save_records(manager._records, args[0])}")
        elif command == "load":
            records = load_records(args[0])
            # Normalize IDs to the contiguous numbering used by delete.
            records = dict(enumerate(records.values(), start=1))
            for record_id, record in records.items():
                record._id = record_id
            manager._records = records
            manager._next_id = len(records) + 1
            print(f"Loaded {len(records)} records.")
        else:
            if args[0] not in criteria:
                raise ValueError(f"Unknown criterion: {args[0]}")
            display_results(manager, search_records(manager._records, criteria[args[0]]))
    else:
        raise ValueError(f"Unknown command: {command}. Type help for usage.")
    return True


def main():
    manager = PIMManager()
    criteria = {}
    print("Welcome to the PIM system. Type help for usage.")
    while True:
        try:
            line = input("pim> ")
            if not execute_command(line, manager, criteria):
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
    print("Goodbye.")


if __name__ == "__main__":
    main()
