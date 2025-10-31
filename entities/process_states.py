from enum import Enum, auto

class ProcessState(Enum):
    """Estados possíveis de um processo no sistema"""
    CREATED = auto()
    IN_QUEUE = auto()
    IN_TRANSIT = auto()
    WAITING_CPU = auto()
    PROCESSING = auto()
    COMPLETED = auto()