from ics import generate_ics_file
from structs import Course, Schedule

# TODO: multiple instructors test case


def test_generate_ics_tuesday_thursday():
    """Test that Tuesday/Thursday classes generate events for both days"""
    course = Course(
        id=1,
        name="Test Course",
        number=241,
        location="Test Room",
        schedule=Schedule(
            start_time="11:00am",
            end_time="12:29pm",
            days="TTh",  # Tuesday and Thursday
        ),
        instructor=["Test Instructor"],
    )

    semester_start = "2025-01-21"  # This is a Tuesday
    semester_end = "2025-01-23"    # This is a Thursday

    ics_content = generate_ics_file([course], semester_start, semester_end)

    # Should have events for both Tuesday (21st) and Thursday (23rd)
    assert "20250121T110000" in ics_content  # Tuesday event
    assert "20250123T110000" in ics_content  # Thursday event
    
    # Count the number of events (should be 2)
    event_count = ics_content.count("BEGIN:VEVENT")
    assert event_count == 2, f"Expected 2 events for TTh, got {event_count}"


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
