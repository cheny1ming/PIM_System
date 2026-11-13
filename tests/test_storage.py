import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from model.records import Contact, Event, Note, Task
from model.storage import load_records, save_records


class StorageTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "records.pim"

    def test_save_pim(self):
        """Test .pim file saving"""
        path = save_records({3: Note(3, "Café\nSecond line")}, self.path.with_suffix(".txt"))
        self.assertEqual(path, self.path)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         "[3] NOTE\n  text: Café\n    Second line\n")

    def test_load_pim(self):
        """Test load function."""
        self.path.write_text(
            "[3] NOTE\n  text: First\n    Second\n\n"
            "[5] TASK\n  description: Submit\n  deadline: 2026-11-20 09:00\n\n"
            "[7] EVENT\n  description: Meet\n  start: 2026-11-15 14:00\n"
            "  alarm: 2026-11-15 13:30\n\n"
            "[9] CONTACT\n  name: Alice\n  address: Hong Kong\n  mobile: 0123\n",
            encoding="utf-8",
        )
        expected = [
            Note(3, "First\nSecond"),
            Task(5, "Submit", datetime(2026, 11, 20, 9)),
            Event(7, "Meet", datetime(2026, 11, 15, 14), datetime(2026, 11, 15, 13, 30)),
            Contact(9, "Alice", "Hong Kong", "0123"),
        ]
        records = load_records(str(self.path.with_suffix("")))
        self.assertEqual(list(records), [3, 5, 7, 9])
        for record in expected:
            with self.subTest(record_id=record.id):
                loaded = records[record.id]
                self.assertIs(type(loaded), type(record))
                self.assertEqual(loaded.to_dict(), record.to_dict())

    def test_load_json(self):
        """Test json files."""
        data = [{"id": 4, "type": "task", "description": "Submit",
                 "deadline": "2026-11-20T09:00:12"}]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        record = load_records(self.path)[4]
        self.assertIsInstance(record, Task)
        self.assertEqual(record.to_dict(), data[0])

    def test_load_error(self):
        """Loading rejects duplicate IDs, bad IDs, schemas, types, and dates."""
        note = {"id": 1, "type": "note", "text": "First"}
        task = {"id": 1, "type": "task", "description": "Submit"}
        cases = [
            ([note, note], "Duplicate record ID"),
            ([note, 7], "Each record must be a JSON object"),
            ([{**note, "id": True}], "Record ID must be a positive integer"),
            ([{**note, "type": "memo"}], "Unsupported record type"),
            ([{"id": 1, "type": "note"}], "Invalid or missing fields"),
            ([{**task, "deadline": 123}], "ISO datetime string"),
            ([{**task, "deadline": "2026-02-30"}], "day is out of range"),
        ]
        for data, message in cases:
            with self.subTest(data=data):
                self.path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    load_records(self.path)

    def test_load_missing_file(self):
        """Loading a nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            load_records(self.path)
