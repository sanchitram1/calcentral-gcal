import re
from dataclasses import dataclass, field


@dataclass
class Course:
    id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    number: int = field(default_factory=int)
    location: str = field(default_factory=str)
    schedule: dict[str, str] = field(default_factory=dict)  # mapping from day to time
    instructor: str = field(default_factory=list)


def parse_class_schedule(text_blob: str) -> list[Course]:
    """
    Parses a raw text blob of a course schedule to extract structured information
    for each enrolled course.

    Args:
        text_blob (str): The string containing the schedule information.

    Returns:
        list: A list of dictionaries, where each dictionary represents a course
              with its name, number, location, schedule, and instructors.
    """
    # split the text by "Enrolled" to isolate each class entry
    class_chunks = text_blob.split("Enrolled")[1:]

    extracted_classes = []

    for chunk in class_chunks:
        # define regex patterns to find the required information
        # class number, subject, and course number
        class_info_pattern = re.compile(r"^\s*(\d+)\s+([A-Za-z\s&]+?)\t+([\w\d]+)")

        # days, time, and location of the class.
        schedule_pattern = re.compile(
            r"([MWFThTu]+)\s+([\d:]+[ap]m\s+-\s+[\d:]+[ap]m)\s+-\s+(.+)"
        )

        # schedule, but in case location isn't defined!
        schedule_no_loc_pattern = re.compile(
            r"([MWFThTu]+)\s+([\d:]+[ap]m\s+-\s+[\d:]+[ap]m)"
        )

        # instructor names
        instructor_pattern = re.compile(r"^[A-Z][a-z]+\s[A-Z][a-z]+$")

        # create the object representing our course
        course: Course = Course()

        # process each chunk line by line for clarity and simplicity.
        lines = chunk.strip().split("\n")

        # now, the first line contains our class info, so we'll check that before
        # iterating
        if lines:
            class_info_match = class_info_pattern.match(lines[0])
            if class_info_match:
                id, subject, number = class_info_match.groups()
                course.id = id
                course.number = number.strip()
                course.name = f"{subject.strip()}"

        # now iterate through everything to populate location and instructors
        for line in lines:
            line = line.strip()

            # Check for schedule with location
            schedule_match = schedule_pattern.search(line)
            if schedule_match:
                days, time, location = schedule_match.groups()
                course.schedule = {"Days": days.strip(), "Time": time.strip()}
                course.location = location.strip()
                continue  # Move to the next line once schedule is found

            # Check for schedule without location
            schedule_no_loc_match = schedule_no_loc_pattern.search(line)
            if schedule_no_loc_match:
                days, time = schedule_no_loc_match.groups()
                course.schedule = {"Days": days.strip(), "Time": time.strip()}
                continue

            # Check for instructor names
            instructor_match = instructor_pattern.match(line)
            if instructor_match:
                course.instructor.append(line)

        extracted_classes.append(course)

    return extracted_classes
