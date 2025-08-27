import uuid
from datetime import datetime, timedelta

from structs import Course

# Day name to weekday number mapping
DAY_TO_WEEKDAY = {
    "Monday": 0,
    "M": 0,
    "Tuesday": 1,
    "T": 1,
    "Wednesday": 2,
    "W": 2,
    "Thursday": 3,
    "Th": 3,
    "Friday": 4,
    "F": 4,
    "Saturday": 5,
    "Sa": 5,
    "Sunday": 6,
}


def handle_instructor(instructors: list[str]) -> str:
    return "\n".join(instructors)


def generate_ics_file(
    classes: list[Course], semester_start_str: str, semester_end_str: str
) -> str:
    """Generate ICS file content from parsed classes"""

    # Parse semester dates
    semester_start = datetime.strptime(semester_start_str, "%Y-%m-%d").date()
    semester_end = datetime.strptime(semester_end_str, "%Y-%m-%d").date()

    # ICS header
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//UC Berkeley Schedule//Schedule Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for cls in classes:
        instructor = handle_instructor(cls.instructor)
        for day in cls.schedule.days:
            if day not in DAY_TO_WEEKDAY:
                continue

            weekday = DAY_TO_WEEKDAY[day]

            # Find the first occurrence of this weekday in the semester
            current_date = semester_start
            while current_date.weekday() != weekday:
                current_date += timedelta(days=1)

            # Parse start and end times
            start_time_str = cls.schedule.start_time.replace(" ", "")
            end_time_str = cls.schedule.end_time.replace(" ", "")

            try:
                start_time = datetime.strptime(start_time_str, "%I:%M%p").time()
                end_time = datetime.strptime(end_time_str, "%I:%M%p").time()
            except Exception as e:
                # Try without minutes if parsing fails
                print(f"Error parsing time: {e}")
                try:
                    start_time = datetime.strptime(start_time_str, "%I%p").time()
                    end_time = datetime.strptime(end_time_str, "%I%p").time()
                except Exception as e:
                    raise e

            # Generate recurring events for each week of the semester
            event_date = current_date
            while event_date <= semester_end:
                start_datetime = datetime.combine(event_date, start_time)
                end_datetime = datetime.combine(event_date, end_time)

                # Format for ICS (UTC format)
                start_utc = start_datetime.strftime("%Y%m%dT%H%M%S")
                end_utc = end_datetime.strftime("%Y%m%dT%H%M%S")

                # Generate unique ID
                event_id = str(uuid.uuid4())

                # Create event
                ics_lines.extend(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{event_id}",
                        f"DTSTART:{start_utc}",
                        f"DTEND:{end_utc}",
                        f"SUMMARY:{cls.name} - {cls.number}",
                        f"LOCATION:{cls.location}",
                        f"DESCRIPTION:Instructor: {instructor}\\nCourse: {cls.number}",
                        "END:VEVENT",
                    ]
                )

                # Move to next week
                event_date += timedelta(days=7)

    # ICS footer
    ics_lines.append("END:VCALENDAR")

    return "\r\n".join(ics_lines)
