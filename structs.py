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
    instructor: list[str] = field(default_factory=list)
    
    def serialize(self) -> dict:
        """Serialize Course object to JSON-compatible dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "number": self.number,
            "location": self.location,
            "schedule": {
                "start_time": self.schedule.start_time,
                "end_time": self.schedule.end_time,
                "days": self.schedule.days,
            },
            "instructor": self.instructor,
        }
