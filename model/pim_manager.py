from datetime import datetime
from .records import *

class PIMManager:
    TYPES = {
        "note": Note,
        "task": Task,
        "event": Event,
        "contact": Contact
    }

    FIELDS = {
        "note": {"text"},
        "task": {"description", "deadline"},
        "event": {"description", "start", "alarm"},
        "contact": {"name", "address", "mobile"}
    }

    def __init__(self):
        self._records = {}
        self._next_id = 1

    def add_record(
        self,
        record_type: str,
        **fields
    ):
        # Check type of record
        if not isinstance(record_type, str) or record_type not in self.TYPES:
            raise ValueError(
                f"Unsupported record type: {record_type}"
            )

        required_fields = self.FIELDS[record_type]
        invalid_fields = set(fields) - required_fields
        missing_fields = required_fields - set(fields)
        if invalid_fields:
            raise ValueError(
                f"Invalid fields for {record_type}: {sorted(invalid_fields)}"
            )
        if missing_fields:
            raise ValueError(
                f"Missing required fields for {record_type}: {sorted(missing_fields)}"
            )

        record_class = self.TYPES[record_type]

        record = record_class(
            record_id=self._next_id,
            **fields
        )

        self._records[record.id] = record
        self._next_id += 1

        return record

    # def add_task(
    #     self,
    #     description: str,
    #     deadline: datetime
    # ) -> Task:
    #     task = Task(
    #         record_id=self._next_id,
    #         description=description,
    #         deadline=deadline
    #     )

    #     self._records[task.id] = task
    #     self._next_id += 1

    #     return task

    # def add_note(
    #     self,
    #     text: str
    # ) -> Note:
    #     note = Note(
    #         record_id=self._next_id,
    #         text=text
    #     )

    #     self._records[note.id] = note
    #     self._next_id += 1

    #     return note

    # def add_event(
    #     self,
    #     description: str,
    #     start: datetime,
    #     alarm: datetime
    # ) -> Event:
    #     event = Event(
    #         record_id=self._next_id,
    #         description=description,
    #         start=start,
    #         alarm=alarm
    #     )

    #     self._records[event.id] = event
    #     self._next_id += 1

    #     return event

    # def add_contact(
    #     self,
    #     name: str,
    #     address: str,
    #     mobile: str
    # ) -> Contact:
    #     contact = Contact(
    #         record_id=self._next_id,
    #         name=name,
    #         address=address,
    #         mobile=mobile
    #     )

    #     self._records[contact.id] = contact
    #     self._next_id += 1

    #     return contact

    def get_records(self, record_id: int):
        return self._records.get(record_id)

    def update(
        self, 
        record_id: int, 
        **fields
    ):
        if type(record_id) is not int or record_id <= 0:
            raise ValueError("Record ID must be a positive integer")

        record = self.get_records(record_id)
        if record is None:
            raise ValueError(f"Record not found: {record_id}")

        invalid_fields = set(fields) - self.FIELDS[record.type]
        if invalid_fields:
            raise ValueError(
                f"Invalid fields for {record.type}: {sorted(invalid_fields)}"
            )

        for name, value in fields.items():
            setattr(record, name, value)

        return record
