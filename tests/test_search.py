from datetime import datetime, timezone
from unittest import TestCase

from model.records import Contact, Event, Note, Task
from model.search import search_records


class SearchTests(TestCase):
    def setUp(self):
        self.day = datetime(2026, 11, 15, 10)
        self.records = {
            4: Note(4, "Project notes"),
            2: Task(2, "Project report", self.day),
            8: Event(8, "Meeting", datetime(2026, 11, 15, 11), self.day),
            1: Contact(1, "Alice", "Hong Kong", "01234567"),
        }

    def test_search_by_type(self):
        """Test search results with provided types."""
        for kind, record_id in (("note", 4), ("task", 2), ("event", 8), ("contact", 1)):
            with self.subTest(kind=kind):
                self.assertEqual(search_records(self.records, {"type": kind}),
                                 {record_id: self.records[record_id]})

    def test_contains(self):
        """Test the substring matching, contains."""
        cases = [
            ("text", "Project", [4]),
            ("description", "Project", [2]),
            ("name", "lic", [1]),
            ("address", "Kong", [1]),
            ("mobile", "012", [1]),
            ("text", "project", []),
        ]
        for field, value, expected_ids in cases:
            with self.subTest(field=field, value=value):
                criterion = {"field": field, "operator": "contains", "value": value}
                self.assertEqual(list(search_records(self.records, criterion)), expected_ids)

    def test_time_comparisons(self):
        """Comparisons in every time field."""
        for field, record_id, hour in (("deadline", 2, 10), ("start", 8, 11), ("alarm", 8, 10)):
            cases = [("<", hour + 1, [record_id]), (">", hour - 1, [record_id]),
                     ("=", hour, [record_id]), ("<", hour, []), (">", hour, []),
                     ("=", hour + 1, [])]
            for operator, comparison_hour, expected in cases:
                with self.subTest(field=field, operator=operator, hour=comparison_hour):
                    criterion = {"field": field, "operator": operator,
                                 "value": self.day.replace(hour=comparison_hour)}
                    self.assertEqual(list(search_records(self.records, criterion)), expected)

    def test_nested_logic(self):
        """AND, OR, and NOT combine predicates while preserving matching objects."""
        criterion = {"&&": [
            {"||": [{"type": "note"}, {"type": "task"}, {"type": "event"}]},
            {"!": {"type": "event"}},
        ]}
        result = search_records(self.records, criterion)
        self.assertEqual(list(result), [4, 2])
        self.assertIs(result[4], self.records[4])
        self.assertIs(result[2], self.records[2])
        self.assertEqual(list(self.records), [4, 2, 8, 1])
        self.assertEqual(search_records({}, criterion), {})

    def test_invalid_criteria(self):
        """If input invalid criteria, raise ValueError."""
        cases = [
            None, {}, {"type": "memo"}, {"type": []}, {"&&": []},
            {"||": {"type": "task"}}, {"!": None},
            {"&&": [{"type": "note"}, {"type": "memo"}]},
            {"field": 1, "operator": "contains", "value": "x"},
            {"field": "text", "operator": "=", "value": "x"},
            {"field": "text", "operator": "contains", "value": 1},
            {"field": "deadline", "operator": "=", "value": "2026-11-15"},
            {"field": "deadline", "operator": "contains", "value": self.day},
            {"field": "unknown", "operator": "contains", "value": "x"},
        ]
        for criterion in cases:
            with self.subTest(criterion=criterion):
                with self.assertRaises(ValueError):
                    search_records({}, criterion)