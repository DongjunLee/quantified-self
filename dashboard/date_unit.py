from enum import Enum


class DateUnit(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class TaskGroup(Enum):
    TIME = "time"
    TASK_NAME = "task_name"
