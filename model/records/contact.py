from .pir import PIR

class Contact(PIR):
    RECORD_TYPE = "contact"

    def __init__(
        self, 
        record_id: int, 
        name: str, 
        address: str, 
        mobile: str
    ):
        super().__init__(record_id)
        self.name = name
        self.address = address
        self.mobile = mobile

    def to_dict(self) -> dict:
        return {
            **self._base_dict(),
            "name": self.name,
            "address": self.address,
            "mobile": self.mobile
        }