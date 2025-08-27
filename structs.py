from dataclasses import dataclass, field


@dataclass
class Schedule:
    start_time: str = ""  # 11:00a
    end_time: str = ""  # 12:30p
    days: str = ""  # MTWThF OR MTWRF


@dataclass
class Course:
    id: int = 0
    name: str = field(default_factory=str)
    number: int = 0
    location: str = field(default_factory=str)
    schedule: Schedule = field(default_factory=Schedule)
    instructor: str = field(default_factory=list)
