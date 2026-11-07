from .pir import PIR

class Note(PIR):
    RECORD_TYPE = "note"

    def __init__(
        self, 
        record_id: int, 
        text: str
    ):
        super().__init__(record_id)
        self.text = text

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "text": self.text
        }