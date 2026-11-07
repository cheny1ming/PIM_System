import json
from datetime import datetime
from pathlib import Path

from .records import PIR
from .pim_manager import PIMManager


def save_records(
    records: dict[int, PIR], 
    filename: str | Path = "records.pim"
) -> Path:
    path = Path(filename)
    if path.suffix != ".pim":
        path = path.with_suffix(".pim")

    data = [record.to_dict() for record in records.values()]
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(json_data, encoding="utf-8")
    return path

def load_records(filename: str | Path) -> dict[int, PIR]:
    path = Path(filename)
    if path.suffix != ".pim":
        path = path.with_suffix(".pim")

    data = json.loads(path.read_text(encoding="utf-8"))
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
