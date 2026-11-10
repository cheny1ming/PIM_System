import json
import re
from datetime import datetime
from pathlib import Path

from .records import PIR
from .pim_manager import PIMManager, format_record


def save_records(
    records: dict[int, PIR], 
    filename: str | Path = "records.pim"
) -> Path:
    path = Path(filename)
    if path.suffix != ".pim":
        path = path.with_suffix(".pim")

    content = "\n".join(format_record(record) + "\n" for record in records.values())
    path.write_text(content, encoding="utf-8")
    return path


def _parse_text_records(content: str) -> list[dict]:
    items = []
    item = None
    field = None
    for line_number, line in enumerate(content.split("\n"), start=1):
        if not line:
            continue
        header = re.fullmatch(r"\[([0-9]+)\] ([A-Z]+)", line)
        if header:
            item = {"id": int(header[1]), "type": header[2].lower()}
            items.append(item)
            field = None
        elif item is not None and field is not None and line.startswith("    "):
            item[field] += "\n" + line[4:]
        else:
            entry = re.fullmatch(r"  ([a-z_]+): (.*)", line)
            if item is None or entry is None or entry[1] in item:
                raise ValueError(f"Invalid PIM format on line {line_number}")
            field = entry[1]
            item[field] = entry[2]
    return items


def load_records(filename: str | Path) -> dict[int, PIR]:
    path = Path(filename)
    if path.suffix != ".pim":
        path = path.with_suffix(".pim")

    content = path.read_text(encoding="utf-8")
    if re.match(r"\s*\[\s*(?:\{|\])", content):
        data = json.loads(content)  # Existing .pim files used a JSON array.
    else:
        data = _parse_text_records(content)
    if not isinstance(data, list):
        raise ValueError("PIM file must contain a list of records")

    records = {}
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each record must be a JSON object")

        record_id = item.get("id")
        record_type = item.get("type")
        if type(record_id) is not int or record_id <= 0:
            raise ValueError("Record ID must be a positive integer")
        if record_id in records:
            raise ValueError(f"Duplicate record ID: {record_id}")
        if not isinstance(record_type, str) or record_type not in PIMManager.TYPES:
            raise ValueError(f"Unsupported record type: {record_type}")

        fields = {key: value for key, value in item.items() if key not in {"id", "type"}}
        if set(fields) != PIMManager.FIELDS[record_type]:
            raise ValueError(f"Invalid or missing fields for {record_type}")

        time_fields = {
            "task": ("deadline",),
            "event": ("start", "alarm"),
        }
        for field in time_fields.get(record_type, ()):
            if not isinstance(fields[field], str):
                raise ValueError(f"{field} must be an ISO datetime string")
            fields[field] = datetime.fromisoformat(fields[field])

        record_class = PIMManager.TYPES[record_type]
        records[record_id] = record_class(record_id=record_id, **fields)

    return records
