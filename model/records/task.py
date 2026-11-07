from datetime import datetime
from .pir import PIR

class Task(PIR):

    RECORD_TYPE = "task"

    FIELDS = {"description", "deadline"}

    def __init__(
        self, 
        record_id: int, 
        description: str,
        deadline: datetime
    ):
        super().__init__(record_id)
        self.description = description
        self.deadline = deadline

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "description": self.description,
            "deadline": self.deadline.isoformat()
        } 