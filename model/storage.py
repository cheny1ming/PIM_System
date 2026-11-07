import json
from pathlib import Path

from .records import PIR


def save_records(records: dict[int, PIR], filename: str | Path) -> Path:
    path = Path(filename)
    if path.suffix != ".pim":
        path = path.with_suffix(".pim")

    data = [record.to_dict() for record in records.values()]
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(json_data, encoding="utf-8")
    return path
