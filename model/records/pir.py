from abc import ABC, abstractmethod
from typing import Any

class PIR(ABC):

    RECORD_TYPE = "pir"

    FIELDS: set[str] = set()

    def __init__(self, record_id: int):
        if type(record_id) is not int or record_id <= 0:
            raise ValueError("Record ID must be positive interger")
        
        self._id = record_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> str:
        return self.RECORD_TYPE

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    def _base_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type
        }

    @classmethod
    def validate_fields(
        cls,
        fields: dict
    ) -> None:

        provided_fields = set(fields)
        invalid_fields = provided_fields - cls.FIELDS
        missing_fields = cls.FIELDS - provided_fields

        if invalid_fields:
            raise ValueError(
                f"Invalid fields for {cls.RECORD_TYPE}: "
                f"{sorted(invalid_fields)}"
            )
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields for {cls.RECORD_TYPE}: "
                f"{sorted(missing_fields)}"
            )

    def __repr__(self):
        return f"{type(self).__name__}({self.to_dict()})"