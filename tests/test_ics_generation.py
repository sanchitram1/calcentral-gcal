from ics import generate_ics_file
from structs import Course, Schedule

# TODO: multiple instructors test case


def test_generate_ics():
    # Minimal course fixture as a dict (adjust if Course class is required)
    course = Course(
        id=1,
        name="Test Course",
        number=101,
        location="Test Room",
        schedule=Schedule(
            start_time="10:00am",
            end_time="11:00am",
            days="M",
        ),
        instructor=["Jane Doe"],
    )

    semester_start = "2025-09-01"
    semester_end = "2025-09-08"  # One week for simplicity

    ics_content = generate_ics_file([course], semester_start, semester_end)

    # Assert non-empty string
    assert isinstance(ics_content, str)
    assert len(ics_content) > 0

    # Assert ICS structure
    assert "BEGIN:VCALENDAR" in ics_content
    assert "END:VCALENDAR" in ics_content
    assert "BEGIN:VEVENT" in ics_content
    assert "END:VEVENT" in ics_content
    assert "SUMMARY:Test Course - 101" in ics_content
    assert "LOCATION:Test Room" in ics_content
    assert "DESCRIPTION:Instructor: Jane Doe\\nCourse: 101" in ics_content
    assert "DTSTART:" in ics_content
    assert "DTEND:" in ics_content

    # Optionally, check number of lines (should be > minimal ICS header/footer)
    lines = ics_content.splitlines()
    assert len(lines) > 10
