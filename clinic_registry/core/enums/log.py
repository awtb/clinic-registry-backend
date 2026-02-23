from enum import StrEnum


class LogEntity(StrEnum):
    PATIENT = "PATIENT"
    USER = "USER"
    MEDICAL_RECORD = "MEDICAL_RECORD"


class LogAction(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
