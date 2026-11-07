from datetime import datetime
from .pir import PIR

class Event(PIR):
    RECORD_TYPE = "event"

    def __init__(
        self, 
        record_id: int, 
        description: str, 
        start: datetime, 
        alarm: datetime
    ):
        super().__init__(record_id)
        self.description = description
        self.start = start
        self.alarm = alarm

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "description": self.description,
            "start": self.start.isoformat(),
            "alarm": self.alarm.isoformat()
        }