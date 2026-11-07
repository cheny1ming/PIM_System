"""
Search PIRs using nested dictionary criteria.

Examples:
    {"type": "task"}
    {"field": "description", "operator": "contains", "value": "project"}
    {"field": "deadline", "operator": "<", "value": datetime(2026, 11, 20)}
    {"&&": [criterion1, criterion2]}
    {"||": [criterion1, criterion2]}
    {"!": criterion}

Text matching is case-sensitive. Missing fields do not match.
Logical lists must contain at least one criterion. Criteria are validated
before searching, even when the record dictionary is empty.
"""

from datetime import datetime
from operator import eq, gt, lt

from .records import PIR


TEXT_FIELDS = {"text", "description", "name", "address", "mobile"}
TIME_FIELDS = {"deadline", "start", "alarm"}
RECORD_TYPES = {"note", "task", "event", "contact"}


def _compile_criterion(criterion):
    if not isinstance(criterion, dict):
        raise ValueError("A criterion must be a dictionary")

    if set(criterion) == {"type"}:
        kind = criterion["type"]
        if not isinstance(kind, str) or kind not in RECORD_TYPES:
            raise ValueError(f"Unsupported record type: {kind}")
        return lambda record: record.type == kind

    for connector in ("&&", "||", "!"):
        if set(criterion) == {connector}:
            children = criterion[connector]
            if connector == "!":
                child = _compile_criterion(children)
                return lambda record: not child(record)
            if not isinstance(children, list) or not children:
                raise ValueError(f"{connector} requires a non-empty list of criteria")
            predicates = [_compile_criterion(child) for child in children]
            if connector == "&&":
                return lambda record: all(predicate(record) for predicate in predicates)
            return lambda record: any(predicate(record) for predicate in predicates)

    if set(criterion) != {"field", "operator", "value"}:
        raise ValueError("Invalid criterion structure")

    field = criterion["field"]
    operator = criterion["operator"]
    value = criterion["value"]
    if not isinstance(field, str) or not isinstance(operator, str):
        raise ValueError("Field and operator must be strings")

    if field in TEXT_FIELDS:
        if operator != "contains" or not isinstance(value, str):
            raise ValueError("Text criteria require 'contains' and a string value")

        def contains(record):
            stored = getattr(record, field, None)
            return isinstance(stored, str) and value in stored

        return contains

    if field in TIME_FIELDS:
        comparisons = {"<": lt, ">": gt, "=": eq}
        if operator not in comparisons or not isinstance(value, datetime):
            raise ValueError("Time criteria require '<', '>', or '=' and a datetime value")
        compare = comparisons[operator]

        def compare_time(record):
            stored = getattr(record, field, None)
            if not isinstance(stored, datetime):
                return False
            if (stored.utcoffset() is None) != (value.utcoffset() is None):
                raise ValueError("Cannot compare timezone-aware and naive times")
            return compare(stored, value)

        return compare_time

    raise ValueError(f"Unsupported search field: {field}")


def search_records(records: dict[int, PIR], criterion: dict) -> dict[int, PIR]:
    """Return matching records, preserving their IDs, order, and objects."""
    matches = _compile_criterion(criterion)
    return {record_id: record for record_id, record in records.items() if matches(record)}
