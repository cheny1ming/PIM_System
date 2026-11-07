from datetime import datetime
from model import PIMManager


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

    for record_id in range(1, 5):
        print(manager.get_records(record_id))


if __name__ == "__main__":
    test()
