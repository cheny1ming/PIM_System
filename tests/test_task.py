from datetime import datetime
from model import PIMManager
from model.storage import save_records, load_records

def test():
    manager = PIMManager()

    manager.add_record("note", text="Study Python")
    manager.add_record(
        "task",
        description="Finish COMP3211 project",
        deadline=datetime(2026, 11, 20),
    )
    manager.add_record(
        "event",
        description="Project meeting",
        start=datetime(2026, 11, 15, 14, 0),
        alarm=datetime(2026, 11, 15, 13, 30),
    )
    manager.add_record(
        "contact",
        name="Alice",
        address="Hong Kong",
        mobile="12345678",
    )

    manager.update(2, description="Hello", deadline=datetime(2026, 11, 10))
    manager.delete(3)

    manager.print_records()

    save_records(manager._records, "my_records.pim")
    
    records = load_records("my_records.pim")

    for record in records.values():
        print(record)

if __name__ == "__main__":
    test()
