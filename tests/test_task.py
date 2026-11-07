from datetime import datetime
from model.records import Task
from model import PIMManager

def test():
    task = Task(
        record_id=1,
        description="Finish COMP3211 project",
        deadline=datetime(2026, 11, 20)
    )

    p = PIMManager()
    p.add_task(
        description="Finish COMP3211 project",
        deadline=datetime(2026, 11, 20)
    )
    task1 = p.get_records(1)
    print(task1)


if __name__ == "__main__":
    test()