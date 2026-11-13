from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from unittest import TestCase

from model import PIMManager
from model.records import Contact, Event, Note, Task


class PIMManagerTests(TestCase):
    def setUp(self):
        self.manager = PIMManager()

    def test_add(self):
        """Adding each supported type assigns the next_id and stores the object."""
        now = datetime(2026, 11, 15)
        cases = [
            ("note", Note, {"text": "Study"}),
            ("task", Task, {"description": "Submit", "deadline": now}),
            ("event", Event, {"description": "Meet", "start": now, "alarm": now}),
            ("contact", Contact, {"name": "Alice", "address": "HK", "mobile": "0123"}),
        ]
        for expected_id, (kind, cls, fields) in enumerate(cases, 1):
            with self.subTest(kind=kind):
                record = self.manager.add_record(kind, **fields)
                self.assertIsInstance(record, cls)
                self.assertEqual(record.id, expected_id)
                self.assertIs(self.manager.get_records(expected_id), record)
                for name, value in fields.items():
                    self.assertEqual(getattr(record, name), value)

    def test_add_error(self):
        """Add will reject unsupported elements."""
        cases = [
            ("memo", {}, "Unsupported record type"),
            (None, {}, "Unsupported record type"),
            ("note", {}, "Missing required fields"),
            ("note", {"text": "Study", "name": "Alice"}, "Invalid fields"),
        ]
        for kind, fields, message in cases:
            with self.subTest(kind=kind, fields=fields):
                with self.assertRaisesRegex(ValueError, message):
                    self.manager.add_record(kind, **fields)
        self.assertIsNone(self.manager.get_records(1))
        self.assertEqual(self.manager.add_record("note", text="Study").id, 1)

    def test_update(self):
        """Updating a task description keeps its ID and deadline."""
        deadline = datetime(2026, 11, 20)
        record = self.manager.add_record("task", description="Draft", deadline=deadline)
        self.assertIs(self.manager.update(record.id, description="Submit"), record)
        self.assertEqual(record.id, 1)
        self.assertEqual(record.description, "Submit")
        self.assertEqual(record.deadline, deadline)

    def test_update_error(self):
        """An invalid update."""
        record = self.manager.add_record("note", text="Original")
        with self.assertRaisesRegex(ValueError, "Invalid fields"):
            self.manager.update(record.id, text="Changed", name="Alice")
        self.assertEqual(record.text, "Original")

    def test_delete(self):
        """Deleting the middle record should keep ids in order."""
        first = self.manager.add_record("note", text="First")
        second = self.manager.add_record("note", text="Second")
        third = self.manager.add_record("note", text="Third")

        self.assertIs(self.manager.delete(2), second)
        self.assertIs(self.manager.get_records(1), first)
        self.assertIs(self.manager.get_records(2), third)
        self.assertEqual(third.id, 2)
        self.assertIsNone(self.manager.get_records(3))
        self.assertEqual(self.manager.add_record("note", text="New").id, 3)

    def test_print(self):
        """Printing handles an empty manager and formats selected or all records."""
        output = StringIO()
        with redirect_stdout(output):
            self.manager.print_records()
        self.assertEqual(output.getvalue(), "No records found.\n")

        self.manager.add_record("note", text="First\nSecond")
        self.manager.add_record("task", description="Submit", deadline=datetime(2026, 11, 20, 9))
        note = "[1] NOTE\n  text: First\n    Second\n"
        task = "[2] TASK\n  description: Submit\n  deadline: 2026-11-20 09:00\n"
        for record_id, expected in ((2, task), (None, note + task)):
            with self.subTest(record_id=record_id):
                output = StringIO()
                with redirect_stdout(output):
                    self.manager.print_records(record_id)
                self.assertEqual(output.getvalue(), expected)
