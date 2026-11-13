from datetime import datetime
from unittest import TestCase

from model.records import Contact, Event, Note, PIR, Task


class RecordTests(TestCase):
    def test_record_serialization(self):
        """Each PIR serializes its type, ID, and fields."""
        start = datetime(2026, 11, 15, 14)
        alarm = datetime(2026, 11, 15, 13, 30)
        cases = [
            (Note(1, "Study\nPython"), {"id": 1, "type": "note", "text": "Study\nPython"}),
            (Task(2, "Submit", start), {
                "id": 2, "type": "task", "description": "Submit",
                "deadline": "2026-11-15T14:00:00",
            }),
            (Event(3, "Meeting", start, alarm), {
                "id": 3, "type": "event", "description": "Meeting",
                "start": "2026-11-15T14:00:00", "alarm": "2026-11-15T13:30:00",
            }),
            (Contact(4, "Alice", "Hong Kong", "01234567"), {
                "id": 4, "type": "contact", "name": "Alice",
                "address": "Hong Kong", "mobile": "01234567",
            }),
        ]
        for record, expected in cases:
            with self.subTest(record_type=expected["type"]):
                self.assertIsInstance(record, PIR)
                self.assertEqual(record.to_dict(), expected)

    def test_constructor(self):
        """PIR IDs must be positive integers."""
        for invalid_id in (0, -1, True, 1.0, "1"):
            with self.subTest(record_id=invalid_id):
                with self.assertRaises(ValueError):
                    Note(invalid_id, "Text")

    def test_repr(self):
        """A record's representation."""
        self.assertEqual(repr(Note(1, "Text")), "Note({'id': 1, 'type': 'note', 'text': 'Text'})")

    def test_task_field(self):
        """Task field accepts the exact schema and rejects mismatches."""
        fields = {"description": "Submit", "deadline": datetime(2026, 11, 20)}
        self.assertIsNone(Task.validate_fields(fields))
        with self.assertRaisesRegex(ValueError, "Missing required fields"):
            Task.validate_fields({"description": "Submit"})
        with self.assertRaisesRegex(ValueError, "Invalid fields"):
            Task.validate_fields({**fields, "text": "Extra"})
